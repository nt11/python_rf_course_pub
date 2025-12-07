#WKR_1
#...


class PaScan(QThread):
    # Define signals as class attributes (for progressbar and returned data)
    progress    = pyqtSignal(int)
    data        = pyqtSignal(np.ndarray, np.ndarray, bool, str, str) # freq, power, clf , legend, color
    csv         = pyqtSignal(np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray) # CSV file name
    log         = pyqtSignal(str)
    # LCD signals
    #WKR_2
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

        #WK_1
        #
        #WK_2
        #
        #
        #

        #WK_3
        #p_tx_nominal = ...

        # Create a list to store the scan data
        gain    = np.array([])
        op1dB   = np.array([])
        oip3    = np.array([])
        oip5    = np.array([])

        freq    = np.array([])
        #WKR_3
        #
            p_tx = p_tx_nominal - 10 # Check gain at low power
            #WK_4
            #
            #

            #WK_5
            #

            # Small signal gain
            #WK_6
            #
            # Get the peak value
            peak_value = self.sa_sweep_marker_max()

            # Set the reference level
            max_level  = np.ceil( peak_value/10 + 1)*10
            set_level  = float(self.scpi_sa.query(f"DISP:WIND:TRAC:Y:RLEV?") )
            if set_level != max_level:
                self.log.emit(f"Thread: Setting reference level to {max_level}")
                self.scpi_sa.write(f"DISP:WIND:TRAC:Y:RLEV {max_level}")

            #WK_7
            #
            gain = np.append(gain, small_signal_gain)
            freq  = np.append(freq, f)

            #WK_8
            #
            self.lcd_p_out.emit(peak_value + self.loss)


            # OP1dB
            #WK_9
            #op1dB_i = ...
            #WK_10
            #op1dB = ...
            #WK_11
            #

            # OIP3 and OIP5
            #WK_12
            #
            #
            subcarrier_power = self.sa_sweep_marker_max()
            p_i        = subcarrier_power + self.loss
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
            #WK_13
            #marker_y_value = ...
            p_i3        = marker_y_value + self.loss
            # Next peak twice (OIP5)
            f_oip5 = f_sub_h + (f_sub_h - f_sub_l)*2
            self.scpi_sa.write(f"CALCulate:MARKer:X {f_oip5} Hz")
            # Get the peak value
            #WK_14
            #marker_y_value = ...
            p_i5        = marker_y_value + self.loss

            #WKR_4
            #oip3_i = ...


            oip5_i = p_i + (p_i - p_i5)/4
            oip3 = np.append(oip3, oip3_i)
            oip5 = np.append(oip5, oip5_i)
            self.lcd_oip3.emit(oip3_i)
            self.lcd_oip5.emit(oip5_i)

            #WKR_5
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
            #WK_17
            #
            peak_value  = self.sa_sweep_marker_max()
            #WK_18
            #gain_i      = ...
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
        #WK_15
        #
        #WK_16
        #
        #peak_value = ...
        # Set sweep time to auto
        self.scpi_sa.write("SWEEP:TIME:AUTO ON")
        self.scpi_sa.query("*OPC?")

        return peak_value


    def stop(self):
        self.running = False

