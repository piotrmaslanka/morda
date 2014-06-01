from yos.ipc import Catalog

from morda.httpInterface.get_series import get_series

def execute(sock, call_on_completion: callable, **kwargs) -> object:
    """
    Do what it takes to serve the request.
    
    Call call_on_completion with JSONable argument when you finish
    """
    
    if kwargs['operation'] == 'get-electro':
        Catalog.gather(['pwr.phase1.voltage', 'pwr.phase2.voltage', 'pwr.phase3.voltage', 
                        'pwr.phase1.power', 'pwr.phase2.power', 'pwr.phase3.power',
                        'pwr.phase1.apparent_power', 'pwr.phase2.apparent_power',
                        'pwr.phase3.apparent_power', 'pwr.phase1.reactive_power',
                        'pwr.phase2.reactive_power', 'pwr.phase3.reactive_power',
                        'pwr.phase1.frequency', 'pwr.phase2.frequency', 
                        'pwr.phase3.frequency', 'pwr.wh_counter'], call_on_completion, catname='values')        
    elif kwargs['operation'] == 'series-load':
        get_series(kwargs['series-name'], int(kwargs['from']), int(kwargs['to']), call_on_completion)        
    else:
        call_on_completion({'hello': 'world'})
