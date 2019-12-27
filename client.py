#!/usr/bin/env python
'''
Created on Dec 27, 2019

@author: dmitri
'''
import os,sys
import time


def setup_parent_proc():
    f = open("/proc/"+str(os.getppid())+"/fd/0", "a")
    sys.stdout = f
    print("initializing rdp2tcp client")
    

def start_client():
    f = open("/tmp/demofile2.txt", "a+")
    f.write(str(os.getppid()))
    f.close()
    i=0
    while True:
        
        print("test")
        data = os.read(0, 4)
        print(str(data))
        print(len(data))
        os.write(1, "hello")

        
        time.sleep(2)
        pass

if __name__ == "__main__":
    setup_parent_proc()
    start_client()