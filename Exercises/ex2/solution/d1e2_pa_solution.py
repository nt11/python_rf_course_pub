
class PA():
    def __init__(self, serial: str) -> None:
        """
        Initialize class. Read from a data file the curves of an amplifier
        :param serial: The serial of the PA
        """
        try:
            with open(f"{serial}.txt") as fid:
                pa_data = fid.read()
        except Exception as e:
            print(f"Could not read file {serial}.txt")
            exit()

        self.serial = serial
        self.measurements = {}
        pa_data = pa_data.split("\n")
        pa_data = pa_data [1:]
        for line in pa_data:
            try:
                fields = line.split(",")
                pin    = float(fields[0])
                pout   = float(fields[1])
                f      = int(fields[2])
                if f not in self.measurements.keys():  # check if frequency doesn't exist yet
                    self.measurements[f] = []
                self.measurements[f].append({'pin': pin, 'pout': pout, 'gain': pout - pin})

            except Exception as e: # In case of parsing error, continue (e.g. blank line)
                pass

    def compute_small_signal_gain(self, f: int, N: int = 5) -> float:
        """
        Computes the small signal gain for an amplifier at a frequency
        :param f: Frequency
        :param N: Number of points to use in the calculation
        :return:
        """
        if f not in self.measurements:
            return None

        gain_sum = 0

        for entry in self.measurements[f][0:N]:
            gain_sum += entry['gain']
        return gain_sum / N

        # Another way to do it:
        # return sum(list(map(lambda x: x['gain'], self.measurements[f][0:N])))/N

    def compute_output_p1db(self, f: int) -> float:
        """
        Computes the P1dB for an amplifier at a frequency

        :param f: Frequency to check
        :return: Output P1dB if found, None otherwise
        """
        if f not in self.measurements: # Frequency wasn't in file
            return None

        ss_gain = self.compute_small_signal_gain(f)
        for entry in self.measurements[f]:
            if entry['gain'] <= ss_gain - 1.0: #p1dB
                return entry['pout']

        return None # If no P1dB was found


if __name__ == "__main__":
    #serials = ['SN1234', 'SN2222', 'SN3333', 'SN4321', 'SN4444'] # need to refer to correct directory
    serials = ['../SN1234', '../SN2222', '../SN3333', '../SN4321', '../SN4444']

    db = []
    for ser in serials:
        db.append(PA(ser))

    # print all P1dBs

    for pa in db:
        print(f"Serial number {pa.serial}:")
        print("--------------------------")
        for f in pa.measurements:
            print(f"Frequency = {f}, Small signal gain = {pa.compute_small_signal_gain(f):.2f} OP1dB = {pa.compute_output_p1db(f):.2f}")
        print("\n")


