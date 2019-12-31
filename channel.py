'''
Created on Dec 12, 2019

@author: dmitri
'''
#from ctypes import windll
import ctypes
from datetime import datetime
from logging1 import debug,trace,info 
from ctypes import *
from action_server import PingAction
try:
    from ctypes.wintypes import *
except:
    pass
import struct
import ctypes_ext
from ctypes_ext import executeDll
import threading
import action
from action import  BaseAction, WaitAction
from tunnel import TunnelManager
import time


RDP2TCP_PING_DELAY = 5

RDP2TCP_CHAN_NAME = "rdp2tcp"
EVT_CHAN_WRITE = 0
EVT_CHAN_READ = 1
EVT_TUNNEL = 2
EVT_PING = 3

def network_write_int(bufferData,offset,val):
    converted = struct.pack('>I', val)
    idx = offset
    for c in converted:
        bufferData[idx]=c
        idx = idx + 1
        
def network_read_int(bufferData,offset):
    return int.from_bytes(bufferData[0:4] , byteorder='big')   

def channel_init(chan_name):
    vchannel = VirtualChannel(chan_name)
    vchannel.Open()
    return vchannel

class BiStreamChannel:
    def __init__(self,server=True):
        self.mutex = threading.Lock()
        self._readBuffer = None
        self.server=server
        self.last_ping = None
        self.__checkOp = 0
        self.pingAllowed=server
        self.connected = False
    def Write(self,tid,command,data):
        if data==None:
            data = ""
        debug(tid,"channel_write "+str(command)+" #"+str(len(data))+" "+str(data),server=self.server)
        binaryMsg = ctypes.create_string_buffer(len(data)+6,data)
        network_write_int(binaryMsg,0,len(data)+2)
        binaryMsg[4]=command
        binaryMsg[5]=tid
        offset = 6
        for c in data:
            binaryMsg[offset] = c
            offset = offset + 1
        trace(0,str(bytearray(binaryMsg)),server=self.server)   
            
        if not self.WriteRaw(bytearray(binaryMsg)):
            raise Exception("unable to write data")  
        return True 
    
    def ReadEvent(self):
        if self._readBuffer !=None and self._readBuffer!=b'':
            raise Exception("buffer not empty")
        self.mutex.acquire()
        data = self.ReadRaw(size=4)
        if data==None or len(data)==0:
            self.mutex.release()
            return None
        size = network_read_int(data, 0)
        data2 = self.ReadRaw(size=size)
        if data2 ==None:
            self._readBuffer = data
            self.mutex.release()
            return None
        data = data + data2
        if self._readBuffer ==None:
            self._readBuffer = data
        else:
            self._readBuffer += data 
        
        data = self._readBuffer
        trace(0,"read len #" + str(len(data)),server=self.server)
        
        #data = self.ReadRaw(size=size);
        #print(data)
        if len(data)<size+4:
            trace(0,"waiting for buffer:" + str(data))
            self.mutex.release()
            return None 
            
        if len(data)>size+4:
            trace(0,"multiple message:" + str(data))

        msg = self._readBuffer[4:size+4]
        self._readBuffer = self._readBuffer[size+4:]
        self.mutex.release()

        trace(0,"message:"+str(msg),server=self.server)        
        command = struct.unpack('<B', msg[0:1])[0]
        tid = struct.unpack('<B', msg[1:2])[0]
        action = BaseAction(command=command,tid=tid,data=msg[2:],server=self.server)
         
        #read all packets
        #offset = 0
        #actions = []
        #while offset<len(data):
        #    msg_len = network_read_int(data, offset)

        #    actions.append(action)
        
        return [action]   
    def PingRaw(self):
        self.last_ping
        now = datetime.now()
        if self.last_ping==None or (now - self.last_ping).total_seconds()>=RDP2TCP_PING_DELAY: 
            self.last_ping = now
            return self.Write(0,action.R2TCMD_PING,None);
        return (0,now)   
    
    def loop(self):
        actions=[None]    
        while actions:
            #try:
            actions = self.ActionWait()
            if actions!=None and len(actions)>0:
                for action in actions:
                    action.Execute(self)
                    action.Ack(self)
            #except:
            #    break
            continue
        
    def ActionWait(self):
        event = self.ReadEvent()
        self.__checkOp = self.__checkOp+1
        if event:
            return event 
        if self.__checkOp>=5 or not self.pingAllowed:
            self.__checkOp=0
            return [WaitAction(5000)]
        else:
            return self.Ping()
        
    def onConnect(self):
        info(0,"channel connected",server=self.server)
                
   

class VirtualChannel(BiStreamChannel):
    
    
    def __init__(self, name):
        super().__init__()
        debug(0,"channel_init",server=self.server)
        self._handle = None
        self._channel = None
        self.name= name
        self.loadLibrary()
    
    def loadLibrary(self):
        wtsapi32Dll = ctypes.WinDLL("wtsapi32.dll")
        self.Wtsapi32Dll = ctypes.windll.LoadLibrary("Wtsapi32.dll")
        
    

        
    def Open(self):
        self.mutex.acquire()
        #print(self.Wtsapi32Dll.WTSVirtualChannelOpen(0, -1, ctypes_ext.as_LPSTR(self.name)))
        self._handle = executeDll(self.Wtsapi32Dll.WTSVirtualChannelOpen,ctypes.wintypes.LPVOID,
                                [ctypes.wintypes.HANDLE, ctypes.wintypes.DWORD, ctypes.wintypes.LPSTR],
                                [0,-1,ctypes_ext.as_LPSTR(self.name)]
                                )
        if not self._handle:
            raise Exception(ctypes.GetLastError()) 
        
        #connect = self.Wtsapi32Dll.WTSVirtualChannelClose
        #connect.restype = ctypes.c_bool
        #connect.argtypes = [ctypes.wintypes.LPVOID]
        #print(connect(self._handle))
        
        #self._readEvent = ctypes.windll.kernel32.CreateEventA(None, True, True, None);  # @UndefinedVariable
        #self._writeEvent = ctypes.windll.kernel32.CreateEventA(None, True, True,None);  # @UndefinedVariable
        
        buffer_ptr = ctypes.POINTER(ctypes.wintypes.LPARAM)()
        bytes_read = ctypes.c_ulong()
        
        param1 = ctypes.byref(buffer_ptr)
        param2 = ctypes.byref(bytes_read)
        
        ret = executeDll(self.Wtsapi32Dll.WTSVirtualChannelQuery,ctypes.c_bool,
                        [ctypes.wintypes.LPVOID, ctypes.c_ushort, ctypes.wintypes.LPVOID,ctypes.wintypes.LPVOID],
                        [self._handle,1,param1,param2]
                        )
        if not ret:
            raise Exception(ctypes.GetLastError()) 
        if bytes_read.value != 8:
            raise Exception("invalid size") 
        self._channel = buffer_ptr[0]
        self.mutex.release()
        return self._handle != None
    
    def Close(self):
        debug(0,"channel_kill")
            
        if self._handle is not None:
            self.mutex.acquire()
            self.Wtsapi32Dll.WTSVirtualChannelClose(self._handle)
            self._handle = None
            self.mutex.release()
        
        time.sleep(15)
    
    def ReadRaw(self, size=None,timeout=100):
        buffer_len = 4096
        if size!=None:
            buffer_len = size
        buffer = ctypes.create_string_buffer(buffer_len)
        
        
        bytes_read = ctypes.c_ulong()
        
        self.mutex.acquire()
        ret = executeDll(self.Wtsapi32Dll.WTSVirtualChannelRead,ctypes.c_bool,
                        [ctypes.wintypes.LPVOID, ctypes.c_ulong, ctypes.wintypes.LPVOID, ctypes.c_ulong,ctypes.wintypes.LPVOID],
                        [self._handle,timeout,ctypes.byref(buffer),buffer_len,ctypes.byref(bytes_read)]
                        )                
        #ret = self.Wtsapi32Dll.WTSVirtualChannelRead(self._handle, 0, ctypes.byref(buffer), buffer_len, ctypes.byref(bytes_read))
        self.mutex.release()
        if ret == 0 or bytes_read.value == 0:
            return None
        
        return bytes(buffer.raw[0:bytes_read.value])
    
    def WriteRaw(self, messageBuffer):
        if self._handle is None:
            return False
        msg_len = len(messageBuffer)
        #buffer = ctypes.create_string_buffer(len(message))
        #buffer.raw = message
        
        buffer_len = ctypes.c_ulong(msg_len)
        byte_written = ctypes.c_ulong()
        
        
        self.mutex.acquire()
        #ret = self.Wtsapi32Dll.WTSVirtualChannelWrite(self._handle, buffer, buffer_len, ctypes.byref(byte_written))
        char_array = ctypes.c_char * msg_len
        
        ret = executeDll(self.Wtsapi32Dll.WTSVirtualChannelWrite,ctypes.c_bool,
                        [ctypes.wintypes.LPVOID, ctypes.wintypes.LPVOID, ctypes.c_ulong,ctypes.wintypes.LPVOID],
                        [self._handle,char_array.from_buffer(messageBuffer),buffer_len,ctypes.byref(byte_written)]
                        )        
        
        self.mutex.release()
        if not ret:
            raise Exception("write failed")
        if byte_written.value!=msg_len:
            raise Exception("len is not equal %d != %d"% (byte_written.value,msg_len))
        return True
    

    

    
    def Ping(self):
        return [PingAction(server=self.server)]

