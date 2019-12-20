import sys
sys.path.append("W:\\src\\rdp2tcp-server-python")
import time
import channel
from channel import channel_init
from logging1 import debug 


def channel_write_event():
    pass


def tunnel_event(tun, h):
    pass


def channel_is_connected():
    return True





def start_server():
    chan_name =  channel.RDP2TCP_CHAN_NAME
    debug(0,"starting server on channel " + chan_name)
    while True:
        vchannel = channel.channel_init(chan_name)
        if not vchannel:
            break
        ping_action = vchannel.Ping()
        while ping_action != None:
            #try:
            actions = vchannel.ActionWait()
            if actions!=None and len(actions)>0:
                for action in actions:
                    action.Execute(vchannel)
                    action.Ack(vchannel)
            #except:
            #    break
            continue
            #old C code
            ret = -1
            (event,tun,h) = vchannel.EventWait()
            if event == channel.EVT_CHAN_WRITE:
                debug(0, "EVT_CHAN_WRITE");
                ret = channel_write_event();
                if not ret:
                    vchannel.last_ping = now;
            elif event == channel.EVT_CHAN_READ:
                debug(0, "EVT_CHAN_READ");
                action = vchannel.ReadAction();
                if action:
                    action.Ack()
                    vchannel.Ping()         
            elif event == channel.EVT_TUNNEL:
                debug(0, "EVT_TUNNEL");
                ret = tunnel_event(tun,h);   
                  
            elif event == channel.EVT_PING:
                ret = 0
                if channel_is_connected():
                    debug(0, "EVT_PING")
                    (ret,now) = vchannel.Ping()
                else :
                    debug(0, "channel still disconnected");


        vchannel.Close()


if __name__ == "__main__":
    start_server()
    