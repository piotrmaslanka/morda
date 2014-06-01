from yos.rt import BaseTasklet, NCounter
from yos.ipc import Catalog
from yos.tasklets import Tasklet
from yos.time import Timer
import struct, time
from morda.utils import totmp, tosgn
from yzero import WriteAssistant, Zero
from morda.settings import ZERO_CONNECT

class HeatingReader(BaseTasklet):
    """
    It just queries the heating PLC
    stores data into catalog and Zero database
    """
    
    def on_startup(self):
        zero = Zero(ZERO_CONNECT)
        self.w_external = WriteAssistant('heating.external.temp', zero).start()
        self.w_boiler = WriteAssistant('heating.boiler.temp', zero).start()
        self.w_boiler_ref = WriteAssistant('heating.boiler.ref', zero).start()
        self.w_internal = WriteAssistant('heating.internal.temp', zero).start()
        self.w_internal_ref = WriteAssistant('heating.internal.ref', zero).start()
        self.w_co = WriteAssistant('heating.co.temp', zero).start()
        self.w_co_ref = WriteAssistant('heating.co.ref', zero).start()
        self.w_cwu = WriteAssistant('heating.cwu.temp', zero).start()
        self.w_cwu_ref = WriteAssistant('heating.cwu.ref', zero).start()
        
        
        def on_232_tasklet_open(tlet):
            self.h232 = tlet
            self.refresh_data()
            Timer.repeat(60, self.called_each_minute)
        
        def on_232_tasklet_id(tid):
            if tid == Catalog.NotFoundError:
                Catalog.get('rs232', on_2323_tasklet_id, catname='serials')
            else:
                Tasklet.open(tid, on_232_tasklet_open)
                
        Catalog.get('rs232', on_232_tasklet_id, catname='serials')        
        
        
    def refresh_data(self):
        """Calls as fast as it can :)"""
        def read_temps1(repl):
            if repl == None: return
            cwu_ref, boiler_temp, cwu_measured = repl
            Catalog.scatter({'heating.cwu.ref': totmp(cwu_ref),
                             'heating.cwu.temp': totmp(cwu_measured),
                             'heating.boiler.temp': totmp(boiler_temp)}, catname='values')

        def read_temps2(repl):
            if repl == None: return
            internal_ref, _, co_temp, co_ref, internal_temp = repl
            Catalog.scatter({'heating.internal.ref': totmp(internal_ref),
                             'heating.internal.temp': totmp(internal_temp),
                             'heating.co.temp': totmp(co_temp),
                             'heating.co.ref': totmp(co_ref)}, catname='values')    

        def read_temps3(repl):
            if repl == None: return
            boiler_ref, = repl
            Catalog.store('heating.boiler.ref', totmp(boiler_ref), catname='values')            
            
        def read_external(repl):
            if repl == None: return
            external, = repl
            Catalog.store('heating.external.temp', totmp(external), catname='values')
            
        def read_presets(repl):
            if repl == None: return
            pr_co_day, _, pr_co_night = repl
            Catalog.scatter({'heating.co.preset.day': tosgn(pr_co_day),
                             'heating.co.preset.night': tosgn(pr_co_night)}, catname='values')    
            
        def flag_read_factory(varname):
            def handler(repl):
                if repl == None: return
                Catalog.store(varname, 1 if repl else 0, catname='values')
            return handler
            
        nc = NCounter(9, self.refresh_data)
        
        self.h232.send_sync(('read-registers', 2, 4102, 3), nc(read_temps1))
        self.h232.send_sync(('read-registers', 2, 4132, 5), nc(read_temps2))
        self.h232.send_sync(('read-registers', 2, 4118, 1), nc(read_temps3))
        self.h232.send_sync(('read-registers', 2, 4089, 1), nc(read_external))
        self.h232.send_sync(('read-registers', 2, 4167, 3), nc(read_presets))
        self.h232.send_sync(('read-flag', 2, 7077), nc(flag_read_factory('heating.cwu.circ')))
        self.h232.send_sync(('read-flag', 2, 7078), nc(flag_read_factory('heating.cwu.load')))
        self.h232.send_sync(('read-flag', 2, 7115), nc(flag_read_factory('heating.co.load')))
        self.h232.send_sync(('read-flag', 2, 7129), nc(flag_read_factory('heating.boiler')))

        
    def called_each_minute(self):
        # Aggregate values and DB'em
        
        def on_gathered(data):
            timestamp = int(time.time())
            try:
                self.w_external.write(timestamp, struct.pack('f', data['heating.external.temp']))
                self.w_boiler.write(timestamp, struct.pack('f', data['heating.boiler.temp']))
                self.w_boiler_ref.write(timestamp, struct.pack('f', data['heating.boiler.ref']))
                self.w_internal.write(timestamp, struct.pack('f', data['heating.internal.temp']))
                self.w_internal_ref.write(timestamp, struct.pack('f', data['heating.internal.ref']))
                self.w_co.write(timestamp, struct.pack('f', data['heating.co.temp']))
                self.w_co_ref.write(timestamp, struct.pack('f', data['heating.co.ref']))
                self.w_cwu.write(timestamp, struct.pack('f', data['heating.cwu.temp']))
                self.w_cwu_ref.write(timestamp, struct.pack('f', data['heating.cwu.ref']))
            except struct.error:
                pass
                    
        Catalog.gather(['heating.external.temp', 'heating.boiler.temp', 'heating.boiler.ref', 
                        'heating.internal.temp', 'heating.internal.ref', 
                        'heating.co.temp', 'heating.co.ref',
                        'heating.cwu.temp', 'heating.cwu.ref'], on_gathered, catname='values')        
