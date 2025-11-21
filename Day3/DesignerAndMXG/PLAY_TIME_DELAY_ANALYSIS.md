# ARB Play Time Delay Analysis

## Root Cause

The 2-second delay occurs because of the following sequence:

1. **`download_wfm()` stops playback**
   The pyarbtools library's `download_wfm()` method explicitly stops ARB playback:
   ```python
   self.set_modState(0)  # Stop modulation
   self.set_arbState(0)  # Stop ARB
   ```

2. **`play()` restarts from cold state**
   The `play()` method then has to:
   - Select the waveform
   - Enable RF output
   - Enable modulation
   - **Start ARB from stopped state** ← THIS is the 2-second delay

3. **Instrument initialization overhead**
   When the MXG ARB transitions from OFF → ON, the firmware performs:
   - Hardware initialization
   - PLL settling
   - Level calibration
   - Internal synchronization

   **This inherently takes ~2 seconds in the MXG firmware.**

## Why Previous Fixes Failed

- Adding `*OPC?` doesn't help because the delay is in the instrument, not a synchronization issue
- Direct SCPI commands have the same delay because `radio:arb:state 1` is what takes 2 seconds
- Optimizing the error checking doesn't help because the delay is before error checking

## Actual Solutions

### Solution 1: Keep ARB Running (Best for simple cases)

Instead of stop/download/play cycle, keep the ARB running and just switch waveforms:

```python
# First time setup only
arb.configure(fs=Fs, iqScale=70)
arb.set_alcState(0)
arb.play('InitialWaveform')  # 2 second delay once

# Subsequent updates - DON'T call play()!
# Upload new waveform while ARB is running (if possible)
# OR: Pre-upload multiple waveforms and switch between them
```

### Solution 2: Use List Mode (Best for multiple waveforms)

MXG supports List Mode with waveform switching in **≤900 microseconds** (vs 2 seconds):

- Pre-load multiple waveforms
- Use list mode to switch between them seamlessly
- No stop/start required

### Solution 3: Direct SCPI Without Stopping

For the specific case in `220_main_mxg.py` where the waveform is updated frequently:

```python
def cb_multitone_update(self):
    if self.arb_gen is not None:
        sig = multitone(...)

        # Method A: Check if we need to restart
        is_running = int(self.sig_gen.query("radio:arb:state?"))

        if not is_running:
            # Full cycle (first time)
            self.arb_gen.download_wfm(sig, wfmID='RfLabMultiTone')
            self.arb_gen.play('RfLabMultiTone')  # 2 second delay
        else:
            # Fast update - stop, upload, restart without delays
            self.sig_gen.write("radio:arb:state 0")
            # Upload directly to instrument memory without pyarbtools
            # (requires manual implementation of upload)
            self.sig_gen.write("radio:arb:state 1")
```

### Solution 4: Debounce Updates (Workaround)

Don't update on every dial/spinbox change. Wait for user to finish:

```python
def cb_multitone_update(self):
    # Cancel previous timer
    if hasattr(self, 'update_timer'):
        self.update_timer.stop()

    # Start new timer - only update after 500ms of no changes
    self.update_timer = QTimer()
    self.update_timer.setSingleShot(True)
    self.update_timer.timeout.connect(self._do_multitone_update)
    self.update_timer.start(500)

def _do_multitone_update(self):
    # Actual update here
    sig = multitone(...)
    self.arb_gen.download_wfm(sig, wfmID='RfLabMultiTone')
    self.arb_gen.play('RfLabMultiTone')  # 2 second delay
```

## Conclusion

**The 2-second delay is a fundamental characteristic of the MXG instrument when stopping and restarting the ARB.**

The only real solutions are:
1. **Don't stop the ARB** - Keep it running continuously
2. **Use List Mode** - For sub-millisecond switching
3. **Debounce** - Reduce the frequency of stop/start cycles
4. **Accept it** - If you must stop and restart, 2 seconds is normal

The pyarbtools library is working correctly - the delay is in the instrument firmware, not the software.
