from serial.serialutil import SerialException
import dpx_func_python as dpx
from serial import SerialException
import serial.tools.list_ports

'''
class Singleton:
    def __init__(self, decorated):
        self._decorated = decorated

    def instance(self):
        try:
            return self._instance
        except AttributeError:
            self._instance = self._decorated()
            return self._instance

    def __call__(self):
        raise TypeError('Singletons must be accessed through `instance()`.')

    def __instancecheck__(self, inst):
        return isinstance(inst, self._decorated)

@Singleton
'''

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
            # Port or baud rate missing
            if (self.port is None) or (self.baud is None):
                return 400

            try:
                self.dpx = dpx.Dosepix(self.port, self.baud, self.config)
                # dpx_func_python.Dosepix(PORT, 2e6, CONFIG_FN, thl_calib_files=thl_calib_files, params_file=PARAMS_FILES, bin_edges_file=BIN_EDGES_FILES)
            except SerialException as err:
                return 503
            return True

    def disconnect(self):
        self.dpx.close()
        self.dpx = None
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
        print(port)
        self.port = port

    def set_config(self, config):
        self.config = config

    # === TOOLS ===
    def get_ports(self):
        self.ports = [comport.device for comport in serial.tools.list_ports.comports()]
        print(self.ports)
        return self.ports

connection_handler = Connection_handler()
