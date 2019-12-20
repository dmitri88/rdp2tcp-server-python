# -*- coding: utf-8 -*-
'''
Created on Dec 19, 2019

@author: dmitri
'''
import ctypes


def as_LPSTR(msg):
    return msg.encode('ascii')


def executeDll(func,retType, types, params):
    func.restype = retType
    func.argtypes = types
    return func(*params)
    