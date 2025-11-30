# Interface Mechanisms - Signals vs Callbacks

## Overview
This document focuses specifically on the **communication mechanisms** used between different components: GUI events, callbacks, signals, and method calls.

## Interface Mechanism Types

### 1. Qt Signal/Slot Connections (GUI → Main Controller)
### 2. Direct Method Calls (Main → Thread initialization)
### 3. PyQt Signals (Thread → Main Controller)
### 4. Shared Object References (Thread → Instruments)

---

## Detailed Interface Diagram

```
┌───────────────────────────────────────────────────────────────────────┐
│                         MAIN THREAD (Qt Event Loop)                   │
├───────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌──────────────────────────────────────────────────────────────┐     │
│  │                    GUI WIDGETS (network.ui)                   │     │
│  │                                                               │     │
│  │  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐        │     │
│  │  │ pushButton  │  │  lineEdit    │  │ progressBar  │        │     │
│  │  │ (Connect)   │  │  (IP addr)   │  │              │        │     │
│  │  └──────┬──────┘  └──────┬───────┘  └──────▲───────┘        │     │
│  │         │                │                  │                │     │
│  └─────────┼────────────────┼──────────────────┼────────────────┘     │
│            │                │                  │                      │
│            │ ① Qt Signal    │ ① Qt Signal      │ ④ Direct Method     │
│            │ (clicked)      │ (editingFinished)│    Call             │
│            │                │                  │                      │
│            ▼                ▼                  │                      │
│  ┌─────────────────────────────────────────────┼────────────────┐     │
│  │         h_gui Dictionary (Widget Wrappers)  │                │     │
│  │                                             │                │     │
│  │  h_gui['Connect'] ───────┐                 │                │     │
│  │  h_gui['IP_SA']   ───────┤                 │                │     │
│  │  h_gui['GoProgress'] ────┤                 │                │     │
│  │                           │                 │                │     │
│  └───────────────────────────┼─────────────────┼────────────────┘     │
│                              │                 │                      │
│                              │ ② Callback      │                      │
│                              │    Registration │                      │
│                              ▼                 │                      │
│  ┌────────────────────────────────────────────────────────────────┐   │
│  │           CALLBACK FUNCTIONS (Event Handlers)                  │   │
│  │                                                                 │   │
│  │  def cb_connect(self):          ← Registered in h_gui dict    │   │
│  │      if self.sender().isChecked():                            │   │
│  │          # ③ Direct Method Calls to PyVISA                     │   │
│  │          self.sa = self.rm.open_resource(...)                 │   │
│  │          self.scpi_sa = SCPIWrapper(...)                      │   │
│  │                                                                 │   │
│  │  def cb_go(self):                ← Registered in h_gui dict    │   │
│  │      # ③ Direct Method Call - Create Thread                    │   │
│  │      self.thread = LongProcess(...)                           │   │
│  │      # ⑤ Connect Signals to Slots (Signal Registration)        │   │
│  │      self.thread.progress.connect(self.tcb_progress)          │   │
│  │      self.thread.data.connect(self.tcb_plot)                  │   │
│  │      self.thread.log.connect(self.log.info)                   │   │
│  │      # ③ Direct Method Call - Start Thread                     │   │
│  │      self.thread.start()                                       │   │
│  │                                                                 │   │
│  │  def tcb_progress(self, i):      ← Connected to thread signal │   │
│  │      # ④ Direct Method Call to GUI                             │   │
│  │      self.h_gui['GoProgress'].set_val(i) ────────────────────┐│   │
│  │                                                               ││   │
│  │  def tcb_plot(self, freq, power): ← Connected to thread signal││   │
│  │      # ④ Direct Method Call to Plot Widget                    ││   │
│  │      self.plot_sa.plot(...)                                   ││   │
│  │                                                               ││   │
│  └───────────────────────────────────────────────────────────────┘│   │
│                              ▲                                     │   │
│                              │                                     │   │
│                              │ ⑥ PyQt Signal                       │   │
│                              │    (Thread-Safe)                    │   │
│                              │                                     │   │
└──────────────────────────────┼─────────────────────────────────────┼───┘
                               │                                     │
                               │                                     │
┌──────────────────────────────┼─────────────────────────────────────┼───┐
│                    WORKER THREAD (Background)                      │   │
├────────────────────────────────────────────────────────────────────┼───┤
│                                                                     │   │
│  ┌──────────────────────────────────────────────────────────────┐  │   │
│  │              LongProcess (QThread subclass)                   │  │   │
│  │                                                               │  │   │
│  │  ┌────────────────────────────────────────────────────────┐  │  │   │
│  │  │  SIGNAL DEFINITIONS (Class Variables)                  │  │  │   │
│  │  │                                                         │  │  │   │
│  │  │  progress = pyqtSignal(int)         ──────────────────────┼──┘   │
│  │  │  data     = pyqtSignal(np.ndarray, np.ndarray) ────────────┘      │
│  │  │  log      = pyqtSignal(str)                             │  │      │
│  │  │                                                         │  │      │
│  │  │  These are CLASS ATTRIBUTES, not instance variables!   │  │      │
│  │  └────────────────────────────────────────────────────────┘  │      │
│  │                                                               │      │
│  │  ┌────────────────────────────────────────────────────────┐  │      │
│  │  │  INITIALIZATION (__init__)                             │  │      │
│  │  │                                                         │  │      │
│  │  │  def __init__(self, f_scan, scpi_sa, scpi_sg):        │  │      │
│  │  │      super().__init__()                                │  │      │
│  │  │      # ⑦ Store References (Shared Memory)              │  │      │
│  │  │      self.f_scan  = f_scan                             │  │      │
│  │  │      self.scpi_sa = scpi_sa  ← Shared reference!       │  │      │
│  │  │      self.scpi_sg = scpi_sg  ← Shared reference!       │  │      │
│  │  │                                                         │  │      │
│  │  └────────────────────────────────────────────────────────┘  │      │
│  │                                                               │      │
│  │  ┌────────────────────────────────────────────────────────┐  │      │
│  │  │  THREAD EXECUTION (run method)                         │  │      │
│  │  │                                                         │  │      │
│  │  │  def run(self):                                        │  │      │
│  │  │      for i, f in enumerate(self.f_scan):              │  │      │
│  │  │          # ⑧ Direct Method Call (via shared ref)       │  │      │
│  │  │          self.scpi_sg.write(f"freq {f} MHz")          │  │      │
│  │  │          self.scpi_sa.write(f"sense:FREQ:CENT...")     │  │      │
│  │  │          self.scpi_sa.write("INIT:IMM")                │  │      │
│  │  │          self.scpi_sa.query("*OPC?")                   │  │      │
│  │  │          peak = float(self.scpi_sa.query(...))         │  │      │
│  │  │                                                         │  │      │
│  │  │          # ⑥ Emit Signal (Thread → Main)               │  │      │
│  │  │          self.progress.emit(100 * i // len(...))   ────┼──┘      │
│  │  │          self.data.emit(freq, power)                   │         │
│  │  │          self.log.emit("Thread: message")              │         │
│  │  │                                                         │         │
│  │  └────────────────────────────────────────────────────────┘         │
│  │                                                                      │
│  └──────────────────────────────────────────────────────────────────┘  │
│                               │                                         │
│                               │ ⑧ SCPI Commands                         │
│                               │    (via shared VISA resources)          │
│                               ▼                                         │
└───────────────────────────────────────────────────────────────────────┘
                                │
                   ┌────────────┴───────────────┐
                   │                            │
                   ▼                            ▼
      ┌────────────────────────┐   ┌────────────────────────┐
      │  Spectrum Analyzer     │   │  Signal Generator      │
      │  (SA - VISA Resource)  │   │  (SG - VISA Resource)  │
      │                        │   │                        │
      │  ⑧ SCPI over TCP/IP    │   │  ⑧ SCPI over TCP/IP    │
      │     (Synchronous)      │   │     (Synchronous)      │
      └────────────────────────┘   └────────────────────────┘
```

---

## Interface Mechanisms Breakdown

### ① Qt Built-in Signals (GUI Event → h_gui wrapper)

**Mechanism**: Qt's native signal/slot system (C++ based)

**Characteristics**:
- Automatically emitted by Qt widgets on user interaction
- Type-safe connections
- Runs in the main thread

**Example**:
```python
# When user clicks button, Qt emits 'clicked' signal
pushButton.clicked → connected internally by h_gui wrapper
```

**Code Location**: `Ex5_solution.py:38`
```python
Connect = h_gui(self.pushButton, self.cb_connect)
#              ^^^^^^^^^^^^^^^^  ^^^^^^^^^^^^^^
#              Widget object     Callback function
#
# h_gui class internally does:
# self.pushButton.clicked.connect(self.cb_connect)
```

---

### ② Callback Registration (h_gui wrapper → User callback)

**Mechanism**: Function reference stored in dictionary

**Characteristics**:
- Direct Python function call
- Synchronous execution
- Runs in the same thread (main thread)

**Data Flow**:
```
h_gui dict stores: Widget → Callback mapping
When Qt signal fires → h_gui calls registered callback
```

**Example**:
```python
self.h_gui = dict(
    Connect = h_gui(self.pushButton, self.cb_connect),
    #                                ^^^^^^^^^^^^^^
    #                                This function reference is stored
)

# Later, when button clicked:
# Qt Signal → h_gui wrapper → self.cb_connect()
```

---

### ③ Direct Method Calls (Callback → Objects)

**Mechanism**: Standard Python method invocation

**Characteristics**:
- Synchronous, blocking calls
- Same thread execution
- Immediate execution

**Examples**:

**A. Opening VISA connection** (`Ex5_solution.py:85-90`)
```python
def cb_connect(self):
    # Direct call to PyVISA
    self.sa = self.rm.open_resource(f"TCPIP0::{ip_sa}::inst0::INSTR")
    #         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    #         Synchronous method call - blocks until connection established
```

**B. Creating thread** (`Ex5_solution.py:176`)
```python
def cb_go(self):
    # Direct constructor call
    self.thread = LongProcess(f_scan=self.f_scan, scpi_sa=self.scpi_sa, ...)
    #             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
    #             Synchronous call - returns immediately after object created
```

**C. Starting thread** (`Ex5_solution.py:181`)
```python
    self.thread.start()
    #           ^^^^^^^
    #           Method call that spawns new thread and returns immediately
```

---

### ④ Direct Method Calls (Slot → GUI update)

**Mechanism**: Standard Python method invocation (but must be on main thread!)

**Characteristics**:
- Synchronous execution
- **Must run on main thread** for GUI updates
- Qt ensures these run on main thread via signal/slot mechanism

**Example** (`Ex5_solution.py:151-152`):
```python
def tcb_progress(self, i):
    # This function is called by Qt on the main thread
    # because it's connected via signal/slot
    self.h_gui['GoProgress'].set_val(i)
    #                        ^^^^^^^^^
    #                        Direct method call to update GUI
    #                        (Safe because we're on main thread)
```

**Why this works**:
```
Worker Thread:  self.progress.emit(50)  ← Emits signal
                          ↓
Qt Event System: [Queues signal to main thread]
                          ↓
Main Thread:    tcb_progress(50)        ← Slot called here
                self.progressBar.setValue(50) ← GUI update safe!
```

---

### ⑤ Signal/Slot Connection (Registration phase)

**Mechanism**: Qt's connect() method - registers signal-to-slot mapping

**Characteristics**:
- Done once during initialization
- Creates a binding between signal emitter and slot receiver
- Can be many-to-many (one signal → multiple slots)

**Example** (`Ex5_solution.py:177-179`):
```python
# Registration phase (runs in main thread, before thread starts)
self.thread.progress.connect(self.tcb_progress)
#           ^^^^^^^^         ^^^^^^^^^^^^^^^^
#           Signal           Slot function
#
# This creates a connection:
# "When thread emits 'progress' signal, call 'tcb_progress'"

self.thread.data.connect(self.tcb_plot)
self.thread.log.connect(self.log.info)
```

**What happens internally**:
```python
# Qt maintains a table:
# Signal Object              → Slots to call
# ─────────────────────────────────────────────
# self.thread.progress       → [self.tcb_progress]
# self.thread.data           → [self.tcb_plot]
# self.thread.log            → [self.log.info]
```

---

### ⑥ PyQt Signal Emission (Thread → Main Controller)

**Mechanism**: Thread-safe signal emission via Qt's meta-object system

**Characteristics**:
- **Thread-safe** - The key feature!
- **Asynchronous** - emit() returns immediately
- **Queued connection** - Signal queued to main thread's event loop
- **Type-safe** - Signal signature must match slot signature

**Example** (`ex5_long_process.py:69, 66, 22`):
```python
# In worker thread's run() method:
def run(self):
    for i, f in enumerate(self.f_scan):
        # ... do measurement ...

        # Emit signals (returns immediately, doesn't block)
        self.progress.emit(100 * (i + 1) // len(self.f_scan))
        #            ^^^^
        #            Thread-safe call that queues signal to main thread

        if i % 20 == 0:
            self.data.emit(freq, power)
            #        ^^^^
            #        Sends data arrays to main thread

        self.log.emit(f"Thread: Processing {f} MHz")
        #       ^^^^
        #       Sends log message to main thread
```

**Signal Definitions** (`ex5_long_process.py:7-9`):
```python
class LongProcess(QThread):
    # These are CLASS ATTRIBUTES (shared by all instances)
    progress = pyqtSignal(int)
    #          ^^^^^^^^^^^
    #          Defines signal with one integer parameter

    data = pyqtSignal(np.ndarray, np.ndarray)
    #      ^^^^^^^^^^^
    #      Defines signal with two numpy array parameters

    log = pyqtSignal(str)
    #     ^^^^^^^^^^^
    #     Defines signal with one string parameter
```

**Threading Diagram**:
```
Worker Thread                       Qt Event System              Main Thread
─────────────────                   ─────────────────            ─────────────
run() executes:
  │
  ├─ progress.emit(50) ──────────→ [Queue event] ──────────→ tcb_progress(50)
  │                                                          progressBar.setValue(50)
  │
  ├─ data.emit(f, p) ────────────→ [Queue event] ──────────→ tcb_plot(f, p)
  │                                                          plot_sa.plot(...)
  │
  └─ log.emit("msg") ────────────→ [Queue event] ──────────→ log.info("msg")
                                                             textBrowser.append(...)
```

---

### ⑦ Shared Object References (Main → Thread)

**Mechanism**: Python object references passed via constructor

**Characteristics**:
- Both threads hold references to the same objects
- **Not thread-safe by default** (depends on object implementation)
- VISA library handles internal thread safety
- Arrays are passed by reference (shallow copy)

**Example** (`Ex5_solution.py:176`):
```python
# Main thread creates thread and passes references
self.thread = LongProcess(
    f_scan=self.f_scan,      # ← Numpy array reference
    scpi_sa=self.scpi_sa,    # ← SCPI wrapper object reference
    scpi_sg=self.scpi_sg     # ← SCPI wrapper object reference
)
```

**Worker thread stores references** (`ex5_long_process.py:11-15`):
```python
def __init__(self, f_scan, scpi_sa, scpi_sg):
    super().__init__()
    self.f_scan = f_scan        # ← Same array object as main thread
    self.scpi_sa = scpi_sa      # ← Same SCPI object as main thread
    self.scpi_sg = scpi_sg      # ← Same SCPI object as main thread
```

**Memory Diagram**:
```
Main Thread Memory              Shared Heap                Worker Thread Memory
──────────────────              ───────────                ────────────────────
self.f_scan ──────────────────→ [np.array]  ←────────────── self.f_scan
                                   object

self.scpi_sa ─────────────────→ [SCPIWrapper] ←──────────── self.scpi_sa
                                    object

self.scpi_sg ─────────────────→ [SCPIWrapper] ←──────────── self.scpi_sg
                                    object
```

**Safety Note**:
- This works because VISA resources are internally thread-safe
- If objects weren't thread-safe, this would cause race conditions!
- Numpy arrays are read-only in worker thread, so safe

---

### ⑧ SCPI Commands (Thread → Instruments)

**Mechanism**: Synchronous network I/O via PyVISA over TCP/IP

**Characteristics**:
- **Blocking I/O** - Thread waits for response
- **Synchronous** - Commands executed sequentially
- Network protocol: SCPI over raw TCP or VXI-11
- Thread-safe (VISA handles locking)

**Example** (`ex5_long_process.py:39-54`):
```python
# Set Signal Generator frequency (WRITE command)
self.scpi_sg.write(f"freq {f} MHz")
#            ^^^^^
#            Sends command, waits for acknowledgment, returns
#            Blocks for ~1-10ms

# Set Spectrum Analyzer center frequency (WRITE command)
self.scpi_sa.write(f"sense:FREQuency:CENTer {f} MHz")

# Trigger measurement (WRITE command)
self.scpi_sa.write("INITiate:IMMediate")

# Wait for completion (QUERY command - blocks until sweep done)
self.scpi_sa.query("*OPC?")
#            ^^^^^
#            Sends command, waits for response "1\n"
#            Blocks for ~100ms to several seconds!

# Read measurement (QUERY command)
peak_value = float(self.scpi_sa.query("CALCulate:MARKer:Y?"))
#                              ^^^^^
#                              Sends query, waits for response like "-23.45\n"
#                              Blocks for ~10-50ms
```

**Network Stack**:
```
Python Code                     PyVISA Layer              Network              Instrument
───────────                     ────────────              ─────────            ──────────
scpi.write("FREQ 1000 MHz")
         │
         ├──→ Format SCPI command
         │
         └──→ visa.write() ────────────→ TCP/IP ─────────→ Parse command
                                         socket           Execute command
                                                          Send ACK
                                         ←─────────────── (implicit)
         ←──────────────────────────────────────────────

scpi.query("*OPC?")
         │
         ├──→ Format SCPI query
         │
         └──→ visa.query() ────────────→ TCP/IP ─────────→ Execute command
                                         socket           Wait for completion
                                                          Send response "1\n"
                                         ←─────────────── "1\n"
         ←──────────────────────────────────────────────
         │
         └──→ Parse response, return "1"
```

---

## Communication Pattern Summary

### Synchronous vs Asynchronous

| Mechanism | Type | Blocking? | Thread-Safe? | Use Case |
|-----------|------|-----------|--------------|----------|
| ① Qt Signal (GUI) | Sync | No (queued to event loop) | Yes | User interaction |
| ② Callback | Sync | Yes | N/A (same thread) | Event handling |
| ③ Direct Method Call | Sync | Yes | Depends on object | Object manipulation |
| ④ GUI Update | Sync | Yes | Yes (Qt ensures main thread) | Update display |
| ⑤ connect() | Sync | Yes (just registration) | Yes | Setup signal routing |
| ⑥ PyQt Signal (Thread) | **Async** | **No** (emit returns immediately) | **Yes** | Cross-thread communication |
| ⑦ Shared Reference | N/A | N/A | Depends on object | Share data/resources |
| ⑧ SCPI Command | Sync | **Yes** (waits for response) | Yes (VISA internal) | Instrument control |

### Thread Boundaries

```
         MAIN THREAD                    │         WORKER THREAD
                                        │
   User clicks button                   │
          │                             │
          ▼                             │
   ① Qt Signal                          │
          │                             │
          ▼                             │
   ② Callback (cb_go)                   │
          │                             │
          ├─ ③ Create thread            │
          ├─ ⑤ Connect signals          │
          └─ ③ Start thread ────────────┼─────→ run() starts
                                        │           │
   ⑥ Slot called ←──────────────────────┼───────────┤
   (tcb_progress)    PyQt Signal        │           │
          │           (Thread-safe!)    │           ├─ ⑧ SCPI commands
          ▼                             │           │   (Blocking)
   ④ Update GUI                         │           │
   (progressBar)                        │           └─ ⑥ Emit signals
                                        │              (Non-blocking)
```

---

## Key Takeaways for Students

### 1. Why PyQt Signals for Threading?
**Problem**: Direct GUI access from worker thread crashes:
```python
# WRONG - Will crash!
def run(self):
    self.progressBar.setValue(50)  # GUI access from wrong thread!
```

**Solution**: Emit signal instead:
```python
# CORRECT - Thread-safe
def run(self):
    self.progress.emit(50)  # Qt queues this to main thread
```

### 2. Blocking vs Non-Blocking

**Blocking (Bad in Main Thread)**:
```python
# This would freeze GUI for minutes!
def cb_go_BAD(self):
    for f in freq_array:
        scpi.write(f"FREQ {f}")  # Blocks for 10ms
        scpi.query("*OPC?")       # Blocks for 2 seconds
        # Repeat 100 times = 200+ seconds of frozen GUI!
```

**Non-Blocking (Good - Use Thread)**:
```python
# This returns immediately, GUI stays responsive
def cb_go_GOOD(self):
    self.thread = LongProcess(...)
    self.thread.start()  # Returns immediately!
    # GUI can still respond to user while thread works
```

### 3. Signal Emission is Fast

```python
# In worker thread - these are FAST (< 1 microsecond each)
self.progress.emit(50)           # Queues event, returns instantly
self.data.emit(freq_array, pwr)  # Even with large arrays!
self.log.emit("Message")         # Returns immediately

# Meanwhile, SCPI is SLOW (milliseconds to seconds)
scpi.query("*OPC?")  # Blocks for 100ms to 10 seconds!
```

### 4. One-Way Communication

```
Main Thread ─────────────────→ Worker Thread
            (Constructor args)

Main Thread ←───────────────── Worker Thread
            (PyQt Signals only!)
```

**You cannot**:
- Call worker thread methods from main thread (except `start()`, `stop()`)
- Access main thread objects from worker thread (except via signals)

**You can**:
- Pass data to worker via constructor
- Get data back via signals
- Share thread-safe objects (like VISA resources)

### 5. Signal Type Safety

```python
# Signal definition
progress = pyqtSignal(int)
#                    ^^^
#                    Must be int!

# Slot definition
def tcb_progress(self, i):
#                     ^^^
#                     Must accept int parameter!

# Connection
self.thread.progress.connect(self.tcb_progress)
# Qt verifies types match at connection time
```

---

## Complete Example Flow

### User clicks "Go" button:

```
Step 1: Qt emits clicked signal
        pushButton_2.clicked [Qt Signal] ──────────────┐
                                                        ▼
Step 2: h_gui wrapper receives signal and calls callback
        h_gui['Go'].callback() ──────────────→ cb_go()
                                                    │
Step 3: cb_go() creates and configures thread     │
        │                                           │
        ├─ self.thread = LongProcess(...)  ←───────┘
        │  [Direct Method Call - Constructor]
        │
        ├─ self.thread.progress.connect(self.tcb_progress)
        │  [Signal/Slot Registration]
        │
        ├─ self.thread.data.connect(self.tcb_plot)
        │  [Signal/Slot Registration]
        │
        └─ self.thread.start()
           [Direct Method Call - Start Thread] ────────────────┐
                                                                │
                                                                ▼
           ┌────────────────────────────────────────────────────────┐
           │              WORKER THREAD STARTS                      │
           │                                                        │
           │  run() executes:                                       │
           │    for i, f in enumerate(self.f_scan):                │
           │        self.scpi_sg.write(f"FREQ {f}")                │
           │        [Direct Method Call via Shared Reference]      │
           │        [Blocks ~10ms]                                  │
           │                                                        │
           │        self.scpi_sa.query("*OPC?")                     │
           │        [Direct Method Call via Shared Reference]      │
           │        [Blocks ~2000ms waiting for sweep]             │
           │                                                        │
           │        peak = self.scpi_sa.query("CALC:MARK:Y?")      │
           │        [Blocks ~20ms]                                  │
           │                                                        │
           │        self.progress.emit(percentage)                  │
           │        [PyQt Signal - Returns immediately] ────────┐  │
           │                                                     │  │
           │        self.data.emit(freq, power)                  │  │
           │        [PyQt Signal - Returns immediately] ────────┤  │
           │                                                     │  │
           └─────────────────────────────────────────────────────┼──┘
                                                                 │
                ┌────────────────────────────────────────────────┘
                │ Qt Event System queues signals to main thread
                │
                ▼
        ┌───────────────────────────────────────────────┐
        │          MAIN THREAD EVENT LOOP               │
        │                                               │
        │  tcb_progress(percentage) called              │
        │    │                                          │
        │    └─→ self.h_gui['GoProgress'].set_val(...)  │
        │        [Direct Method Call to update GUI]     │
        │        progressBar.setValue(percentage)       │
        │                                               │
        │  tcb_plot(freq, power) called                 │
        │    │                                          │
        │    └─→ self.plot_sa.plot(freq, power)         │
        │        [Direct Method Call to update plot]    │
        │                                               │
        └───────────────────────────────────────────────┘
```

This complete flow shows all interface mechanisms working together!
