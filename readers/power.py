from yos.rt import BaseTasklet, NCounter
from yos.ipc import Catalog
from yos.tasklets import Tasklet
from yzero import Zero, WriteAssistant
from yos.time import Timer
import struct, time
from morda.settings import ZERO_CONNECT
from morda.utils import tosgn

class ElectricityReader(BaseTasklet):
    """
    It just queries the power meter,
    stores data into catalog and Zero database
    """
    
    def on_startup(self):
        zero = Zero(ZERO_CONNECT)
        self.w_v1 = WriteAssistant('pwr.phase1.voltage', zero).start()
        self.w_v2 = WriteAssistant('pwr.phase2.voltage', zero).start()
        self.w_v3 = WriteAssistant('pwr.phase3.voltage', zero).start()
        self.w_w1 = WriteAssistant('pwr.phase1.power', zero).start()
        self.w_w2 = WriteAssistant('pwr.phase2.power', zero).start()
        self.w_w3 = WriteAssistant('pwr.phase3.power', zero).start()        
        self.w_pk = WriteAssistant('pwr.wh_counter', zero).start()
        self.w_va1 = WriteAssistant('pwr.phase1.apparent_power', zero).start()
        self.w_va2 = WriteAssistant('pwr.phase2.apparent_power', zero).start()
        self.w_va3 = WriteAssistant('pwr.phase3.apparent_power', zero).start()        
        self.w_var1 = WriteAssistant('pwr.phase1.reactive_power', zero).start()
        self.w_var2 = WriteAssistant('pwr.phase2.reactive_power', zero).start()
        self.w_var3 = WriteAssistant('pwr.phase3.reactive_power', zero).start()        
        
        def on_485_tasklet_open(tlet):
            self.h485 = tlet
            Timer.repeat(60, self.called_each_minute)
            
            # We need to ensure that this gets called on exactly full hour
            seconds_passed_since_fullhour = int(time.time()) % 3600 
            seconds_remaining_to_fullhour = 3600 - seconds_passed_since_fullhour
            
            Timer.schedule(seconds_remaining_to_fullhour, 
                lambda: (self.called_each_hour(), Timer.repeat(3600, self.called_each_hour)))
            
            self.refresh_data()
        
        def on_485_tasklet_id(tid):
            if tid == Catalog.NotFoundError:
                Catalog.get('rs485', on_485_tasklet_id, catname='serials')
            else:
                Tasklet.open(tid, on_485_tasklet_open)
                
        Catalog.get('rs485', on_485_tasklet_id, catname='serials')        
        
        
    def refresh_data(self):
        """Calls as fast as it can :)"""
        # read voltages
        
        def read_voltages(repl):
            if repl == None: return
            l1v, a, l2v, b, l3v = repl
            Catalog.scatter({'pwr.phase1.voltage': tosgn(l1v),
                             'pwr.phase2.voltage': tosgn(l2v),
                             'pwr.phase3.voltage': tosgn(l3v)}, catname='values')

        def read_powers(repl):
            if repl == None: return
            w1, a, w2, b, w3 = repl
            Catalog.scatter({'pwr.phase1.power': tosgn(w1),
                             'pwr.phase2.power': tosgn(w2),
                             'pwr.phase3.power': tosgn(w3)}, catname='values')
            
        def read_kwh(repl):
            if repl == None: return
            Catalog.scatter({'pwr.wh_counter': int(repl)}, catname='values')
        
        def read_apparent_power(repl):
            if repl == None: return
            w1, a, w2, b, w3 = repl
            Catalog.scatter({'pwr.phase1.apparent_power': tosgn(w1),
                             'pwr.phase2.apparent_power': tosgn(w2),
                             'pwr.phase3.apparent_power': tosgn(w3)}, catname='values')
  
        def read_reactive_power(repl):
            if repl == None: return
            w1, a, w2, b, w3 = repl
            Catalog.scatter({'pwr.phase1.reactive_power': tosgn(w1),
                             'pwr.phase2.reactive_power': tosgn(w2),
                             'pwr.phase3.reactive_power': tosgn(w3)}, catname='values')            
    
            
        def read_frequencies(repl):
            if repl == None: return
            h1, a, h2, b, h3 = repl
            Catalog.scatter({'pwr.phase1.frequency': tosgn(h1),
                             'pwr.phase2.frequency': tosgn(h2),
                             'pwr.phase3.frequency': tosgn(h3)}, catname='values')            
            
        nc = NCounter(6, self.refresh_data)
        
        self.h485.send_sync(('read-registers', 31, 1, 5), nc(read_voltages))
        self.h485.send_sync(('read-registers', 31, 19, 5), nc(read_powers))
        self.h485.send_sync(('read-registers', 31, 27, 5), nc(read_apparent_power))
        self.h485.send_sync(('read-registers', 31, 35, 5), nc(read_reactive_power))
        self.h485.send_sync(('read-registers', 31, 51, 5), nc(read_frequencies))
        self.h485.send_sync(('read-lte', 31, 79), nc(read_kwh))
        
        
    def called_each_hour(self):
        # Drop the power counter into DB
        
        def on_gathered(data):
            timestamp = int(time.time())
            try:
                self.w_pk.write(timestamp, struct.pack('d', data['pwr.wh_counter']))
            except struct.error:
                pass
                
        Catalog.gather(['pwr.wh_counter'], on_gathered, catname='values')

    def called_each_minute(self):
        # Aggregate values and DB'em
        
        def on_gathered(data):
            timestamp = int(time.time())
            try:
                self.w_v1.write(timestamp, struct.pack('f', data['pwr.phase1.voltage']))
                self.w_v2.write(timestamp, struct.pack('f', data['pwr.phase2.voltage']))
                self.w_v3.write(timestamp, struct.pack('f', data['pwr.phase3.voltage']))
                self.w_w1.write(timestamp, struct.pack('f', data['pwr.phase1.power']))
                self.w_w2.write(timestamp, struct.pack('f', data['pwr.phase2.power']))
                self.w_w3.write(timestamp, struct.pack('f', data['pwr.phase3.power']))
                self.w_va1.write(timestamp, struct.pack('f', data['pwr.phase1.apparent_power']))
                self.w_va2.write(timestamp, struct.pack('f', data['pwr.phase2.apparent_power']))
                self.w_va3.write(timestamp, struct.pack('f', data['pwr.phase3.apparent_power']))
                self.w_var1.write(timestamp, struct.pack('f', data['pwr.phase1.reactive_power']))
                self.w_var2.write(timestamp, struct.pack('f', data['pwr.phase2.reactive_power']))
                self.w_var3.write(timestamp, struct.pack('f', data['pwr.phase3.reactive_power']))
            except struct.error:
                pass
                    
        Catalog.gather(['pwr.phase1.voltage', 'pwr.phase2.voltage', 'pwr.phase3.voltage', 
                        'pwr.phase1.power', 'pwr.phase2.power', 'pwr.phase3.power',
                        'pwr.phase1.apparent_power', 'pwr.phase2.apparent_power',
                        'pwr.phase3.apparent_power', 'pwr.phase1.reactive_power',
                        'pwr.phase2.reactive_power', 'pwr.phase3.reactive_power'], on_gathered, catname='values')