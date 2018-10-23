# -*- coding: utf-8 -*-
"""
Created on Wed Sep 26 21:21:59 2018

@author: even
"""

def get_orders_left(fcoin,symbol):
    states = 'submitted,partial_filled'
    limit=100
    l = list()
    timestamp = 0
    ret = fcoin.list_orders(symbol=symbol,states=states,limit=limit)
#    print('ret',len(ret['data']))
#    print(ret)
    l.append(ret)
    if len(ret['data']) >= limit:
        while True:
            timestamp = ret['data'][-1]['created_at']
#            print('ts',timestamp)
            ret = fcoin.list_orders(symbol=symbol,states=states,before=timestamp,limit=limit)
#            print(ret)
            ret['data'].pop(0)
            if len(ret['data']) == 0:
                break
            else:
                l.append(ret) 
    return l