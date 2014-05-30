from yzero import Zero
import struct
from morda.settings import ZERO_CONNECT

def get_series(sername, from_, to, callback, zero=None):
    if zero == None: zero = Zero(ZERO_CONNECT)
        
    class Receiver(object):
        def __init__(self, zero, from_, to, callback):
            self.zero = zero
            self.serdef = None
            self.data = []
            self.from_ = from_
            self.to = to
            self.fin_callback = callback
            
        def on_got_serdef(self, serdef):
            self.serdef = serdef
            zero.readSeries(serdef, self.from_, self.to, self.on_got_data, self.on_end)
            
        def on_got_data(self, dat):
            self.data.extend(dat)
            
        def on_end(self, suc):
            deco = lambda x: struct.unpack('d' if self.serdef.recordsize == 8 else 'f', x)[0]
            
            for i in range(0, len(self.data)):
                ts, dat = self.data[i]
                self.data[i] = (ts, deco(dat))
            
            self.fin_callback(self.data)
    
    rec = Receiver(zero, from_, to, callback)
    zero.getDefinition(sername, rec.on_got_serdef)
    
    
    