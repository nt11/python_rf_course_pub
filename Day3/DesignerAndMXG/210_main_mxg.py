import re
import sys

import pyvisa
import yaml
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.uic import loadUi

from utils.pyqt2python import h_gui


def is_valid_ip(ip:str) -> bool:
    # Regular expression pattern for matching IP address
    ip_pattern = r'^((25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$'
    return re.match(ip_pattern, ip) is not None

# Load the UI file into the Class (LabDemoMxgControl) object
# The UI file (BasicMxgControl.ui) is created using Qt Designer
# The UI file is located in the same directory as this Python script
# The GUI controller clas inherit from QMainWindow object as defined in the ui file
class LabDemoMxgControl(QMainWindow):
    def __init__(self):
        super().__init__()
        # Load the UI file into the Class (LabDemoMxgControl) object
        loadUi("BasicMxgControl.ui", self)

        self.setWindowTitle("MXG Control")

        # Interface of the GUI Widgets to the Python code
        self.h_gui = dict(
            Connect     = h_gui(self.pushButton         , self.cb_connect       ),
            RF_On_Off   = h_gui(self.pushButton_2       , self.cb_rf_on_off     ),
            Mod_On_Off  = h_gui(self.pushButton_3       , self.cb_mod_on_off    ),
            IP          = h_gui(self.lineEdit           , self.cb_ip            ),
            Fc          = h_gui(self.lineEdit_2         , self.cb_fc            ),
            Pout        = h_gui(self.horizontalSlider   , self.cb_pout_slider   ),
            Save        = h_gui(self.actionSave         , self.cb_save          ),
            Load        = h_gui(self.actionLoad         , self.cb_load          ))

        # Create a Resource Manager object
        self.rm         = pyvisa.ResourceManager('@py')
        self.sig_gen    = None

        # Load the configuration/default values from the YAML file
        self.Params     = None
        self.file_name  = "sig_gen_defaults.yaml"
        self.h_gui['Load'].emit() #  self.cb_load

        self.file_name = "last.yaml"
        try:
            self.h_gui['Load'].callback()  # self.cb_load
        except FileNotFoundError:
            print("No last.yaml file found")

        self.h_gui['Save'].emit() #  self.cb_save

    def sig_gen_write(self, cmd:str):
        if self.sig_gen is not None:
            self.sig_gen.write(cmd)

    # Callback function for the Connect button
    # That is a checkable button
    def cb_connect(self):
        if self.sender().isChecked(): # self.h_gui['Connect'].obj.isChecked():
            print("Connect button Checked")
            # Open the connection to the signal generator
            try:
                ip           = self.h_gui['IP'].get_val()
                self.sig_gen = self.rm.open_resource(f"TCPIP0::{ip}::inst0::INSTR")
                print(f"Connected to {ip}")
                # Read the signal generator status and update the GUI (RF On/Off, Modulation On/Off,Pout and Fc)
                # Query RF On/Off mode
                self.sig_gen.write(":OUTPUT:STATE?")
                rf_state    = bool(int(self.sig_gen.read().strip()))
                # Query Modulation On/Off mode
                self.sig_gen.write(":OUTPUT:MOD:STATE?")
                mod_state   = bool(int(self.sig_gen.read().strip()))
                # Query Output Power
                self.sig_gen.write(":POWER?")
                output_power_dbm = float(self.sig_gen.read())
                # Query Frequency
                self.sig_gen.write(":FREQ?")
                fc          = float(self.sig_gen.read()) * 1e-6

                # Update the GUI (no callbacks)
                self.h_gui['RF_On_Off'  ].set_val( rf_state)
                self.h_gui['Mod_On_Off' ].set_val(mod_state)
                self.h_gui['Pout'       ].set_val(output_power_dbm)
                self.h_gui['Fc'         ].set_val(fc)
            except Exception:
                if self.sig_gen is not None:
                    self.sig_gen.close()
                    self.sig_gen = None
                # Clear Button state
                self.sender().setChecked(False)
        else:
            print("Connect button Cleared")
            # Close the connection to the signal generator
            if self.sig_gen is not None:
                self.sig_gen.close()
                self.sig_gen = None

    # Callback function for the RF On/Off button
    # That is a checkable button
    def cb_rf_on_off(self):
        if self.sender().isChecked():
            self.sig_gen_write(":OUTPUT:STATE ON")
            print("RF On")
        else:
            self.sig_gen_write(":OUTPUT:STATE OFF")
            print("RF Off")

    # Callback function for the Modulation On/Off button
    # That is a checkable button
    def cb_mod_on_off(self):
        if self.sender().isChecked():
            self.sig_gen_write(":OUTPUT:MOD:STATE ON")
            print("Modulation On")
        else:
            self.sig_gen_write(":OUTPUT:MOD:STATE OFF")
            print("Modulation Off")

    # Callback function for the IP lineEdit
    def cb_ip(self):
        ip          = self.h_gui['IP'].get_val()
        # Check if the ip is a valid
        if not is_valid_ip(ip):
            print(f"Invalid IP address: {ip}, Resetting to default")
            ip = self.Params["IP"]
            # Set the default value to the GUI object
            self.h_gui['IP'].set_val(ip)

        print(f"IP = {ip}")

    # Callback function for the Fc lineEdit
    def cb_fc(self):
        # Check if the frequency is a valid float number
        try:
            frequency_mhz = self.h_gui['Fc'].get_val()
        except ValueError:
            print(f"Invalid Frequency: Resetting to default")
            frequency_mhz = self.Params["Fc"]
            # Set the default value to the GUI object
            self.h_gui['Fc'].set_val(frequency_mhz)

        self.sig_gen_write(f":FREQuency {frequency_mhz} MHz") # can replace the '} MHz' with '}e6'
        print(f"Fc = {frequency_mhz} MHz")

    def cb_pout_slider( self ):
        val = self.h_gui['Pout'].get_val()
        self.sig_gen_write(f":POWER {val} dBm")

        print(f"Pout = {val} dBm")

    def cb_save(self):
        print("Save")
        # Read the values from the GUI objects and save them to the Params dictionary
        for key, value in self.Params.items():
            if key in self.h_gui:
                self.Params[key] = self.h_gui[key].get_val()

        with open(self.file_name, "w") as f:
            yaml.dump(self.Params, f)

    def cb_load(self):
        print("Load")
        try:
            with open(self.file_name, "r") as f:
                self.Params = yaml.safe_load(f)
        except FileNotFoundError:
            print(f"File not found: {self.file_name}")
            raise

        # Set the default values to the GUI objects
        for key, value in self.Params.items():
            if key in self.h_gui:
                self.h_gui[key].set_val(value, is_callback=True)

        # Additional configuration parameters
        self.h_gui['Pout'].call_widget_method('setMaximum',False,self.Params["PoutMax"])
        self.h_gui['Pout'].call_widget_method('setMinimum',False,self.Params["PoutMin"])

    def closeEvent(self, event):
        print("Exiting the application")
        # Clean up the resources
        # Close the connection to the signal generator
        if self.sig_gen is not None:
            self.sig_gen.close()
        # Close the Resource Manager
        self.rm.close()

if __name__ == "__main__":
    # Initializes the application and prepares it to run a Qt event loop
    #  it is necessary to create an instance of this class before any GUI elements can be created
    app         = QApplication( sys.argv )
    # Create the LabDemoMxgControl object
    controller  = LabDemoMxgControl()
    # Show the GUI
    controller.show()
    # Start the Qt event loop (the sys.exit is for correct exit status to the OS)
    sys.exit(app.exec())
