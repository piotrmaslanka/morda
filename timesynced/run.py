from yos.rt import BaseTasklet, NCounter
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
                # if this happens that means that at least one of the handlers
                # hasn't started up yet - try again...
                Catalog.gather(['rs485', 'rs232'], rs_catalog_handler, catname='serials')
                return
            
            c = NCounter(2, self.post_init) # after both tasklets are open, self.post_init will be called
            Tasklet.open(cat['rs485'], c(lambda v: setattr(self, 'rs485_handler', v)))
            Tasklet.open(cat['rs232'], c(lambda v: setattr(self, 'rs232_handler', v)))

        Catalog.gather(['rs485', 'rs232'], rs_catalog_handler, catname='serials')
        
    def post_init(self):
        """Called when both MODBUS executors were acquired"""
        # Register sync watchers    
        Timer.repeat(60, self.periodical_clock_sweep)
        Timer.repeat(60*60, self.each_hour_sync)

    def synchronize_time(self):
        ZERO_LAMBDA = lambda ret: None
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
        
    def each_hour_sync(self):
        """Called each hour, forcibly synchronizes time"""
        self.synchronize_time()
        print("timesynced: Planned time sync occurred")