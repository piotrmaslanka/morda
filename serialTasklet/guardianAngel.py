from threading import Thread
from queue import Queue
import serial
from morda.serialTasklet.modbus import SerialCommunication

class GuardianAngel(Thread):
    """
    Thread that helps serialTasklet carry out it's duties
    """
    
    def __init__(self, serialTasklet, comport):
        Thread.__init__(self)
        self.to_execute = Queue()
        self.tasklet = serialTasklet
        self.serial = serial.Serial(comport, baudrate=9600, parity='N', stopbits=1, timeout=1)
        self.sercom = SerialCommunication(self.serial)
        
    def run(self):
        while True:
            yosMsg = self.to_execute.get()
            command, *the_rest = yosMsg.get()
            
            # clear the serial buffers
            self.serial.setTimeout(0)
            self.serial.read(200)
            self.serial.setTimeout(1)
            
            result = {
             'read-registers': self.sercom.getReg,
             'write-register': self.sercom.setReg,
             'read-flag': self.sercom.getFlag,
             'read-lte': self.sercom.getLTEReg
            }[command](*the_rest)
                
            self.tasklet.on_message_execed(yosMsg, result)