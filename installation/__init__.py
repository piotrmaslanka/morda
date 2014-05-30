from yos.rt import BaseTasklet, NCounter
from yos.tasklets import Tasklet
from yzero import Zero, SeriesDefinition
from morda.settings import ZERO_CONNECT

class Install(BaseTasklet):
    
    def on_startup(self):
        self.zero = Zero(ZERO_CONNECT)
    
        def done():
            Tasklet.me().terminate()
    
        installs = NCounter(7, done)
    
        # define electricity
        
        e_pc = SeriesDefinition('pwr.wh_counter', 1, 1, 0, 8, '', 0)
        
        e_v1 = SeriesDefinition('pwr.phase1.voltage', 1, 1, 16070400, 4, 'slabsize=65536', 0)
        e_v2 = SeriesDefinition('pwr.phase2.voltage', 1, 1, 16070400, 4, 'slabsize=65536', 0)
        e_v3 = SeriesDefinition('pwr.phase3.voltage', 1, 1, 16070400, 4, 'slabsize=65536', 0)

        e_w1 = SeriesDefinition('pwr.phase1.power', 1, 1, 16070400, 4, 'slabsize=65536', 0)
        e_w2 = SeriesDefinition('pwr.phase2.power', 1, 1, 16070400, 4, 'slabsize=65536', 0)
        e_w3 = SeriesDefinition('pwr.phase3.power', 1, 1, 16070400, 4, 'slabsize=65536', 0)
        
        self.zero.updateDefinition(e_v1, installs()).updateDefinition(e_v2, installs()).updateDefinition(e_v3, installs()).updateDefinition(e_w1, installs()).updateDefinition(e_w2, installs()).updateDefinition(e_w3, installs()).updateDefinition(e_pc, installs())
        
        