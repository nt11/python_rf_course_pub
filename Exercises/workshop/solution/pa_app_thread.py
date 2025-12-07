from PyQt6.QtCore       import QThread, pyqtSignal
import numpy as np

class PaScan(QThread):
    # Define signals as class attributes (for progressbar and returned data)
    progress    = pyqtSignal(int)
    data        = pyqtSignal(np.ndarray, np.ndarray, bool, str, str) # freq, power, clf , legend, color
    csv         = pyqtSignal(np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray) # CSV file name
    log         = pyqtSignal(str)
    # LCD signals
    lcd_g      = pyqtSignal(float)
    lcd_op1dB  = pyqtSignal(float)
    lcd_oip3   = pyqtSignal(float)
    lcd_oip5   = pyqtSignal(float)
    lcd_p_out  = pyqtSignal(float) # Power out

    def __init__(self, f_scan,scpi_sa, scpi_sg, loss = 0):
        super().__init__()
        self.f_scan     = f_scan
        self.scpi_sa    = scpi_sa
        self.scpi_sg    = scpi_sg
        self.loss       = loss
        
        self.running    = False

    def run(self):
        # Save the instrument attributes for recall at the end of the scan
        self.running = True
        self.log.emit("Thread: Starting scan")

        # Set RF output on
        self.scpi_sg.write(":OUTPUT:STATE ON")
        self.scpi_sa.write("sense:DETEctor AVERage")
        # Trace Clear/write mode
        self.scpi_sa.write("TRACe:MODE WRITe")
        self.scpi_sa.write("INITiate:CONTinuous OFF")

        p_tx_nominal = float(self.scpi_sg.query("POW:LEV?"))

        # Create a list to store the scan data
        gain    = np.array([])
        op1dB   = np.array([])
        oip3    = np.array([])
        oip5    = np.array([])

        freq    = np.array([])
        for i, f in enumerate(self.f_scan):
            # Set the SG to the frequency of the current scan point and power level
            p_tx = p_tx_nominal - 10 # Check gain at low power
            self.scpi_sg.write(f"POW:LEV {p_tx}")
            self.scpi_sg.write(f"freq {f} MHz")

            # Set the SA center frequency
            self.scpi_sa.write(f"sense:FREQuency:CENTer {f} MHz")

            # Small signal gain
            self.scpi_sg.write(":OUTPUT:MOD:STATE OFF") # Modulation off
            self.scpi_sg.query(f"*OPC?")
            peak_value = self.sa_sweep_marker_max()

            # Set the reference level
            max_level  = np.ceil( peak_value/10 + 1)*10
            set_level  = float(self.scpi_sa.query(f"DISP:WIND:TRAC:Y:RLEV?") )
            if set_level != max_level:
                self.log.emit(f"Thread: Setting reference level to {max_level}")
                self.scpi_sa.write(f"DISP:WIND:TRAC:Y:RLEV {max_level}")
            # save the peak value and frequency
            small_signal_gain   = peak_value + self.loss - p_tx
            gain                = np.append(gain, small_signal_gain)
            freq                = np.append(freq, f)
            # Update the Gain LCD
            self.lcd_g.emit(small_signal_gain)
            self.lcd_p_out.emit(peak_value + self.loss)
            # OP1dB
            op1dB_i = self.find_op1db_binary_search(p_tx_nominal - 6, p_tx_nominal + 5, gain[-1])
            op1dB   = np.append(op1dB, op1dB_i)
            self.lcd_op1dB.emit(op1dB_i)

            # OIP3 and OIP5
            # Modulation On and tx power to nominal
            self.scpi_sg.write(":OUTPUT:MOD:STATE ON")
            self.scpi_sg.write(f"POW:LEV {p_tx_nominal}")
            subcarrier_power = self.sa_sweep_marker_max()
            p_i        = subcarrier_power + self.loss
            # Get the frequency of subcarrier 1
            freq_sig1  = float(self.scpi_sa.query("CALCulate:MARKer:X?"))
            # Next peak (subcarrier 2)
            self.scpi_sa.write("CALCulate:MARKer:MAXimum:NEXT")
            # Get the frequency of subcarrier 2
            freq_sig2  = float(self.scpi_sa.query("CALCulate:MARKer:X?"))
            f_sub_h = max(freq_sig1, freq_sig2)
            f_sub_l = min(freq_sig1, freq_sig2)
            # Set the marker to OIP3 (sub_h + (sub_h - sub_l))
            f_oip3 = f_sub_h + (f_sub_h - f_sub_l)
            self.scpi_sa.write(f"CALCulate:MARKer:X {f_oip3} Hz")
            # Get the peak value
            marker_y_value = float(self.scpi_sa.query("CALCulate:MARKer:Y?"))
            p_i3        = marker_y_value + self.loss
            # Next peak twice (OIP5)
            f_oip5 = f_sub_h + (f_sub_h - f_sub_l)*2
            self.scpi_sa.write(f"CALCulate:MARKer:X {f_oip5} Hz")
            # Get the peak value
            marker_y_value = float(self.scpi_sa.query("CALCulate:MARKer:Y?"))
            p_i5        = marker_y_value + self.loss

            oip3_i = p_i + (p_i - p_i3)/2
            oip5_i = p_i + (p_i - p_i5)/4
            oip3 = np.append(oip3, oip3_i)
            oip5 = np.append(oip5, oip5_i)
            self.lcd_oip3.emit(oip3_i)
            self.lcd_oip5.emit(oip5_i)

            self.data.emit(freq, gain , True , f"Gain" , 'k')
            self.data.emit(freq, op1dB, False, f"OP1dB", 'b')
            self.data.emit(freq, oip3 , False, f"OIP3" , 'g')
            self.data.emit(freq, oip5 , False, f"OIP5" , 'r')

            # Update the progress bar
            self.progress.emit(100 * (i + 1) // len(self.f_scan))
            if not self.running:
                break

        # Dump the data to a CSV file
        self.csv.emit(freq, gain, op1dB, oip3, oip5)

    def find_op1db_binary_search(self, p_tx_start, p_tx_end, small_signal_gain, resolution=0.1):
        '''
        Perform a binary search to find the 1dB compression point.
        Args:
            p_tx_start: starting power to search in dBm
            p_tx_end: ending power to search in dBm
            small_signal_gain: small signal gain at the frequency in dB
            resolution: stop criteria in dB

        Returns: Output power at 1dB compression point in dBm

        '''
        low     = p_tx_start
        high    = p_tx_end
        op1dB_i = None

        while high - low > resolution:
            mid = (low + high) / 2

            # Set the power level and measure gain
            self.scpi_sg.write(f"POW:LEV {mid}")
            peak_value  = self.sa_sweep_marker_max()
            gain_i      = peak_value + self.loss - mid
            gain_diff   = small_signal_gain - gain_i
            self.lcd_p_out.emit(peak_value + self.loss)

            # Check if we found the 1dB compression point
            if gain_diff >= 1:
                # We've exceeded 1dB compression, search lower
                high    = mid
                op1dB_i = peak_value + self.loss
            else:
                # Not yet at 1dB compression, search higher
                low = mid

        # Final measurement at the determined power level
        if op1dB_i is None:
            # If we didn't find a point with 1dB compression, use the highest power
            self.scpi_sg.write(f"POW:LEV {high}")
            peak_value  = self.sa_sweep_marker_max()
            op1dB_i     = peak_value + self.loss

        return op1dB_i

    def sa_sweep_marker_max(self):
        '''
        Perform a single sweep on the spectrum analyzer with average detector
        and return the peak marker value.
        Returns: Peak marker value in dBm
        '''

        # Set detector to average
        self.scpi_sa.write("SENSE:DETECTOR AVERage")
        # Read the Sweep time
        sweep_time = float(self.scpi_sa.query("SENSE:SWEEP:TIME?"))
        # call OPC after save
        self.scpi_sa.query("*OPC?")
        # Set sweep time to 10x for average detector
        self.scpi_sa.write(f"SENSE:SWEEP:TIME {sweep_time*10}")
        # Initiate a single sweep
        self.scpi_sa.write("INITiate:IMMediate")
        self.scpi_sa.query("*OPC?")
        # Set marker to peak
        self.scpi_sa.write("CALCulate:MARKer:MAXimum")
        # Get the peak value
        peak_value = float(self.scpi_sa.query("CALCulate:MARKer:Y?"))
        # Set sweep time to auto
        self.scpi_sa.write("SWEEP:TIME:AUTO ON")
        self.scpi_sa.query("*OPC?")

        return peak_value


    def stop(self):
        self.running = False

