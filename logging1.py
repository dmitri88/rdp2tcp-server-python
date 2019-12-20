'''
Created on Dec 12, 2019

@author: dmitri
'''


def debug(tun_id,msg):
    _log(tun_id,msg)
    
def trace(tun_id,msg):
    _log(tun_id,msg)
    
def _log(tun_id,msg):
    print("#%d %s" %(tun_id,msg))