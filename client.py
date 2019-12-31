#!/usr/bin/env python
'''
Created on Dec 27, 2019

@author: dmitri
'''
import os,sys
import time
from channel import BiStreamChannel


def setup_parent_proc():
    f = open("/proc/"+str(os.getppid())+"/fd/0", "a")
    sys.stdout = f
    sys.stderr = f
    print("initializing rdp2tcp client")
    
class Client(BiStreamChannel):
    def __init__(self):
        super().__init__(server=False)
    def ReadRaw(self,size):
        return os.read(0, size)
    def WriteRaw(self,data):
        os.write(1, data)

        

def start_client():
    Client().loop()

if __name__ == "__main__":
    setup_parent_proc()
    start_client()