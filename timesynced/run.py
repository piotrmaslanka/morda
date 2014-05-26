from yos.rt import BaseTasklet
from yos.ipc import Catalog
from yos.time import Timer
from yos.tasklets import Tasklet

class TimesyncedTasklet(BaseTasklet):
    """
    Tasklet whose job is to keep clock synchronized on our devices
    """
    
    def __init__(self):
        BaseTasklet.__init__(self)
        self.rs485_handler = None
        self.rs232_handler = None
    
    def on_startup(self):
        # We need to acquire MODBUS command executors...

        
        def rs232_catalog_handler(tid):
            if tid == Catalog.NotFoundError:
                Catalog.get('rs232', rs232_catalog_handler, catname='serials')
            else:
                def test(rs232_handler):
                    self.rs232_handler = rs232_handler
                    self.post_init_232()
                Tasklet.open(tid, test)
        
        def rs485_catalog_handler(tid):
            if tid == Catalog.NotFoundError:
                Catalog.get('rs485', rs485_catalog_handler, catname='serials')
            else:
                def test(rs485_handler):
                    self.rs485_handler = rs485_handler
                    Timer.create(10, self.show_hour_onPulser)
                Tasklet.open(tid, test)
                
        Catalog.get('rs485', rs485_catalog_handler, catname='serials')
        #Catalog.get('rs232', rs232_catalog_handler, catname='serials')
        
        
    def post_init_232(self):
        self.rs232_handler.send_sync(('read-registers', 2, 4001, 2), lambda response: print(response))        
        
    def show_hour_onPulser(self):
        self.rs485_handler.send_sync(('read-registers', 28, 4001, 2), self.show_hour_onData)
        
    def show_hour_onData(self, time):
        """Called by self when all channel handler were acquired"""
        if time == None:
            self.rs485_handler.send_sync(('read-registers', 28, 4001, 2), self.show_hour_onData)
        else:
            print("Irrigation PLC reports %s:%s" % (time[1], time[0]))
            Timer.create(10, self.show_hour_onPulser)