from yos.rt import GCTasklet
from yos.tasklets import Tasklet

class Initrd(GCTasklet):
    def on_startup(self):
        
        from morda.serialTasklet import SerialTasklet
        from morda.timesynced import TimesyncedTasklet
        from morda.httpInterface import HTTPServerTasklet
        from morda.power import ElectricityReader
        from morda.installation import Install
        
        #Tasklet.start(SerialTasklet, '232handler', 'SerialHandler', None, None, 'COM1', 'rs232')
        Tasklet.start(SerialTasklet, '485handler', 'SerialHandler', None, None, 'COM2', 'rs485')
        #Tasklet.start(TimesyncedTasklet, 'timesynced', 'Support', None)
        Tasklet.start(HTTPServerTasklet, 'server', 'http', None)
        Tasklet.start(ElectricityReader, 'power', 'power', None)
        Tasklet.start(Install, 'install', 'install', None)
