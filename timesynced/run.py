from yos.rt import BaseTasklet
from yos.ipc import Catalog
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
                    self.post_init_485()
                Tasklet.open(tid, test)
                
        Catalog.get('rs485', rs485_catalog_handler, catname='serials')
        #Catalog.get('rs232', rs232_catalog_handler, catname='serials')
        
        
    def post_init_232(self):
        self.rs232_handler.send_sync(('read-registers', 2, 4002, 1), lambda response: print(response))        
        
    def post_init_485(self):
        """Called by self when all channel handler were acquired"""
        print("Post init")
        
        self.rs485_handler.send_sync(('read-registers', 29, 4002, 1), lambda response: print(response))