from yos.rt import BaseTasklet
from yos.ipc import Catalog
from yos.tasklets import Tasklet

from morda.serialTasklet.guardianAngel import GuardianAngel

class SerialTasklet(BaseTasklet):
    """
    This tasklet executes MODBUS commands on a particular port
    """
    
    def __init__(self, comport: str, channame: str):
        BaseTasklet.__init__(self)
        
        # spawn our serial port handler
        self.angel = GuardianAngel(self, comport)
        self.angel.start()
        
        self.channame = channame

    def on_startup(self):
        # tell that you support a particular channel
        Catalog.store(self.channame, Tasklet.me().tid, catname='serials')
        
    def on_message(self, source: int, msg):
        """
        Please send only synchronous messages. Thank you =)
        
        
        Valid commands are:
        
                ('read-registers', address, register-start, register-amount)
                            response: array of results or None if failure
                ('write-register', address, register, value)
                            response: True is success, None if failure
                ('read-flag', address, flag)
                            response: True or False, None if failure
                ('read-lte', address, register) 
                                this reads something that in previous BMS was 
                                called LTE. I have no idea what that means,
                                but I'm leaving this in for legacy.
                                It uses Read-Input-Register 0x04 MODBUS command btw
                            response: value if result, None if failure
                            
        tl;dr - I have read-lte to support reading from a particular electric power meter
        """
        self.angel.to_execute.put(msg)
                
    def on_message_execed(self, msg, data):
        """
        Called by the Guardian Angel upon completing a request.
        Sadly, the way it's called violates y/OS guidelines, because 
        the event is not scheduled via Event Execution Processor
        Too bad =)
        """
        msg.reply(data)