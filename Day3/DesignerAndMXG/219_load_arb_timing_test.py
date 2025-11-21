"""
Diagnostic script to measure timing of ARB play() method
This script tests different approaches to starting ARB playback
"""
import pyarbtools as arb
import pyvisa
import time

# Test configuration
mxg_ip = '10.0.0.14'
Fs = 20e6  # Hz Sampling frequency
name = 'TestWaveform'

# Generate a simple test waveform
import numpy as np
iqdata = np.exp(1j * 2 * np.pi * 1e6 * np.arange(1000) / Fs)

# Connect using both pyarbtools and pyvisa
print("=" * 60)
print("ARB PLAY TIMING DIAGNOSTIC TEST")
print("=" * 60)

# Test 1: Standard pyarbtools play() method
print("\n[Test 1] Standard pyarbtools play() method")
print("-" * 60)

start_time = time.perf_counter()
sigarb = arb.instruments.VSG(mxg_ip, timeout=5)
connect_time = time.perf_counter() - start_time
print(f"Connection time: {connect_time:.3f} seconds")

start_time = time.perf_counter()
sigarb.configure(fs=Fs, iqScale=70)
sigarb.download_wfm(iqdata, wfmID=name)
setup_time = time.perf_counter() - start_time
print(f"Configure + download time: {setup_time:.3f} seconds")

sigarb.set_cf(1e9)
sigarb.set_fs(Fs)
sigarb.set_alcState(0)

start_time = time.perf_counter()
sigarb.play(name)
play_time = time.perf_counter() - start_time
print(f"play() method time: {play_time:.3f} seconds *** THIS IS THE ISSUE ***")

# Test 2: Direct SCPI commands with timing breakdown
print("\n[Test 2] Direct SCPI commands with timing breakdown")
print("-" * 60)

# Connect with pyvisa
rm = pyvisa.ResourceManager('@py')
sig = rm.open_resource(f"TCPIP0::{mxg_ip}::inst0::INSTR")
sig.timeout = 5000

# Stop any current playback
sig.write("radio:arb:state 0")
sig.write("output:modulation 0")
time.sleep(0.1)

# Configure and download waveform (reusing pyarbtools)
sigarb2 = arb.instruments.VSG(mxg_ip, timeout=5)
sigarb2.configure(fs=Fs, iqScale=70)
sigarb2.download_wfm(iqdata, wfmID=name + '2')
sigarb2.set_cf(1e9)
sigarb2.set_fs(Fs)
sigarb2.set_alcState(0)

# Now measure each SCPI command individually
print("\nSending SCPI commands individually:")

start_time = time.perf_counter()
sig.write('radio:arb:waveform "WFM1:{}2"'.format(name))
t1 = time.perf_counter() - start_time
print(f"  1. Set waveform: {t1:.3f} seconds")

start_time = time.perf_counter()
sig.write("output 1")
t2 = time.perf_counter() - start_time
print(f"  2. RF output ON: {t2:.3f} seconds")

start_time = time.perf_counter()
sig.write("output:modulation 1")
t3 = time.perf_counter() - start_time
print(f"  3. Modulation ON: {t3:.3f} seconds")

start_time = time.perf_counter()
sig.write("radio:arb:state 1")
t4 = time.perf_counter() - start_time
print(f"  4. ARB state ON: {t4:.3f} seconds *** LIKELY CULPRIT ***")

start_time = time.perf_counter()
err = sig.query("SYST:ERR?").strip()
t5 = time.perf_counter() - start_time
print(f"  5. Error check: {t5:.3f} seconds (error: {err})")

total_direct = t1 + t2 + t3 + t4 + t5
print(f"\nTotal time (direct SCPI): {total_direct:.3f} seconds")

# Test 3: Using *OPC? for synchronization
print("\n[Test 3] Using *OPC? for proper synchronization")
print("-" * 60)

# Stop playback
sig.write("radio:arb:state 0")
sig.write("output:modulation 0")
time.sleep(0.1)

start_time = time.perf_counter()
sig.write('radio:arb:waveform "WFM1:{}2"'.format(name))
sig.write("output 1")
sig.write("output:modulation 1")
sig.write("radio:arb:state 1")
# Wait for operation to complete
response = sig.query("*OPC?")
opc_time = time.perf_counter() - start_time
print(f"Time with *OPC? query: {opc_time:.3f} seconds")
print(f"*OPC? response: {response.strip()}")

# Test 4: Pre-enable outputs (might reduce startup time)
print("\n[Test 4] Pre-enable outputs before setting ARB state")
print("-" * 60)

# Stop playback
sig.write("radio:arb:state 0")
time.sleep(0.1)

# Enable outputs first
sig.write("output 1")
sig.write("output:modulation 1")
sig.write('radio:arb:waveform "WFM1:{}2"'.format(name))

start_time = time.perf_counter()
sig.write("radio:arb:state 1")
response = sig.query("*OPC?")
pre_enable_time = time.perf_counter() - start_time
print(f"ARB state ON with pre-enabled outputs: {pre_enable_time:.3f} seconds")

# Summary
print("\n" + "=" * 60)
print("TIMING SUMMARY")
print("=" * 60)
print(f"Test 1 - pyarbtools play():           {play_time:.3f} seconds")
print(f"Test 2 - Direct SCPI (total):         {total_direct:.3f} seconds")
print(f"Test 3 - With *OPC? synchronization:  {opc_time:.3f} seconds")
print(f"Test 4 - Pre-enabled outputs:         {pre_enable_time:.3f} seconds")
print("=" * 60)

# Cleanup
sig.close()
rm.close()
