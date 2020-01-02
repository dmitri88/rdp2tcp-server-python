#!/usr/bin/env python3
'''
Created on Dec 27, 2019

@author: dmitri
'''
import os,sys
from channel import BiStreamChannel
import time


def setup_parent_proc():
    pso = "/proc/"+str(os.getppid())+"/fd/0"
    
    f = open(pso, "w")
    sys.stdout = f
    sys.stderr = f
    
    print("initializing rdp2tcp client")
    
class Client(BiStreamChannel):
    def __init__(self):
        super().__init__(server=False)
    def ReadRaw(self,size):
        self.mutex.acquire()
        ret=os.read(0, size)
        self.mutex.release()
        return ret
    def WriteRaw(self,data):
        
        self.mutex.acquire()
        time.sleep(3)
        os.write(1, data)
        self.mutex.release()
        #raise Exception("Asd")
        return True

        

def start_client():
    Client().loop()
    print("Died")

if __name__ == "__main__":
    setup_parent_proc()
    start_client()