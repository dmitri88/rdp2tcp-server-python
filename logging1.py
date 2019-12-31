'''
Created on Dec 12, 2019

@author: dmitri
'''


def info(tun_id,msg,server=None):
    _log(tun_id,msg,server=server)

def debug(tun_id,msg,server=None):
    _log(tun_id,msg,server=server)
    
def trace(tun_id,msg,server=None):
    _log(tun_id,msg,server=server)
    
def _log(tun_id,msg,server=None):
    prefix = ""
    if server!=None:
        prefix = "[C] "
        if server:
            prefix = "[S] "
    print("#%d %s%s" %(tun_id,prefix,msg))