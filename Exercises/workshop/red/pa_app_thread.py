#WKR_1: Import the necessary modules (PyQt6.QtCore QThread and pyqtSignal, numpy as np)
#...


class PaScan(QThread):
    # Define signals as class attributes (for progressbar and returned data)
    progress    = pyqtSignal(int)
    data        = pyqtSignal(np.ndarray, np.ndarray, bool, str, str) # freq, power, clf , legend, color
    csv         = pyqtSignal(np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray) # CSV file name
    log         = pyqtSignal(str)
    # LCD signals
    #WKR_2: Define the LCD signals (lcd_g, lcd_op1dB, lcd_oip3, lcd_oip5, lcd_p_out)
    #lcd_g      = ...
    #lcd_op1dB  = ...
    #lcd_oip3   = ...
    #lcd_oip5   = ...
    #lcd_p_out  = ...

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

        #WK_1: Signal Generator RF Output On
        #
        #WK_2: Spectrum Analyzer Detector Average, Trace Mode Write, Single Sweep Mode
        #
        #
        #

        #WK_3: Get the power level from the signal generator into p_tx_nominal
        #p_tx_nominal = ...

        # Create a list to store the scan data
        gain    = np.array([])
        op1dB   = np.array([])
        oip3    = np.array([])
        oip5    = np.array([])

        freq    = np.array([])
        #WKR_3: Loop over the scan frequencies, generate both index i and frequency f
        #for ...
            # Set the SG to the frequency of the current scan point and power level
            p_tx = p_tx_nominal - 10 # Check gain at low power
            #WK_4: Set the signal generator frequency and power level
            #
            #

            #WK_5: Set the SA center frequency
            #

            # Small signal gain
            #WK_6: Set the signal generator modulation off for CW testing
            #
            # Get the peak value
            peak_value = self.sa_sweep_marker_max()

            # Set the reference level
            max_level  = np.ceil( peak_value/10 + 1)*10
            set_level  = float(self.scpi_sa.query(f"DISP:WIND:TRAC:Y:RLEV?") )
            if set_level != max_level:
                self.log.emit(f"Thread: Setting reference level to {max_level}")
                self.scpi_sa.write(f"DISP:WIND:TRAC:Y:RLEV {max_level}")

            # compute the gain and save the frequency and gain
            #WK_7: Compute the gain from the peak value, loss and power level
            #gain_i = ...
            gain = np.append(gain, gain_i)
            freq  = np.append(freq, f)
            # Update the Gain LCD
            #WK_8 Emit a signal to the gain LCD (slide 4-27, example o310)
            #
            self.lcd_p_out.emit(peak_value + self.loss)


            # OP1dB
            #WK_9: Call find_op1db_binary_search with range (p_tx_nominal - 6, p_tx_nominal + 5) and gain[-1] as reference
            #op1dB_i = ...
            #WK_10: Append the op1dB_i to the op1dB array
            #op1dB = ...
            #WK_11: Emit a signal to the OP1dB LCD (slide 4-27, example o310)
            #

            # OIP3 and OIP5
            # WK_12 Modulation On and tx power to p_tx_nominal on signal generator
            #
            #
            peak_value = self.sa_sweep_marker_max()
            p_i        = peak_value + self.loss
            # Get the frequency of subcarrier 1
            freq_sig1  = float(self.scpi_sa.query("CALCulate:MARKer:X?"))
            # Next peak twice (OIP3)
            self.scpi_sa.write("CALCulate:MARKer:MAXimum:NEXT")
            # Get the frequency of subcarrier 2
            freq_sig2  = float(self.scpi_sa.query("CALCulate:MARKer:X?"))
            f_sub_h = max(freq_sig1, freq_sig2)
            f_sub_l = min(freq_sig1, freq_sig2)
            # Set the marker to OIP3 (sub_h + (sub_h - sub_l))
            f_oip3 = f_sub_h + (f_sub_h - f_sub_l)
            self.scpi_sa.write(f"CALCulate:MARKer:X {f_oip3} Hz")
            # Get the peak value
            # WK_13: Get the peak value from the spectrum analyzer using a SCPI command
            #peak_value = ...
            p_i3        = peak_value + self.loss
            # Next peak twice (OIP5)
            f_oip5 = f_sub_h + (f_sub_h - f_sub_l)*2
            self.scpi_sa.write(f"CALCulate:MARKer:X {f_oip5} Hz")
            # Get the peak value
            # WK_14: Get the peak value from the spectrum analyzer using a SCPI command
            #peak_value = ...
            p_i5        = peak_value + self.loss

            #WKR_4: Compute the OIP3 (p_i is the fundamental power, p_i3 is the 3rd order power)
            #oip3_i = ...


            oip5_i = p_i + (p_i - p_i5)/4
            oip3 = np.append(oip3, oip3_i)
            oip5 = np.append(oip5, oip5_i)
            self.lcd_oip3.emit(oip3_i)
            self.lcd_oip5.emit(oip5_i)

            # if i%10==0:
            #WKR_5: Emit the data to the plot widget. emit the gain, op1dB, oip3 and oip5 using self.data.emit
            #clear the plot for the first call (use True) and don't clear for the rest (use False), use colors 'k', 'b', 'g', 'r'
            #
            #
            #
            #

            # Update the progress bar
            self.progress.emit(100 * (i + 1) // len(self.f_scan))
            if not self.running:
                break

        # Dump the data to a CSV file
        self.csv.emit(freq, gain, op1dB, oip3, oip5)

    def find_op1db_binary_search(self, p_tx_start, p_tx_end, gain_ref, resolution=0.1):
        low     = p_tx_start
        high    = p_tx_end
        op1dB_i = None

        while high - low > resolution:
            mid = (low + high) / 2

            # Set the power level and measure gain
            #WK_17: Set the signal generator power level to mid
            #
            peak_value  = self.sa_sweep_marker_max()
            #WK_18: Compute the gain from the peak value, loss and mid power level
            #gain_i      = ...
            gain_diff   = gain_ref - gain_i
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
        # Set detector to average
        self.scpi_sa.write("SENSE:DETECTOR AVERage")
        # Read the Sweep time
        sweep_time = float(self.scpi_sa.query("SENSE:SWEEP:TIME?"))
        # call OPC after save
        self.scpi_sa.query("*OPC?")
        # Set sweep time to 10x for average detector
        self.scpi_sa.write(f"SENSE:SWEEP:TIME {sweep_time*10}")
        # WK_15 Initiate a single sweep on the spectrum analyzer using a SCPI command
        #
        # WK_16 Check for operation complete using a SCPI command (OPC)
        #
        # Set marker to peak using a SCPI command
        #
        # Get the peak value
        #peak_value = ...
        # Set sweep time to auto
        self.scpi_sa.write("SWEEP:TIME:AUTO ON")
        self.scpi_sa.query("*OPC?")

        return peak_value


    def stop(self):
        self.running = False

