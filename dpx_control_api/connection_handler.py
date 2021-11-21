import dpx_func_python
import serial.tools.list_ports

class Connection_handler:
    def __init__(self):
        # Initialize DPX instance as None
        self.dpx = None
        self.port = None
        self.baud = 2e6
        self.config = None
        return

    # === CONNECTION STATE ===
    def connect(self):
        if not self.is_connected():
            if self.port is None:
                return 'Select port first'

            try:
                self.dpx = dpx_func_python.Dosepix(self.port, self.baud, self.config)
                # dpx_func_python.Dosepix(PORT, 2e6, CONFIG_FN, thl_calib_files=thl_calib_files, params_file=PARAMS_FILES, bin_edges_file=BIN_EDGES_FILES)
            except:
                return False
            return True

    def is_connected(self):
        if self.dpx is not None:
            return True
        else:
            return False

    # === SETTINGS ===
    def get_instance(self):
        return self.dpx

    def set_baud(self, baud):
        self.baud = baud

    def set_port(self, port):
        self.port = port

    def set_config(self, config):
        self.config = config

    # === TOOLS ===
    def get_ports(self):
        self.ports = [comport.device for comport in serial.tools.list_ports.comports()]
        print(self.ports)
        return self.ports

connection_handler = Connection_handler();
