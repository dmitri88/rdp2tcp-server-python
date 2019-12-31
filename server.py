import sys
import threading
sys.path.append("W:\\src\\rdp2tcp-server-python")
import time
import channel
from channel import channel_init
from logging1 import debug 
from socketserver import ThreadingMixIn, TCPServer, StreamRequestHandler
from socks import ThreadingTCPServer,SocksProxy 

def channel_write_event():
    pass


def tunnel_event(tun, h):
    pass


def channel_is_connected():
    return True





def start_server():
    chan_name =  channel.RDP2TCP_CHAN_NAME
    debug(0,"starting rdp2tcp server on channel " + chan_name)
    
    #server = ThreadingTCPServer(('127.0.0.1', 9011), SocksProxy)
    #debug(0,"starting sock5 server on 127.0.0.1:9011 ")
    #socksThread = threading.Thread(target=server.serve_forever, args=())
    #socksThread.start()
    
    while True:
        vchannel = channel.channel_init(chan_name)
        if not vchannel:
            break
        actions = vchannel.Ping()
        while actions:
            #try:
            actions = vchannel.ActionWait()
            if actions!=None and len(actions)>0:
                for action in actions:
                    action.Execute(vchannel)
                    action.Ack(vchannel)
            #except:
            #    break
            continue
        vchannel.Close()


if __name__ == "__main__":
    start_server()
    