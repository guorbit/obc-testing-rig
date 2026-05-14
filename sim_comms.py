"""
E32 LoRa Module Simulator running on Pi Pico
Implements actual E32 protocol on the Pi Pico acting as the hardware device
"""

from machine import UART, Pin
from time import ticks_ms

# E32 Protocol constants
E32_UART_PORT = 0  # UART0 on Pi Pico (GP0=TX, GP1=RX)
E32_BAUD_RATE = 9600

# CFG Pin to control mode (attach to microcontroller's PC6)
CFG_PIN = Pin(20, Pin.IN)  # GP20 as input to detect CFG state

# E32 Command frame structure
CMD_READ_CONFIG = 0x02
CMD_WRITE_CONFIG = 0x01
CMD_READ_VERSION = 0x03

# Configuration bytes (8 bytes total in E32)
CONFIG_SIZE = 8

class E32Simulator:
    """Simulates the E32 LoRa module hardware"""
    
    def __init__(self, uart_id=0, baud_rate=9600, cfg_pin=20):
        self.uart = UART(uart_id, baud_rate, tx=Pin(0), rx=Pin(1))
        self.cfg_pin = cfg_pin
        
        # E32 configuration (stored as bytes)
        # Structure: [HEAD, ADDH, ADDL, SPED, CHAN, OPTION(2), CRYPT(2)]
        self.config = bytearray([
            0xC1,        # HEAD (0)
            0x00,        # ADDH (1)
            0x00,        # ADDL (2)
            0x1A,        # SPED: baud=9600, parity=8N1, air_rate=2.4k (3)
            0x00,        # CHAN: channel 0 (4)
            0xC3,        # OPTION: fixed tx, io push-pull, wake 250ms (5)
            0xC0,        # OPTION: FEC on, TX power default (6)
            0x00,        # CRYPT_H (7)
        ])
        
        self.mode = "NORMAL"  # Will update based on CFG pin
        self.received_count = 0
        print("[E32] Simulator initialized on UART{} @ {} baud".format(uart_id, baud_rate))
    
    def check_mode(self):
        """Check CFG pin and update mode"""
        try:
            cfg_state = Pin(self.cfg_pin, Pin.IN).value()
            if cfg_state == 1:  # CFG high = CONFIG mode
                old_mode = self.mode
                self.mode = "CONFIG"
                if old_mode != "CONFIG":
                    print("[E32] Switched to CONFIG mode")
            else:  # CFG low = NORMAL mode
                old_mode = self.mode
                self.mode = "NORMAL"
                if old_mode != "NORMAL":
                    print("[E32] Switched to NORMAL mode")
        except:
            pass
    
    def process_frame(self, frame):
        """Process incoming command frame and send response"""
        if len(frame) < 3:
            # If less than 3 bytes, check if it's data in NORMAL mode
            if self.mode == "NORMAL" and len(frame) > 0:
                print("[E32] Received {} bytes of data: {}".format(len(frame), ''.join(chr(b) for b in frame)))
            return
        
        hdr = frame[0]
        
        # Check if it's a command frame
        if hdr == 0xC1:
            cmd = frame[1]
            length = frame[2]
            
            if cmd == CMD_READ_CONFIG:  # Read configuration
                print("[E32] Read config command")
                response = bytes([0xC1, 0x00]) + self.config
                self.uart.write(response)
                print("[E32] Sent config response ({} bytes)".format(len(response)))
            
            elif cmd == CMD_WRITE_CONFIG:  # Write configuration
                print("[E32] Write config command")
                if len(frame) >= 3 + CONFIG_SIZE:
                    # Update config from frame
                    self.config = bytearray(frame[3:3+CONFIG_SIZE])
                    print("[E32] Config updated")
                
                # Send acknowledgment
                response = bytes([0xC1, 0x00])
                self.uart.write(response)
                print("[E32] Sent write ack response")
            
            elif cmd == CMD_READ_VERSION:  # Read version/model
                print("[E32] Read version command")
                response = bytes([0xC1, 0x00, 0x03, 0xC3, 0x00, 0x80])  # Model info
                self.uart.write(response)
                print("[E32] Sent version response")
            
            else:
                print("[E32] Unknown command: 0x{:02X}".format(cmd))
        
        else:
            # Not a command frame, treat as data in NORMAL mode
            if self.mode == "NORMAL":
                print("[E32] Received {} bytes of data: {}".format(len(frame), ''.join(chr(b) for b in frame)))
            else:
                print("[E32] Invalid header in CONFIG mode: 0x{:02X}".format(hdr))
    
    def poll(self):
        """Poll UART for incoming data"""
        print("[E32] Polling for data...")
        self.check_mode()
        
        if self.uart.any():
            data = self.uart.read()
            if data:
                self.received_count += 1
                self.process_frame(data)

# Global simulator instance
simulator = None

def initComms():
    """Initialize the E32 simulator"""
    global simulator
    simulator = E32Simulator(uart_id=0, baud_rate=9600, cfg_pin=20)
    print("E32 simulator initialized.")

def pollComms():
    """Poll the E32 simulator"""
    global simulator
    if simulator:
        simulator.poll()

def sendMessage(message):
    """Send raw message through E32 (for testing)"""
    global simulator
    if simulator:
        simulator.uart.write(message)
        print("[HOST] Sent message: {}".format(message))
