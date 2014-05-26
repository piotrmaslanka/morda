from yos.rt import GCTasklet
from yos.tasklets import Tasklet

class Initrd(GCTasklet):
    def on_startup(self):
        
        from morda.serialTasklet import SerialTasklet
        from morda.timesynced import TimesyncedTasklet
        
        Tasklet.start(SerialTasklet, '232handler', 'SerialHandler', None, None, 'COM1', 'rs232')
        Tasklet.start(SerialTasklet, '485handler', 'SerialHandler', None, None, 'COM2', 'rs485')
        Tasklet.start(TimesyncedTasklet, 'timesynced', 'Support', 'MORDA')