"""
Setup Test Script for RF Measurement System

This script tests the basic connectivity and functionality of:
1. Signal Generator (MXG)
2. Spectrum Analyzer

It validates that the instruments are responsive and working correctly.
Uses pyvisa-py with @py backend.
"""

import pyvisa
import numpy as np
import time
from typing import Tuple, Optional
import pyarbtools as arb


class TestResult:
    """Store test results and status"""
    def __init__(self):
        self.tests_passed = []
        self.tests_failed = []
        self.warnings = []

    def add_pass(self, test_name: str):
        self.tests_passed.append(test_name)
        print(f"  ✓ {test_name}")

    def add_fail(self, test_name: str, reason: str):
        self.tests_failed.append(f"{test_name}: {reason}")
        print(f"  ✗ {test_name}: {reason}")

    def add_warning(self, warning: str):
        self.warnings.append(warning)
        print(f"  ⚠ WARNING: {warning}")

    def get_verdict(self) -> str:
        """Get final verdict on setup status"""
        if len(self.tests_failed) == 0:
            if len(self.warnings) == 0:
                return "✓ ALL TESTS PASSED - Setup is working perfectly!"
            else:
                return f"✓ ALL TESTS PASSED - Setup is working (with {len(self.warnings)} warning(s))"
        else:
            return f"✗ TESTS FAILED - {len(self.tests_failed)} issue(s) detected"


def check_scpi_errors(instr, instrument_name: str, results: TestResult) -> bool:
    """
    Check for SCPI errors in the instrument error queue
    Returns True if no errors, False if errors found
    """
    try:
        error_str = instr.query(':SYST:ERR?').strip()
        error_code = int(error_str.split(',')[0])

        if error_code != 0:
            results.add_fail(f"SCPI Error Check ({instrument_name})",
                           f"Error {error_str}")
            return False
        return True
    except Exception as e:
        results.add_warning(f"Could not check SCPI errors on {instrument_name}: {e}")
        return True  # Don't fail test if error checking fails


def test_signal_generator(sg_ip: str, results: TestResult) -> Optional[object]:
    """
    Test Signal Generator connectivity and basic functionality
    Returns the instrument object if successful, None otherwise
    """
    print("\n" + "="*60)
    print("SIGNAL GENERATOR TESTS")
    print("="*60)

    rm = pyvisa.ResourceManager('@py')

    try:
        # Connect to signal generator
        print(f"\n[1] Connecting to Signal Generator at {sg_ip}...")
        sg = rm.open_resource(f'TCPIP::{sg_ip}::INSTR')
        sg.timeout = 5000
        results.add_pass("Signal Generator connection established")

        # Test 1: Reset and Clear
        print("\n[2] Resetting and clearing instrument...")
        sg.write('*RST')
        sg.query('*OPC?')  # Wait for reset to complete
        sg.write('*CLS')
        results.add_pass("Reset (*RST) and Clear (*CLS)")
        check_scpi_errors(sg, "Signal Generator", results)

        # Test 2: Query IDN
        print("\n[3] Querying instrument identification...")
        idn = sg.query('*IDN?').strip()
        parts = idn.split(',')
        if len(parts) >= 4:
            manufacturer, model, serial, firmware = parts[0], parts[1], parts[2], parts[3]
            print(f"  Manufacturer: {manufacturer}")
            print(f"  Model: {model}")
            print(f"  Serial: {serial}")
            print(f"  Firmware: {firmware}")
            results.add_pass("*IDN? query successful")
        else:
            results.add_fail("*IDN? query", "Unexpected response format")
            return None
        check_scpi_errors(sg, "Signal Generator", results)

        # Test 3: Frequency and Power Write/Query (Modulation OFF)
        print("\n[4] Testing frequency and power control...")

        # Turn modulation off first
        sg.write(':OUTPUT:MOD:STATE OFF')
        sg.query('*OPC?')  # Wait for operation to complete
        check_scpi_errors(sg, "Signal Generator", results)

        # Test frequency
        test_freq = 2.5e9  # 2.5 GHz
        sg.write(f':FREQ:CW {test_freq}')
        sg.query('*OPC?')  # Wait for operation to complete
        freq_read = float(sg.query(':FREQ:CW?').strip())
        if abs(freq_read - test_freq) < 1e3:  # Within 1 kHz tolerance
            results.add_pass(f"Frequency write/query (set: {test_freq/1e9:.3f} GHz, read: {freq_read/1e9:.3f} GHz)")
        else:
            results.add_fail("Frequency write/query",
                           f"Mismatch - set: {test_freq/1e9:.3f} GHz, read: {freq_read/1e9:.3f} GHz")
        check_scpi_errors(sg, "Signal Generator", results)

        # Test power
        test_power = -10  # dBm
        sg.write(f':POWER {test_power}')
        sg.query('*OPC?')  # Wait for operation to complete
        power_read = float(sg.query(':POWER?').strip())
        if abs(power_read - test_power) < 0.1:  # Within 0.1 dB tolerance
            results.add_pass(f"Power write/query (set: {test_power} dBm, read: {power_read:.1f} dBm)")
        else:
            results.add_fail("Power write/query",
                           f"Mismatch - set: {test_power} dBm, read: {power_read:.1f} dBm")
        check_scpi_errors(sg, "Signal Generator", results)

        # Test 4: ARB functionality using pyarbtools
        print("\n[5] Testing ARB functionality...")
        start_time = time.time()

        try:
            # Generate a simple test waveform (1000 samples)
            test_wfm_length = 1000
            i_data = np.sin(2 * np.pi * np.arange(test_wfm_length) / 10) * 0.5
            q_data = np.cos(2 * np.pi * np.arange(test_wfm_length) / 10) * 0.5
            iq_data = i_data + 1j * q_data

            # Create ARB object using pyarbtools
            arb_gen = arb.instruments.VSG(sg_ip, timeout=5)

            # Configure ARB
            test_fs = 20e6  # 20 MHz sampling frequency
            arb_gen.configure(fs=test_fs, iqScale=70)

            # Download waveform
            arb_gen.download_wfm(iq_data, wfmID='TEST_WFM')

            load_time = time.time() - start_time

            # Set basic parameters
            arb_gen.set_cf(2.5e9)  # 2.5 GHz center frequency
            arb_gen.set_fs(test_fs)
            arb_gen.set_alcState(0)  # ALC off

            # Verify waveform is loaded by trying to play it
            arb_gen.play('TEST_WFM')

            if load_time < 5.0:  # Should load in less than 5 seconds for small waveform
                results.add_pass(f"ARB waveform download and configuration (load time: {load_time:.2f}s)")
            else:
                results.add_warning(f"ARB waveform loaded but slow (load time: {load_time:.2f}s)")
                results.add_pass("ARB waveform download and configuration (slow)")

            check_scpi_errors(sg, "Signal Generator", results)

            # Stop ARB playback
            arb_gen.stop()

        except Exception as e:
            results.add_fail("ARB functionality test", f"Error: {e}")
            check_scpi_errors(sg, "Signal Generator", results)

        # Clean up - turn off RF output
        sg.write(':OUTPUT:STATE OFF')

        print(f"\n{'='*60}")
        return sg

    except pyvisa.errors.VisaIOError as e:
        results.add_fail("Signal Generator connection", str(e))
        print(f"\n{'='*60}")
        return None
    except Exception as e:
        results.add_fail("Signal Generator test", f"Unexpected error: {e}")
        print(f"\n{'='*60}")
        return None


def test_spectrum_analyzer(sa_ip: str, results: TestResult) -> Optional[object]:
    """
    Test Spectrum Analyzer connectivity and basic functionality
    Returns the instrument object if successful, None otherwise
    """
    print("\n" + "="*60)
    print("SPECTRUM ANALYZER TESTS")
    print("="*60)

    rm = pyvisa.ResourceManager('@py')

    try:
        # Connect to spectrum analyzer
        print(f"\n[1] Connecting to Spectrum Analyzer at {sa_ip}...")
        sa = rm.open_resource(f'TCPIP::{sa_ip}::INSTR')
        sa.timeout = 15000  # Longer timeout for sweeps
        results.add_pass("Spectrum Analyzer connection established")

        # Test 1: Reset and Clear
        print("\n[2] Resetting and clearing instrument...")
        sa.write('*RST')
        sa.query('*OPC?')  # Wait for reset to complete
        sa.write('*CLS')
        results.add_pass("Reset (*RST) and Clear (*CLS)")
        check_scpi_errors(sa, "Spectrum Analyzer", results)

        # Test 2: Query IDN
        print("\n[3] Querying instrument identification...")
        idn = sa.query('*IDN?').strip()
        parts = idn.split(',')
        if len(parts) >= 4:
            manufacturer, model, serial, firmware = parts[0], parts[1], parts[2], parts[3]
            print(f"  Manufacturer: {manufacturer}")
            print(f"  Model: {model}")
            print(f"  Serial: {serial}")
            print(f"  Firmware: {firmware}")
            results.add_pass("*IDN? query successful")
        else:
            results.add_fail("*IDN? query", "Unexpected response format")
            return None
        check_scpi_errors(sa, "Spectrum Analyzer", results)

        # Test 3: Set frequency span and RBW, read trace
        print("\n[4] Testing frequency configuration and trace acquisition...")

        # Configure basic settings
        sa.write(':FREQ:CENT 2.5 GHz')
        sa.write(':FREQ:SPAN 100 MHz')
        sa.write(':BAND:RES 1 MHz')
        sa.write(':SWE:POIN 401')  # Fewer points for faster sweep
        sa.query('*OPC?')  # Wait for configuration to complete
        check_scpi_errors(sa, "Spectrum Analyzer", results)

        # Read back settings
        cf = float(sa.query(':FREQ:CENT?').strip())
        span = float(sa.query(':FREQ:SPAN?').strip())
        rbw = float(sa.query(':BAND:RES?').strip())
        points = int(sa.query(':SWE:POIN?').strip())

        print(f"  Center Frequency: {cf/1e9:.3f} GHz")
        print(f"  Span: {span/1e6:.1f} MHz")
        print(f"  RBW: {rbw/1e6:.3f} MHz")
        print(f"  Points: {points}")
        results.add_pass("Frequency and RBW configuration")
        check_scpi_errors(sa, "Spectrum Analyzer", results)

        # Trigger a sweep and read trace
        print("\n[5] Acquiring trace data...")
        start_time = time.time()

        sa.write(':INIT:IMM')  # Initiate sweep
        sa.query('*OPC?')  # Wait for sweep to complete

        sweep_time = time.time() - start_time

        # Read trace
        sa.write(':FORM:DATA ASCII')
        trace_data = sa.query(':TRAC? TRACE1').strip()
        trace_values = [float(x) for x in trace_data.split(',')]

        read_time = time.time() - start_time

        # Validate trace data
        if len(trace_values) == points:
            # Check if values are reasonable (typical SA range: -120 to +30 dBm)
            min_val = min(trace_values)
            max_val = max(trace_values)
            avg_val = sum(trace_values) / len(trace_values)

            if -150 < min_val < 50 and -150 < max_val < 50:
                print(f"  Trace acquired: {len(trace_values)} points")
                print(f"  Value range: {min_val:.1f} to {max_val:.1f} dBm (avg: {avg_val:.1f} dBm)")
                print(f"  Sweep time: {sweep_time:.2f}s, Total read time: {read_time:.2f}s")

                if read_time < 10.0:
                    results.add_pass(f"Trace acquisition and read (time: {read_time:.2f}s)")
                else:
                    results.add_warning(f"Trace acquisition slow (time: {read_time:.2f}s)")
                    results.add_pass("Trace acquisition and read (slow)")
            else:
                results.add_fail("Trace data validation",
                               f"Values out of expected range: {min_val:.1f} to {max_val:.1f} dBm")
        else:
            results.add_fail("Trace data validation",
                           f"Expected {points} points, got {len(trace_values)}")

        check_scpi_errors(sa, "Spectrum Analyzer", results)

        print(f"\n{'='*60}")
        return sa

    except pyvisa.errors.VisaIOError as e:
        results.add_fail("Spectrum Analyzer connection", str(e))
        print(f"\n{'='*60}")
        return None
    except Exception as e:
        results.add_fail("Spectrum Analyzer test", f"Unexpected error: {e}")
        print(f"\n{'='*60}")
        return None


def main():
    """Main test routine"""
    print("="*60)
    print("RF MEASUREMENT SETUP TEST")
    print("="*60)
    print("\nThis script will test the connectivity and basic")
    print("functionality of your Signal Generator and Spectrum Analyzer.")
    print()

    # Get IP addresses from user
    sg_ip = input("Enter Signal Generator IP address: ").strip()
    sa_ip = input("Enter Spectrum Analyzer IP address: ").strip()

    if not sg_ip or not sa_ip:
        print("\nError: Both IP addresses are required!")
        return

    print(f"\nSignal Generator: {sg_ip}")
    print(f"Spectrum Analyzer: {sa_ip}")

    # Initialize test results
    results = TestResult()

    # Test instruments
    sg = test_signal_generator(sg_ip, results)
    sa = test_spectrum_analyzer(sa_ip, results)

    # Clean up - Reset instruments to default state
    print("\n" + "="*60)
    print("CLEANUP - Resetting instruments")
    print("="*60)
    try:
        if sg:
            print("Resetting Signal Generator...")
            sg.write('*RST')
            sg.query('*OPC?')
            sg.write('*CLS')
            sg.close()
            print("  ✓ Signal Generator reset and closed")
        if sa:
            print("Resetting Spectrum Analyzer...")
            sa.write('*RST')
            sa.query('*OPC?')
            sa.write('*CLS')
            sa.close()
            print("  ✓ Spectrum Analyzer reset and closed")
    except Exception as e:
        print(f"  ⚠ Warning during cleanup: {e}")

    # Print summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    print(f"\nTests Passed: {len(results.tests_passed)}")
    print(f"Tests Failed: {len(results.tests_failed)}")
    print(f"Warnings: {len(results.warnings)}")

    if results.tests_failed:
        print("\n❌ Failed Tests:")
        for failure in results.tests_failed:
            print(f"  - {failure}")

    if results.warnings:
        print("\n⚠️  Warnings:")
        for warning in results.warnings:
            print(f"  - {warning}")

    # Final verdict
    print("\n" + "="*60)
    print("VERDICT")
    print("="*60)
    print(f"\n{results.get_verdict()}\n")


if __name__ == "__main__":
    main()
