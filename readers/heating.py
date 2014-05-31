from yos.rt import BaseTasklet, NCounter
from yos.ipc import Catalog
from yos.tasklets import Tasklet
from yos.time import Timer
import struct, time
from morda.utils import totmp, tosgn

class HeatingReader(BaseTasklet):
    """
    It just queries the heating PLC
    stores data into catalog and Zero database
    """
    
    def on_startup(self):

        def on_232_tasklet_open(tlet):
            self.h232 = tlet
            self.refresh_data()
        
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
            
        def read_external(repl):
            if repl == None: return
            external, = repl
            Catalog.store('heating.external', totmp(external), catname='values')
            
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
            
        nc = NCounter(8, self.refresh_data)
        
        self.h232.send_sync(('read-registers', 2, 4102, 3), nc(read_temps1))
        self.h232.send_sync(('read-registers', 2, 4132, 5), nc(read_temps2))
        self.h232.send_sync(('read-registers', 2, 4089, 1), nc(read_external))
        self.h232.send_sync(('read-registers', 2, 4167, 3), nc(read_presets))
        self.h232.send_sync(('read-flag', 2, 7077), nc(flag_read_factory('heating.cwu.circ')))
        self.h232.send_sync(('read-flag', 2, 7078), nc(flag_read_factory('heating.cwu.load')))
        self.h232.send_sync(('read-flag', 2, 7115), nc(flag_read_factory('heating.co.load')))
        self.h232.send_sync(('read-flag', 2, 7129), nc(flag_read_factory('heating.boiler')))
