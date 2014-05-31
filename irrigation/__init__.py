from yos.rt import BaseTasklet, NCounter
from yos.ipc import Catalog
from yos.tasklets import Tasklet
from yos.time import Timer
import struct, time

class IrrigationReader(BaseTasklet):
    """
    It just queries the irrigation PLC
    stores data into catalog and Zero database
    """
    
    def on_startup(self):

        def on_485_tasklet_open(tlet):
            self.h485 = tlet
            self.refresh_data()
        
        def on_485_tasklet_id(tid):
            if tid == Catalog.NotFoundError:
                Catalog.get('rs485', on_485_tasklet_id, catname='serials')
            else:
                Tasklet.open(tid, on_485_tasklet_open)
                
        Catalog.get('rs485', on_485_tasklet_id, catname='serials')        
        
        
    def refresh_data(self):
        """Calls as fast as it can :)"""
        def read_registers(repl):
            if repl == None: return
            dailyCounter, sectionCounter, _, prevDayCounter, visStan, leakDetected, forbidDrop, forbidIrrig = repl
            Catalog.scatter({'irrig.dailyCounter': dailyCounter,
                             'irrig.sectionCounter': sectionCounter,
                             'irrig.visState': visStan,
                             'irrig.prevDayCounter': prevDayCounter,
                             'irrig.leakDetected': leakDetected,
                             'irrig.forbidDrop': forbidDrop,
                             'irrig.forbidIrrig': forbidIrrig}, catname='values')

        nc = NCounter(1, self.refresh_data)
        
        self.h485.send_sync(('read-registers', 28, 4085, 8), nc(read_registers))
    
