"""
Simple Multitone Signal Generator Example using pyarbtools

This example demonstrates how to:
1. Generate a multitone signal
2. Connect to an MXG signal generator
3. Download the waveform to the ARB
4. Play the signal

This is a completely standalone example with no external dependencies
beyond pyarbtools and numpy.

Requirements:
- pyarbtools library
- numpy
- MXG signal generator accessible on network
"""

from typing import Tuple
import numpy as np
import pyarbtools as arb


def multitone(BW: float, Ntones: int, Fs: float, Nfft: int = 4096, DEBUG=False) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    '''
    Design a multi-tone signal in the frequency domain and return the time domain signal.
    Flat amplitude symmetrical around DC.

    :param BW: Bandwidth in MHz
    :param Ntones: Number of tones to generate
    :param Fs: Sampling frequency in MHz
    :param Nfft: FFT size (default 4096)
    :param DEBUG: If True, return (x, X, F). If False, return only x
    :return: x - Periodic time domain multi-tone signal, X - frequency domain, F - Frequency vector
    '''
    # Generate the frequency vector (symmetric around DC)
    f = np.linspace(-BW / 2, BW / 2, Ntones)
    # Generate the amplitude vector
    A = np.ones(Ntones)
    # Generate a random phase vector
    phi = np.random.rand(Ntones) * 2 * np.pi
    # Initialize the frequency domain vector to zeros
    X = np.zeros(Nfft, dtype=complex)
    # Generate the frequency domain signal (with frequency f rounded to the nearest bin)
    for i in range(Ntones):
        # Calculate the bin index for the frequency f[i] while the DC bin is at the center
        bin_index = int(np.round(f[i] / Fs * Nfft)) + Nfft // 2
        # Set the amplitude and phase
        X[bin_index] = A[i] * np.exp(1j * phi[i])
    # Generate the time domain signal
    x = np.fft.ifft(np.fft.ifftshift(X))
    if DEBUG:
        F = -Fs / 2 + Fs / Nfft * np.arange(Nfft)
        return x / np.max(np.abs(x)), X, F
    else:
        return x / np.max(np.abs(x))


def main():
    # ========================================
    # Configuration Parameters
    # ========================================

    # Signal generator IP address (modify to match your setup)
    MXG_IP = '10.0.0.14'

    # Signal parameters
    CENTER_FREQ = 1e9          # Center frequency: 1 GHz
    OUTPUT_POWER = -20         # Output power: -20 dBm
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

    # Set output power using SCPI command via pyarbtools
    sig_gen.write(f":POWER {OUTPUT_POWER} dBm")
    print(f"  ✓ Output power: {OUTPUT_POWER} dBm")

    # Turn off Automatic Level Control (ALC)
    # CRITICAL: Use integer 0/1, NOT boolean False/True!
    sig_gen.set_alcState(0)
    print("  ✓ ALC: OFF")

    # Enable RF output
    sig_gen.write(":OUTPUT:STATE ON")
    print("  ✓ RF output: ON")

    # Enable modulation output
    sig_gen.write(":OUTPUT:MOD:STATE ON")
    print("  ✓ Modulation: ON")

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
    print(f"  Output Power:        {OUTPUT_POWER} dBm")
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
