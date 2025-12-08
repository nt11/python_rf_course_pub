"""
Simple Multitone Signal Generator Example using pyarbtools

This example demonstrates how to:
1. Generate a multitone signal
2. Connect to an MXG signal generator
3. Download the waveform to the ARB
4. Play the signal

Requirements:
- pyarbtools library
- python_rf_course_utils library
- MXG signal generator accessible on network
"""

import numpy as np
import pyarbtools as arb
from python_rf_course_utils.arb import multitone


def main():
    # ========================================
    # Configuration Parameters
    # ========================================

    # Signal generator IP address (modify to match your setup)
    MXG_IP = '10.0.0.14'

    # Signal parameters
    CENTER_FREQ = 1e9          # Center frequency: 1 GHz
    SAMPLING_FREQ = 20e6       # Sampling frequency: 20 MHz (in Hz)
    SAMPLING_FREQ_MHZ = 20.0   # Sampling frequency: 20 MHz (for multitone function)

    # Multitone parameters
    BANDWIDTH_MHZ = 4.0        # Bandwidth of multitone signal in MHz
    NUM_TONES = 5              # Number of tones to generate
    FFT_SIZE = 2048            # FFT size for signal generation

    # ARB configuration
    IQ_SCALE = 70              # IQ scaling factor (typical value)
    WAVEFORM_NAME = 'MultiToneExample'  # Name for the downloaded waveform

    print("=" * 60)
    print("Multitone Signal Generation Example")
    print("=" * 60)

    # ========================================
    # Step 1: Generate the Multitone Signal
    # ========================================
    print("\n[Step 1] Generating multitone signal...")
    print(f"  - Bandwidth: {BANDWIDTH_MHZ} MHz")
    print(f"  - Number of tones: {NUM_TONES}")
    print(f"  - Sampling frequency: {SAMPLING_FREQ_MHZ} MHz")
    print(f"  - FFT size: {FFT_SIZE}")

    # Generate the multitone IQ data
    iq_data = multitone(BW=BANDWIDTH_MHZ,
                        Ntones=NUM_TONES,
                        Fs=SAMPLING_FREQ_MHZ,
                        Nfft=FFT_SIZE)

    print(f"  ✓ Generated {len(iq_data)} IQ samples")
    print(f"  ✓ Signal duration: {len(iq_data)/SAMPLING_FREQ*1e3:.2f} ms")

    # ========================================
    # Step 2: Connect to MXG Signal Generator
    # ========================================
    print(f"\n[Step 2] Connecting to MXG at {MXG_IP}...")

    try:
        # Create VSG (Vector Signal Generator) object
        sig_gen = arb.instruments.VSG(MXG_IP, timeout=3)
        print("  ✓ Connected successfully")
    except Exception as e:
        print(f"  ✗ Connection failed: {e}")
        print("\nPlease check:")
        print("  1. MXG IP address is correct")
        print("  2. MXG is powered on and accessible on the network")
        print("  3. No firewall is blocking the connection")
        return

    # ========================================
    # Step 3: Configure the ARB
    # ========================================
    print("\n[Step 3] Configuring ARB...")
    print(f"  - Sampling frequency: {SAMPLING_FREQ/1e6} MHz")
    print(f"  - IQ scale: {IQ_SCALE}")

    # Configure the signal generator
    sig_gen.configure(fs=SAMPLING_FREQ, iqScale=IQ_SCALE)
    print("  ✓ Configuration complete")

    # ========================================
    # Step 4: Download Waveform
    # ========================================
    print(f"\n[Step 4] Downloading waveform '{WAVEFORM_NAME}'...")

    # Download the IQ data to the signal generator
    sig_gen.download_wfm(iq_data, wfmID=WAVEFORM_NAME)
    print("  ✓ Waveform downloaded successfully")

    # ========================================
    # Step 5: Configure Output Parameters
    # ========================================
    print("\n[Step 5] Configuring output parameters...")

    # Set center frequency
    sig_gen.set_cf(CENTER_FREQ)
    print(f"  ✓ Center frequency: {CENTER_FREQ/1e9} GHz")

    # Set sampling frequency
    sig_gen.set_fs(SAMPLING_FREQ)
    print(f"  ✓ Sampling frequency: {SAMPLING_FREQ/1e6} MHz")

    # Turn off Automatic Level Control (ALC)
    # CRITICAL: Use integer 0/1, NOT boolean False/True!
    sig_gen.set_alcState(0)
    print("  ✓ ALC: OFF")

    # ========================================
    # Step 6: Play the Waveform
    # ========================================
    print(f"\n[Step 6] Playing waveform '{WAVEFORM_NAME}'...")

    # Start waveform playback
    sig_gen.play(WAVEFORM_NAME)
    print("  ✓ Waveform playback started")

    # ========================================
    # Summary
    # ========================================
    print("\n" + "=" * 60)
    print("SUCCESS! Multitone signal is now playing on the MXG")
    print("=" * 60)
    print("\nSignal Configuration:")
    print(f"  Center Frequency:    {CENTER_FREQ/1e9} GHz")
    print(f"  Sampling Frequency:  {SAMPLING_FREQ/1e6} MHz")
    print(f"  Bandwidth:           {BANDWIDTH_MHZ} MHz")
    print(f"  Number of Tones:     {NUM_TONES}")
    print(f"  Waveform Name:       {WAVEFORM_NAME}")

    print("\nTo stop the signal, call: sig_gen.stop()")
    print("\nPress Ctrl+C to stop the signal and exit...")

    # Keep running until user stops
    try:
        import time
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n\nStopping signal...")
        sig_gen.stop()
        print("✓ Signal stopped")
        print("Goodbye!")


if __name__ == "__main__":
    main()
