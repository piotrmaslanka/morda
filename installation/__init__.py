from yos.rt import BaseTasklet, NCounter
from yos.tasklets import Tasklet
from yzero import Zero, SeriesDefinition
from morda.settings import ZERO_CONNECT

class Install(BaseTasklet):
    
    def on_startup(self):
        print("Installing")
        self.zero = Zero(ZERO_CONNECT)
    
        def done():
            print ("Zero series defined")
            Tasklet.me().terminate()
    
        installs = NCounter(22, done)
    
        # define electricity
        
        e_pc = SeriesDefinition('pwr.wh_counter', 1, 1, 0, 8, '', 0)
        
        e_v1 = SeriesDefinition('pwr.phase1.voltage', 1, 1, 16070400, 4, 'slabsize=65536', 0)
        e_v2 = SeriesDefinition('pwr.phase2.voltage', 1, 1, 16070400, 4, 'slabsize=65536', 0)
        e_v3 = SeriesDefinition('pwr.phase3.voltage', 1, 1, 16070400, 4, 'slabsize=65536', 0)

        e_w1 = SeriesDefinition('pwr.phase1.power', 1, 1, 16070400, 4, 'slabsize=65536', 0)
        e_w2 = SeriesDefinition('pwr.phase2.power', 1, 1, 16070400, 4, 'slabsize=65536', 0)
        e_w3 = SeriesDefinition('pwr.phase3.power', 1, 1, 16070400, 4, 'slabsize=65536', 0)
    
        e_va1 = SeriesDefinition('pwr.phase1.apparent_power', 1, 1, 16070400, 4, 'slabsize=65536', 0)
        e_va2 = SeriesDefinition('pwr.phase2.apparent_power', 1, 1, 16070400, 4, 'slabsize=65536', 0)
        e_va3 = SeriesDefinition('pwr.phase3.apparent_power', 1, 1, 16070400, 4, 'slabsize=65536', 0)

        e_var1 = SeriesDefinition('pwr.phase1.reactive_power', 1, 1, 16070400, 4, 'slabsize=65536', 0)
        e_var2 = SeriesDefinition('pwr.phase2.reactive_power', 1, 1, 16070400, 4, 'slabsize=65536', 0)
        e_var3 = SeriesDefinition('pwr.phase3.reactive_power', 1, 1, 16070400, 4, 'slabsize=65536', 0)
        
        # define heating
        
        h_external = SeriesDefinition('heating.external.temp', 1, 1, 0, 4, 'slabsize=65536', 0)
        h_boiler = SeriesDefinition('heating.boiler.temp', 1, 1, 16070400, 4, 'slabsize=65536', 0)
        h_boiler_ref = SeriesDefinition('heating.boiler.ref', 1, 1, 16070400, 4, 'slabsize=65536', 0)
        h_co = SeriesDefinition('heating.co.temp', 1, 1, 16070400, 4, 'slabsize=65536', 0)
        h_co_ref = SeriesDefinition('heating.co.ref', 1, 1, 16070400, 4, 'slabsize=65536', 0)
        h_cwu = SeriesDefinition('heating.cwu.temp', 1, 1, 16070400, 4, 'slabsize=65536', 0)
        h_cwu_ref = SeriesDefinition('heating.cwu.ref', 1, 1, 16070400, 4, 'slabsize=65536', 0)
        h_internal = SeriesDefinition('heating.internal.temp', 1, 1, 16070400, 4, 'slabsize=65536', 0)
        h_internal_ref = SeriesDefinition('heating.internal.ref', 1, 1, 16070400, 4, 'slabsize=65536', 0)
        
        
        self.zero.updateDefinition(e_v1, installs()).updateDefinition(e_v2, installs()).updateDefinition(e_v3, installs()).updateDefinition(e_w1, installs()).updateDefinition(e_w2, installs()).updateDefinition(e_w3, installs()).updateDefinition(e_pc, installs()).updateDefinition(e_va1, installs()).updateDefinition(e_va2, installs()).updateDefinition(e_va3, installs()).updateDefinition(e_var1, installs()).updateDefinition(e_var2, installs()).updateDefinition(e_var3, installs()).updateDefinition(h_external, installs()).updateDefinition(h_boiler, installs()).updateDefinition(h_boiler_ref, installs()).updateDefinition(h_co, installs()).updateDefinition(h_co_ref, installs()).updateDefinition(h_cwu, installs()).updateDefinition(h_cwu_ref, installs()).updateDefinition(h_internal, installs()).updateDefinition(h_internal_ref, installs())
        
        