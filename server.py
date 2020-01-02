import sys
import threading
sys.path.append("W:\\src\\rdp2tcp-server-python")
import time
import channel
from channel import channel_init
from logging1 import debug 
from socketserver import ThreadingMixIn, TCPServer, StreamRequestHandler
from socks import ThreadingTCPServer,SocksProxy 

class Server:
    def __init__(self):
        self.vchannel = None
        self.terminated = False
        
    def Terminate(self):
        self.terminated = True
        if self.vchannel:
            self.vchannel.Terminate()
    def loop(self):
        chan_name =  channel.RDP2TCP_CHAN_NAME
        debug(0,"starting rdp2tcp server on channel " + chan_name)

        while not self.terminated:
            self.vchannel = channel.channel_init(chan_name)
            if not self.vchannel:
                break
            actions = self.vchannel.Ping()
            self.vchannel.loop()
            self.vchannel.Close()        

    
    #server = ThreadingTCPServer(('127.0.0.1', 9011), SocksProxy)
    #debug(0,"starting sock5 server on 127.0.0.1:9011 ")
    #socksThread = threading.Thread(target=server.serve_forever, args=())
    #socksThread.start()
    



if __name__ == "__main__":
    Server().loop()
    