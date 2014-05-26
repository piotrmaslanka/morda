import struct
from datetime import datetime
# ----------------------------------- MODBUS

class ModbusManager(object):
    def __init__(self):
        lst = []
        i = 0
        while (i<256):
            data = i<<1
            crc = 0
            j = 8
            while (j>0):
                data >>= 1
                if ((data^crc)&0x1):
                    crc = (crc>>1) ^ 0xA001
                else:
                    crc >>= 1
                j -= 1
            lst.append (crc)
            i += 1
        self.table = lst           
    def cCRC(self,st: bytes) -> bytes:
        crc = 0xFFFF
        for ch in st:
            crc = (crc>>8)^self.table[(crc^ch)&0xFF]
        return struct.pack('<H',crc)
    def getReadFlag(self, address: int, flag: int) -> bytes:
        flag = flag & 0xFFF8
        msg = struct.pack('>BBHH', address, 1, flag, 8)
        return msg + self.cCRC(msg)
    def parseReadFlag(self, msg, flag):
        data = msg[3]
        bflag = flag & 0xFFF8
        while (bflag != flag):
            data = data >> 1
            bflag = bflag+1
        return data & 1
    def getReadQuery(self, address, register, amount=1):
        msg = struct.pack('>BBHH', address, 3, register, amount)
        return msg + self.cCRC(msg)
    def getWriteQuery(self, address, register, value):
        msg = struct.pack('>BBHH', address, 6, register, value)
        return msg + self.cCRC(msg)
    def getWriteFlagQuery(self, address, flag, value):
        msg = struct.pack('>BBHH', address, 5, flag, 0xFF00 if value else 0x0000)
        return msg + self.cCRC(msg)
        
    def getReadInputLTEQuery(self, address, register):
        msg = struct.pack('>BBHH', address, 4, register, 2)
        return msg + self.cCRC(msg)        
    def parseReadRequest(self, msg, amount=1):
        lst = []
        for x in range(0, amount):
            lst.append(msg[3+x*2] * 256 + msg[4+x*2])
        return lst
    def parseReadInputLTERequest(self, msg):
        return msg[3] * 256 + msg[4], msg[5] * 256 + msg[6]
    def validate(self, msg):
        crc = msg[-2:]
        precrc = msg[:-2]
        return self.cCRC(precrc) == crc

class SerialCommunication(object):
    def __init__(self, serport):
        self.mm = ModbusManager()
        self.serport = serport
        
    def getFlag(self, a: int, r: int):
        mmr = self.mm.getReadFlag(a, r)
        self.serport.flushInput()
        self.serport.flushOutput()
        self.serport.write(mmr)
        msg = self.serport.read(6)
        if self.mm.validate(msg) and (msg[0] == a):
            msg = self.mm.parseReadFlag(msg, r)
            return bool(msg)
        else:
            return None
        
    def getReg(self, a, r, amount=1):
        mmr = self.mm.getReadQuery(a, r, amount)
        self.serport.flushInput()
        self.serport.flushOutput()
        print(mmr)
        self.serport.write(mmr)
        msg = self.serport.read(5+amount*2)
        if self.mm.validate(msg):
            msg = self.mm.parseReadRequest(msg, amount)
            return msg
        else:
            print("Validation failed, received ",msg)
            return None

    def getLTEReg(self, a, r):
        mmr = self.mm.getReadInputLTEQuery(a, r)
        self.serport.flushInput()
        self.serport.flushOutput()
        self.serport.write(mmr)
        msg = self.serport.read(9)
        if self.mm.validate(msg):
            a, b = self.mm.parseReadInputLTERequest(msg)
            lte = a * 65536 + b
        
            dbl, = struct.unpack('f',struct.pack('<L',lte))
        
            return dbl
        else:
            return None

    def setReg(self, a, r, v):
        self.serport.flushInput()
        self.serport.flushOutput()
        self.serport.write(self.mm.getWriteQuery(a, r, v))
        msg = self.serport.read(8)        
        if self.mm.validate(msg) and (msg[0] == a):
            return True
        else:
            return False
