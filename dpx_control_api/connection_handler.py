from serial import SerialException
import serial.tools.list_ports

from . import SINGLE_HW
if SINGLE_HW:
    import dpx_control_hw as dpx
else:
    import dpx_control as dpx

class Connection_handler:
    def __init__(self):
        # Initialize DPX instance as None
        self.dpx = None
        self.port = None
        self.baud = 2e6
        self.config = None

    # === CONNECTION STATE ===
    def connect(self):
        if not self.is_connected():
            # Port or baud rate missing
            if (self.port is None) or\
                (SINGLE_HW and (self.baud is None)):
                return 400

            try:
                if SINGLE_HW:
                    self.dpx = dpx.Dosepix(
                        port_name=self.port,
                        config_fn=self.config
                    )
                else:
                    self.dpx = dpx.Dosepix(
                        self.port,
                        self.baud,
                        self.config
                    )
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
