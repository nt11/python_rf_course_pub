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
