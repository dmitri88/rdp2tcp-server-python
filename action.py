'''
Created on Dec 20, 2019

@author: dmitri
'''
#rdp2tcp commands
import struct
import socket
from tunnel import TunnelManager
from logging1 import debug,trace
import time

R2TCMD_CONN=0
R2TCMD_CLOSE=1
R2TCMD_DATA=2
R2TCMD_PING=3
R2TCMD_BIND=4
R2TCMD_RCONN=5
R2TCMD_PINGECHO=6 #future
R2TCMD_NOOP=7 #delay command
R2TCMD_MAX=10

TUNAF_ANY=0
TUNAF_IPV4=1
TUNAF_IPV6=2
 

class BaseAction:    
    def __init__(self,tid=None,command=None, data=None, server=True):
        self.data = data
        self.server=server
        import action_client
        import action_server
        if server:
            self.actions = action_server
        else:
            self.actions = action_client
        if tid!=None:
            self.tunnelId = int(tid)
        else:
            self.tunnelId = None
        if command != None:
            self.command = int(command)
        else:
            self.command = None
        if self.command<0 or self.command>R2TCMD_MAX:
            raise Exception("invalid tid #"+str(self.tunnelId)+" command "+str(self.command)+" data:"+str(self.data))
        
        
        self.__parse(data)
    
    def Ack(self,vchannel):
        debug(self.tid,"ack for action"+str(self))
        pass
    
    def Execute(self,vchannel):
        trace(self.tid,"execute for action"+str(self))
        pass
    
    def Parse(self,msgBuffer):
        pass
    
    def __parse(self,msgBuffer):
        if self.command==R2TCMD_CONN:
            self.__class__=self.actions.ConnectAction
        elif self.command==R2TCMD_CLOSE:
            self.__class__=self.actions.CloseAction
        elif self.command==R2TCMD_PING:
            self.__class__=self.actions.PingAction
        elif self.command==R2TCMD_DATA:
            self.__class__=self.actions.DataAction
        elif self.command==R2TCMD_NOOP:
            self.__class__=WaitAction
        elif self.command==R2TCMD_PINGECHO:
            self.__class__=self.actions.PingEchoAction
        else:
            raise Exception("unknown command "+str(self.command)+" data:"+str(self.data))
        self.Parse(msgBuffer)
    
        
    def __str__(self):
        return str(self.__class__)+": tun:"+str(self.tunnelId)+" cmd:"+str(self.command)+" data:"+str(self.data)
       
class WaitAction(BaseAction):
    def __init__(self,timeout=1000):
        super(WaitAction, self).__init__(tid=0,command=R2TCMD_NOOP)
        self.timeout=timeout
        self.tid=0
    def Ack(self,vchannel):
        pass
    
    def Execute(self,vchannel):
        time.sleep(self.timeout/1000)
    pass
    