from yos.rt import GCTasklet
from yos.tasklets import Tasklet

class Initrd(GCTasklet):
    def on_startup(self):
        
        from morda.serialTasklet import SerialTasklet
        from morda.timesynced import TimesyncedTasklet
        from morda.httpInterface import HTTPServerTasklet
        from morda.power import ElectricityReader
        from morda.installation import Install
        from morda.irrigation import IrrigationReader
        
        # Serial port handlers
        Tasklet.start(SerialTasklet, '232handler', 'serials', None, None, 'COM1', 'rs232')
        Tasklet.start(SerialTasklet, '485handler', 'serials', None, None, 'COM2', 'rs485')
        
        # Time synchronizer
        Tasklet.start(TimesyncedTasklet, 'timesynced', 'timesynced', None)
        
        # HTTP REST API server
        Tasklet.start(HTTPServerTasklet, 'server', 'http', None)
        
        # Device readers
        Tasklet.start(ElectricityReader, 'reader', 'power', None)        
        Tasklet.start(IrrigationReader, 'reader', 'irrigation', None)
        
        # Configurator and environment sanitizer
        Tasklet.start(Install, 'install', 'install', None)
