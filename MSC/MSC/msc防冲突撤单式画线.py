# -*- coding: utf-8 -*-
"""
Created on Tue Sep 11 09:09:29 2018

@author: My
"""

from fcoin_hand import market_adjust
import configparser
import json
import time
import random
import sd_hx_dat as dat

'''
bitfun
'''
key = ''
secret = ''


ma = market_adjust('msceth',True)
ma.auth(key,secret)


conf = configparser.ConfigParser()
conf.read('conf.ini')
adjust_list = conf.get("conf", "list")
adjust_list = json.loads(adjust_list)['list']
i = int(conf.get("conf", "start_from"))
print(adjust_list)
def err_warn():
    dat.hx_set_0()
    print('\a'+'程序意外停止！\n5秒后重新运行程序...')
    time.sleep(1)
    print('\a'+'4秒后重新运行程序...')
    time.sleep(1)
    print('\a'+'3秒后重新运行程序...')
    time.sleep(1)
    print('\a'+'2秒后重新运行程序...')
    time.sleep(1)
    print('\a'+'1秒后重新运行程序...')
    time.sleep(1)
for j in range(i,len(adjust_list)):
    d = adjust_list[j]
    try:
        i += 1
        t = random.randint(45,75)
        print("%d秒后进行第%d次调整,调整量：%d"%(t,i,d))
        time.sleep(t)
        r = ma.adjust(d)
        dat.hx_set_0()
        conf.set('conf','start_from',str(j+1))
        with open('conf.ini','w') as fw:
            conf.write(fw)
        if r != 0 and r != -2:
            print('\a')
            time.sleep(1)
            print('\a')
            time.sleep(1)
            print('\a')
    except Exception as e:
        print('----------------------------------------------------')
        print('出错了！！！！！！！！\nError:', e)
        print('----------------------------------------------------')
        err_warn()
    except:
        print('----------------------------------------------------')
        print('出错了！！！！！！！！')
        print('----------------------------------------------------')
        err_warn()
while True:
    dat.hx_set_0()
    input('画线结束')
