def execute(sock, call_on_completion: callable, **kwargs) -> object:
    """
    Do what it takes to serve the request.
    
    Call call_on_completion with JSONable argument when you finish
    """
    
    call_on_completion({'hello': 'world'})
