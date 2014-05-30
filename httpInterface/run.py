from yos.io import NetworkSocket
from yos.rt import BaseTasklet, GCTasklet
from yos.tasklets import Tasklet
import urllib.parse
from morda.httpInterface.execute import execute
import json

try:
    from http_parser.parser import HttpParser
except ImportError:
    from http_parser.pyparser import HttpParser

class HTTPConnection(GCTasklet):
    def __init__(self, client_sock):
        self.client_sock = client_sock
        self.buffer = bytearray()
        
    def on_startup(self):
        self.client_sock.register(self.on_readable, None, None, None, None)
    
    def on_readable(self, sock, data):
        self.buffer.extend(data)

        p = HttpParser()
        p.execute(self.buffer, len(self.buffer))
        if not p.is_message_complete():
            return
                
        try:
            jsonargs = urllib.parse.parse_qs(self.buffer.split(b'\r\n')[-1])
            jsonargs = dict((k.decode('utf8'), v[0].decode('utf8')) for k, v in jsonargs.items())
        except:
            sock.close()
            return

        execute(sock, self.output_values, **jsonargs)
            
    def output_values(self, val):
        try:
            x = json.dumps(val)
        except Exception as x:
            val = x
        
        if isinstance(val, Exception):
            self.client_sock.write(b'HTTP/1.1 500 Internal server error\nAccess-Control-Allow-Origin: *\n\n')
        else:
            self.client_sock.write(b'HTTP/1.1 200 OK\nContent-Type: application/json\nAccess-Control-Allow-Origin: *\n\n')
            self.client_sock.write(x.encode('utf8'))

        self.client_sock.close()

class HTTPServerTasklet(BaseTasklet):
    """
    Tasklet that is a server for HTTP REST API for the BMS
    """
    
    def on_startup(self):
        sock = NetworkSocket.server(NetworkSocket.SOCK_TCP, ('127.0.0.1', 81))
        sock.register(self.on_new_connection, None, None, None, None)
        
    def on_new_connection(self, sock, clientsock):
        Tasklet.start(HTTPConnection, 'client', None, None, None, clientsock)