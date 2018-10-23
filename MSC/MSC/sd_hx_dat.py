# -*- coding: utf-8 -*-
"""
Created on Mon Sep 17 23:30:18 2018

@author: My
"""

def get_hx():
    try:
        with open('hx.dat','r') as f:
            return f.read()
    except FileNotFoundError:
        with open('hx.dat','w') as f:
            f.write('0')
        return '0'
def get_sd():
    try:
        with open('sd.dat','r') as f:
            return f.read()
    except FileNotFoundError:
        with open('sd.dat','w') as f:
            f.write('0')
        return '0'
def hx_set_1():
    with open('hx.dat','w') as f:
        return f.write('1')
def sd_set_1():
    with open('sd.dat','w') as f:
        return f.write('1')
def hx_set_0():
    with open('hx.dat','w') as f:
        return f.write('0')
def sd_set_0():
    with open('sd.dat','w') as f:
        return f.write('0')