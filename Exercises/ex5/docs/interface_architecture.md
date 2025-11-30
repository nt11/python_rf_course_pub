# Interface Architecture Diagram - Exercise 5

## Overview
This document describes the interfaces between processes, threads, and GUI components in the Filter Response Analyzer application.

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         QApplication (Qt Event Loop)                     │
│                              sys.argv → app.exec()                       │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                    LabNetworkControl (QMainWindow)                       │
│                        Ex5_solution.py:24-241                            │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌─────────────────────┐         ┌──────────────────────────────────┐   │
│  │   GUI Widgets       │         │   Internal State                 │   │
│  │   (network.ui)      │         │                                  │   │
│  ├─────────────────────┤         ├──────────────────────────────────┤   │
│  │ • pushButton        │         │ • self.rm (ResourceManager)      │   │
│  │ • pushButton_2      │         │ • self.sa (VISA Instrument)      │   │
│  │ • lineEdit (IP_SG)  │         │ • self.sg (VISA Instrument)      │   │
│  │ • lineEdit_2 (IP_SA)│         │ • self.scpi_sa (SCPIWrapper)     │   │
│  │ • lineEdit_3-6      │         │ • self.scpi_sg (SCPIWrapper)     │   │
│  │ • progressBar       │         │ • self.f_scan (np.array)         │   │
│  │ • textBrowser (log) │         │ • self.thread (LongProcess)      │   │
│  │ • widget (plot)     │         │ • self.Params (dict from YAML)   │   │
│  └─────────────────────┘         └──────────────────────────────────┘   │
│           │                                    │                         │
│           │ User Actions                       │                         │
│           ▼                                    ▼                         │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │              Callback Functions (Event Handlers)                │    │
│  ├─────────────────────────────────────────────────────────────────┤    │
│  │ • cb_connect()      :78  - Connect/disconnect to instruments    │    │
│  │ • cb_ip_sa()        :128 - Validate SA IP address               │    │
│  │ • cb_ip_sg()        :139 - Validate SG IP address               │    │
│  │ • cb_go()           :163 - Start measurement thread             │    │
│  │ • cb_scan()         :209 - Validate scan parameters             │    │
│  │ • cb_save()         :184 - Save params to YAML                  │    │
│  │ • cb_load()         :194 - Load params from YAML                │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                    │                                     │
│                                    │ cb_go() creates thread              │
│                                    ▼                                     │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │             Thread Callback Functions (Slot Handlers)           │    │
│  ├─────────────────────────────────────────────────────────────────┤    │
│  │ • tcb_progress(i)      :151 - Update progress bar               │    │
│  │ • tcb_plot(freq,power) :155 - Update plot widget                │    │
│  │ • log.info(msg)        :179 - Log messages from thread          │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                          ▲                                              │
└──────────────────────────┼──────────────────────────────────────────────┘
                           │
                           │ Qt Signals (Thread → GUI)
                           │
┌──────────────────────────┴──────────────────────────────────────────────┐
│                   LongProcess (QThread)                                  │
│                   ex5_long_process.py:5-79                               │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    PyQt Signals (Class Attributes)              │    │
│  ├─────────────────────────────────────────────────────────────────┤    │
│  │ • progress = pyqtSignal(int)                        :7          │    │
│  │   └─> Emits percentage complete (0-100)                         │    │
│  │                                                                  │    │
│  │ • data = pyqtSignal(np.ndarray, np.ndarray)         :8          │    │
│  │   └─> Emits (frequency_array, power_array) every 20 points      │    │
│  │                                                                  │    │
│  │ • log = pyqtSignal(str)                             :9          │    │
│  │   └─> Emits log messages as strings                             │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                                                           │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                      Thread Methods                              │    │
│  ├─────────────────────────────────────────────────────────────────┤    │
│  │ • __init__(f_scan, scpi_sa, scpi_sg)  :11                       │    │
│  │   └─> Receives instrument refs from main thread                 │    │
│  │                                                                  │    │
│  │ • run()                                :19                       │    │
│  │   └─> Main thread execution (auto-called by .start())           │    │
│  │   └─> Loop through frequencies, measure, emit signals           │    │
│  │                                                                  │    │
│  │ • stop()                               :77                       │    │
│  │   └─> Sets self.running = False to gracefully stop              │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                    │                                     │
│                                    │ SCPI Commands                       │
│                                    ▼                                     │
└─────────────────────────────────────────────────────────────────────────┘
                                     │
                    ┌────────────────┴─────────────────┐
                    │                                  │
                    ▼                                  ▼
      ┌──────────────────────────┐      ┌──────────────────────────┐
      │  Spectrum Analyzer (SA)  │      │  Signal Generator (SG)   │
      │  VISA/SCPI Interface     │      │  VISA/SCPI Interface     │
      ├──────────────────────────┤      ├──────────────────────────┤
      │ Connection:              │      │ Connection:              │
      │ TCPIP0::{IP}::inst0      │      │ TCPIP0::{IP}::inst0      │
      │                          │      │                          │
      │ Commands Used:           │      │ Commands Used:           │
      │ • *IDN?                  │      │ • *IDN?                  │
      │ • *RST, *CLS             │      │ • *RST, *CLS             │
      │ • SENS:BAND:RES          │      │ • FREQ <value>           │
      │ • SENS:DET AVERage       │      │ • POW:LEV <value>        │
      │ • TRAC:MODE WRITe        │      │ • OUTP:STAT ON/OFF       │
      │ • INIT:CONT OFF          │      │ • OUTP:MOD:STAT OFF      │
      │ • SENS:FREQ:CENT         │      │                          │
      │ • SENS:FREQ:SPAN         │      │                          │
      │ • INIT:IMM               │      │                          │
      │ • *OPC?                  │      │                          │
      │ • CALC:MARK:MAX          │      │                          │
      │ • CALC:MARK:Y?           │      │                          │
      │ • DISP:WIND:TRAC:Y:RLEV  │      │                          │
      └──────────────────────────┘      └──────────────────────────┘
```

## Key Interface Points Explained

### 1. GUI → Main Controller (User Interaction)
- **Interface Type**: Qt Signal/Slot mechanism via `h_gui` dictionary
- **Location**: `Ex5_solution.py:37-47`
- **Data Flow**: User clicks/edits → Qt signals → Callback functions
- **Example**:
  - User clicks "Connect" button → `cb_connect()` triggered
  - User edits IP field → `cb_ip_sa()` or `cb_ip_sg()` triggered

**Code Reference:**
```python
self.h_gui = dict(
    Connect     = h_gui(self.pushButton,   self.cb_connect),
    Go          = h_gui(self.pushButton_2, self.cb_go),
    GoProgress  = h_gui(self.progressBar,  None),
    IP_SG       = h_gui(self.lineEdit,     self.cb_ip_sg),
    IP_SA       = h_gui(self.lineEdit_2,   self.cb_ip_sa),
    # ... etc
)
```

### 2. Main Controller → Thread (Starting Background Work)
- **Interface Type**: Constructor parameters + `.start()` method
- **Location**: `Ex5_solution.py:176-181`
- **Data Flow**:
  1. Create thread instance with shared references
  2. Connect thread signals to main controller slots
  3. Start thread execution

**Code Reference:**
```python
# Create the thread object with instrument references
self.thread = LongProcess(f_scan=self.f_scan,
                          scpi_sa=self.scpi_sa,
                          scpi_sg=self.scpi_sg)

# Connect signals to slot handlers
self.thread.progress.connect(self.tcb_progress)
self.thread.data.connect(self.tcb_plot)
self.thread.log.connect(self.log.info)

# Start thread execution (calls run() method in new thread)
self.thread.start()
```

### 3. Thread → Main Controller (Background Updates)
- **Interface Type**: PyQt Signals (thread-safe communication)
- **Location**: `ex5_long_process.py:7-9`
- **Signal Types**:
  - `progress(int)`: Updates progress bar percentage (0-100)
  - `data(ndarray, ndarray)`: Sends measurement data for plotting
  - `log(str)`: Sends log messages to GUI text browser
- **Thread Safety**: Qt automatically queues signals across threads to ensure GUI updates happen on main thread

**Code Reference:**
```python
class LongProcess(QThread):
    # Define signals as class attributes
    progress = pyqtSignal(int)
    data     = pyqtSignal(np.ndarray, np.ndarray)
    log      = pyqtSignal(str)

    def run(self):
        # ... measurement loop ...
        for i, f in enumerate(self.f_scan):
            # ... do measurement ...

            # Emit signals (thread-safe)
            if i % 20 == 0:
                self.data.emit(freq, power)

            self.progress.emit(100 * (i + 1) // len(self.f_scan))
```

### 4. Main Controller → Instruments (SCPI Communication)
- **Interface Type**: PyVISA + SCPIWrapper
- **Location**: `Ex5_solution.py:85-90`
- **Connection String**: `"TCPIP0::{ip}::inst0::INSTR"`
- **Methods**:
  - `scpi.write(command)`: Send SCPI command to instrument
  - `scpi.query(command)`: Send command and get response

**Code Reference:**
```python
# Open VISA resources
self.sa = self.rm.open_resource(f"TCPIP0::{ip_sa}::inst0::INSTR")
self.sg = self.rm.open_resource(f"TCPIP0::{ip_sg}::inst0::INSTR")

# Wrap in SCPI helper
self.scpi_sa = SCPIWrapper(instr=self.sa, log=self.log, name='SA')
self.scpi_sg = SCPIWrapper(instr=self.sg, log=self.log, name='SG')

# Query instrument
idn = self.scpi_sa.query("*IDN?")
```

### 5. Thread → Instruments (Measurement Loop)
- **Interface Type**: Shared SCPI references (passed via constructor)
- **Location**: `ex5_long_process.py:38-63`
- **Flow**:
  1. Set SG frequency (line 39)
  2. Set SA center frequency (line 41)
  3. Set SA span (line 43)
  4. Trigger measurement (line 45)
  5. Wait for completion using `*OPC?` (line 47)
  6. Read peak value (line 54)
  7. Emit data signal (line 66, 74)

**Code Reference:**
```python
def run(self):
    for i, f in enumerate(self.f_scan):
        # Set Signal Generator frequency
        self.scpi_sg.write(f"freq {f} MHz")

        # Configure Spectrum Analyzer
        self.scpi_sa.write(f"sense:FREQuency:CENTer {f} MHz")
        self.scpi_sa.write(f"sense:FREQuency:SPAN 5 MHz")

        # Trigger and wait for sweep completion
        self.scpi_sa.write("INITiate:IMMediate")
        self.scpi_sa.query("*OPC?")

        # Read measurement
        self.scpi_sa.write("CALCulate:MARKer:MAXimum")
        peak_value = float(self.scpi_sa.query("CALCulate:MARKer:Y?"))

        # Store and emit data
        power = np.append(power, peak_value)
        self.data.emit(freq, power)
```

## Critical Design Patterns

### Thread Safety Mechanisms
1. **PyQt Signals**: Provide thread-safe cross-thread communication
2. **No Direct GUI Access**: Worker thread never calls GUI methods directly
3. **One-Way Data Flow**: Thread emits → Main receives → Main updates GUI
4. **Queued Connections**: Qt automatically queues signals from worker thread to main thread

### Separation of Concerns
1. **Main Thread Responsibilities**:
   - GUI updates and rendering
   - User interaction handling
   - Configuration (YAML I/O)
   - Connection management

2. **Worker Thread Responsibilities**:
   - Instrument control
   - Measurement execution
   - Data collection
   - Progress reporting

3. **Instruments**:
   - Hardware abstraction via SCPI
   - RF signal generation/analysis

### Event-Driven Architecture
```
User Action → Qt Event → Callback → State Change → Signal Emission → Slot Handler → GUI Update
```

**Example Flow:**
1. User clicks "Go" button
2. Qt triggers `cb_go()` callback
3. Callback creates `LongProcess` thread
4. Callback connects signals to slots
5. Callback calls `thread.start()`
6. Thread's `run()` method executes in background
7. Thread emits `progress` signals → `tcb_progress()` updates progress bar
8. Thread emits `data` signals → `tcb_plot()` updates plot
9. Thread emits `log` signals → messages appear in text browser

## Data Flow Summary

### Initialization Phase
```
QApplication → LabNetworkControl.__init__() → Load YAML → Initialize GUI widgets
```

### Connection Phase
```
User clicks Connect → cb_connect() → Open VISA resources → Query *IDN? → Display status
```

### Measurement Phase
```
User clicks Go → cb_go() → Create LongProcess thread →
    Thread.run() loops:
        Set SG freq → Set SA freq → Trigger sweep → Read power →
        Emit progress signal → Emit data signal every 20 points

Main thread receives signals:
    progress → Update progress bar
    data → Update plot
    log → Display messages
```

### Benefits of This Architecture
1. **Responsive GUI**: Long measurements don't freeze the interface
2. **Real-time Feedback**: Progress bar and plot update during measurement
3. **Thread Safety**: Qt signals prevent race conditions
4. **Clean Separation**: Business logic separated from UI logic
5. **Testability**: Each component can be tested independently
6. **Maintainability**: Clear interfaces make code easier to understand and modify

## Important Notes for Students

### Why Use Threads?
Without threading, the measurement loop would block the main thread, freezing the GUI for minutes. The user couldn't cancel, see progress, or interact with the application.

### Why Use Signals Instead of Direct Calls?
```python
# WRONG - Unsafe cross-thread GUI access
def run(self):
    self.progressBar.setValue(50)  # Crashes! GUI access from wrong thread

# CORRECT - Thread-safe signal emission
def run(self):
    self.progress.emit(50)  # Safe! Qt handles thread synchronization
```

### SCPI Communication Pattern
The SCPI commands follow a standard pattern:
- **Configuration**: `SENS:FREQ:CENT`, `POW:LEV`
- **Action**: `INIT:IMM` (trigger measurement)
- **Synchronization**: `*OPC?` (wait for completion)
- **Query**: `CALC:MARK:Y?` (read result)

This ensures measurements complete before reading results.
