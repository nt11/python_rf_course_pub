# PA Measurement Algorithm Flowchart

## Algorithm Flow at `.run()` Level

```
┌─────────────────────────────────────────────────────────────┐
│                      START: PaScan.run()                    │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────┐
│ INITIALIZATION                                              │
│ • Turn ON RF output                                         │
│ • Set SA detector to AVERAGE mode                           │
│ • Get nominal TX power (P_tx_nominal)                       │
│ • Initialize result arrays: gain, op1dB, oip3, oip5, freq   │
└────────────────────────────┬────────────────────────────────┘
                             │
                             ▼
                ┌────────────────────────────┐
                │  For each frequency (f)    │
                │  in scan range f_scan      │
                └────────┬───────────────────┘
                         │
                         ▼
        ┌────────────────────────────────────────────┐
        │ SET FREQUENCY                              │
        │ • SG frequency = f                         │
        │ • SA center frequency = f                  │
        └────────┬───────────────────────────────────┘
                 │
                 ▼
        ┌────────────────────────────────────────────┐
        │ MEASURE 1: SMALL SIGNAL GAIN               │
        │ • Set TX power = P_tx_nominal - 10 dB      │
        │ • Modulation OFF (single tone)             │
        │ • sa_sweep_marker_max() → peak_value       │
        │ • Adjust SA reference level if needed      │
        │ • Gain = peak_value + loss - P_tx          │
        │ • Store gain, update LCD                   │
        └────────┬───────────────────────────────────┘
                 │
                 ▼
        ┌────────────────────────────────────────────┐
        │ MEASURE 2: P1dB (1dB COMPRESSION POINT)    │
        │ • Call find_op1db_binary_search()          │
        │   - Input: P_tx range, small_signal_gain   │
        │   - Output: Output power at 1dB comp       │
        │ • Store OP1dB, update LCD                  │
        └────────┬───────────────────────────────────┘
                 │
                 ▼
        ┌────────────────────────────────────────────┐
        │ MEASURE 3: OIP3 SETUP                      │
        │ • Modulation ON (two-tone signal)          │
        │ • Set TX power = P_tx_nominal              │
        │ • sa_sweep_marker_max() → find subcarrier  │
        │ • P_i = subcarrier_power + loss            │
        │ • Get freq_sig1 (1st subcarrier freq)      │
        │ • Find next peak → freq_sig2               │
        └────────┬───────────────────────────────────┘
                 │
                 ▼
        ┌────────────────────────────────────────────┐
        │ MEASURE 3a: OIP3 CALCULATION               │
        │ • f_sub_h = max(freq_sig1, freq_sig2)      │
        │ • f_sub_l = min(freq_sig1, freq_sig2)      │
        │ • f_oip3 = f_sub_h + (f_sub_h - f_sub_l)   │
        │ • Move marker to f_oip3                    │
        │ • Read marker → P_i3                       │
        │ • OIP3 = P_i + (P_i - P_i3) / 2            │
        │ • Store OIP3, update LCD                   │
        └────────┬───────────────────────────────────┘
                 │
                 ▼
        ┌────────────────────────────────────────────┐
        │ MEASURE 4: OIP5 CALCULATION                │
        │ • f_oip5 = f_sub_h + 2*(f_sub_h - f_sub_l) │
        │ • Move marker to f_oip5                    │
        │ • Read marker → P_i5                       │
        │ • OIP5 = P_i + (P_i - P_i5) / 4            │
        │ • Store OIP5, update LCD                   │
        └────────┬───────────────────────────────────┘
                 │
                 ▼
        ┌────────────────────────────────────────────┐
        │ EMIT DATA                                  │
        │ • Emit plotting data (gain, OP1dB, OIP3,   │
        │   OIP5 vs frequency)                       │
        │ • Update progress bar                      │
        └────────┬───────────────────────────────────┘
                 │
                 ▼
                ┌────────────────┐
                │ More frequencies│
                │ to scan?       │
                └───┬────────┬───┘
                    │ YES    │ NO
                    └───►────┘
                         │
                         ▼
        ┌────────────────────────────────────────────┐
        │ FINALIZATION                               │
        │ • Emit CSV data (all measurements)         │
        └────────┬───────────────────────────────────┘
                 │
                 ▼
        ┌────────────────────────────────────────────┐
        │                     END                    │
        └────────────────────────────────────────────┘
```

## Key Notes

### Measurement Sequence (per frequency point):
1. **Small Signal Gain** (low power, modulation OFF)
2. **P1dB** (variable power, modulation OFF, binary search)
3. **OIP3 & OIP5** (nominal power, modulation ON, two-tone analysis)

### Important Parameters:
- **Loss**: Cable/path loss compensation (added to all measurements)
- **P_tx_nominal**: Configured nominal transmit power
- **Small signal measurement**: Always at P_tx_nominal - 10 dB
- **Binary search resolution**: 0.1 dB (configurable)

### Spectrum Analyzer Configuration:
- **Detector**: AVERAGE mode
- **Sweep time**: 10× normal for averaging
- **Reference level**: Auto-adjusted based on signal level
- **Marker**: Used for peak detection and specific frequency measurements
