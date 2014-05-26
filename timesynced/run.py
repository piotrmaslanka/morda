from yos.rt import BaseTasklet
from yos.ipc import Catalog
from yos.time import Timer
from yos.tasklets import Tasklet

import datetime # time module would be useless - we don't want UTC time :)

class TimesyncedTasklet(BaseTasklet):
    """
    Tasklet whose job is to keep clock synchronized on all PLC devices.
    
    It does it in two ways:
        1) each hour a time signal is sent to attached devices
        2) each minute it is checked whether time deviated more than 30 minutes.
                if it does, then computer clock was changed and time signal is
                sent to attached devices
    """
    
    def __init__(self):
        BaseTasklet.__init__(self)
        self.rs485_handler = None
        self.rs232_handler = None
        
        self.last_timestamp = datetime.datetime.now()       # Last timestamp
    
    def on_startup(self):
        # We need to acquire MODBUS command executors...
        def rs_catalog_handler(cat):
            if None in cat.values():
                Catalog.gather(['rs485', 'rs232'], rs_catalog_handler, catname='serials')
                return
                
            def test485(rs485_handler):
                self.rs485_handler = rs485_handler
                if self.rs232_handler != None:
                    self.post_init()            
            def test232(rs232_handler):
                self.rs232_handler = rs232_handler
                if self.rs485_handler != None:
                    self.post_init()
                    
            Tasklet.open(cat['rs485'], test485)
            Tasklet.open(cat['rs232'], test232)

        Catalog.gather(['rs485', 'rs232'], rs_catalog_handler, catname='serials')
        
    def post_init(self):
        """Called when both MODBUS executors were acquired"""
        # Register sync watchers    
        self.periodical_clock_sweep()
        self.each_hour_sync()

    def synchronize_time(self):
        ZERO_LAMBDA = lambda ret: pass
        HOUR = datetime.datetime.now().hour
        MINUTE = datetime.datetime.now().minute
    
        # Synchronize irrigation
        self.rs485_handler.send_sync(('write-register', 28, 4001, MINUTE), ZERO_LAMBDA)
        self.rs485_handler.send_sync(('write-register', 28, 4002, HOUR), ZERO_LAMBDA)

        # Synchronize heating
        self.rs232_handler.send_sync(('write-register', 2, 4001, MINUTE), ZERO_LAMBDA)
        self.rs232_handler.send_sync(('write-register', 2, 4002, HOUR), ZERO_LAMBDA)
        
    def periodical_clock_sweep(self):
        """Called each minute, checking clock deviation. If more than 30 minutes, then clock has 
        been readjusted - sends time signal to target devices then"""
        
        if abs(self.last_timestamp - datetime.datetime.now()) > datetime.timedelta(0, 30*60):
            # Clock deviated, correct it
            print("timesynced: Unplanned clock deviation occurred")
            self.synchronize_time()
            
        self.last_timestamp = datetime.datetime.now()
        Timer.create(60, self.periodical_clock_sweep)
        
    def each_hour_sync(self):
        """Called each hour, forcibly synchronizes time"""
        self.synchronize_time()
        Timer.create(60*60, self.each_hour_sync)
        print("timesynced: Planned time sync occurred")