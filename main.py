import socketio
import time
import serial
import threading
import imutils
from imutils.video import VideoStream
from pyzbar import pyzbar
import requests
from utils import threaded
from LightManager import LightManager

class MyxStore:
    def __init__(self, mode, stall_uid):
        """Initializes the Myx Storage System
        
        Arguments:
            mode {string} -- "dev" or "prod"
            stall_uid {string} -- Stall's UID to subscribe to
        """
        # Subscribe to socket server for id "myx"
        # Load what cup is stored where?
        # Load camera thread
        if mode == 'dev':
            self.server_url = "http://10.12.254.221:11235"
            self.socket_url = "http://10.12.254.221:11236"
        else:
            self.server_url = "https://www.myxbrewapi.com"
            self.socket_url = self.server_url
        self.stall_uid = stall_uid
        self.socket_subscribe()
        self.serial_initialize()
        self.busy = False
        self.initialize_camera()
        self.light_manager = LightManager()
        # Available modes: Idle, Depositing, Deposited, Withdrawing, Withdrawed
        self.light_manager.mode = "Idle"
    
    def serial_initialize(self):
        """Initializes the serial comms. On RPI, this is 
        via Pins 14 (TX) and 15 (RX)
        """
        self.ser = serial.Serial(            
            port='/dev/serial0',
            baudrate = 9600,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=1
        )
        self.ser_read()

    @threaded
    def ser_read(self):
        """
        Listens to Arduino status, sets self.busy to false when
        Arduino sends the appropriate message
        """
        while True:
            line = self.ser.readline()
            if 'Done' in line:
                self.busy = False
                if self.light_manager.mode == "Depositing":
                    self.light_manager.mode == "Deposited"
                else:
                    self.light_manager.mode == "Withdrawed"
                time.sleep(5)
                self.light_manager.mode = "Idle"

    def socket_subscribe(self):
        """
        Subscribes to server's socket to listen for orders and shelf instructions
        """
        self.sio = socketio.Client()
        self.sio.connect(self.socket_url)
        self.sio.emit('stall_join', self.stall_uid)
        print("Socket server connected!")

        @self.sio.on('orders')
        def on_message(data):
            print("Order message received!")
            print(data)

        @self.sio.on('shelf')
        def on_message(data):
            print("Shelf message received!")
            print(data)
            self.load_shelf(data["slot"], data["direction"])

    def load_shelf(self, slot, direction):
        """
        Deposit or Withdraw a drink depending on slot.
        If system is currently already in the process of moving a drink, ignore.
        
        Arguments:
            slot {int} -- Slot to/from which to move a drink. 1 to 16.
            direction {int} -- -1 (withdraw), 1 (deposit)
        """
        if slot not in range(1, 17):
            print(f"Invalid slot specified: [{slot}]")
            return False
        if not self.busy:
            slot += 48
            if direction < 0:
                self.light_manager.mode = "Withdrawing"
                slot += 16
            else:
                self.light_manager.mode = "Depositing"
            self.ser.write(chr(slot).encode('UTF-8'))
            self.busy = True
        else:
            print("System busy - load_shelf command rejected")
            
    @threaded
    def initialize_camera(self):
        vs = VideoStream(usePiCamera=True).start()
        time.sleep(2)
        print("Camera initialized!")
        while True:
            frame = vs.read()
            frame = imutils.resize(frame, width=400)
            barcodes = pyzbar.decode(frame)
            if len(barcodes) == 1:
                print(barcodes[0].data)
                res = requests.post(f'{self.server_url}/retrieve', json={'order_id':barcodes[0].data})
                print(res)
            
if __name__ == "__main__":
    print("Starting Myx shelving system backend...")
    test_case = MyxStore('dev', 'ch1ck3n')
    
