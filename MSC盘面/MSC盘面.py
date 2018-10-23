# -*- coding: utf-8 -*-
"""
Created on Wed Sep  5 10:58:03 2018

@author: even
"""

import time
from fcoin import Fcoin
from prettytable import PrettyTable
from colorama import init,Fore
import get_orders


'''
刷新间隔(秒)
'''
t = 5
init(autoreset=True) 
limit = '100'
symbol = 'msceth'
'''
属性	含义解释
submitted	已提交
partial_filled	部分成交
partial_canceled	部分成交已撤销
filled	完全成交
canceled	已撤销
pending_cancel	撤销已提交
'''
def query_orders():
    while True:
        buy_dict = {}
        sell_dict = {}
        l = list()
        l += get_orders.get_orders_left(fcoin1,symbol)
        l += get_orders.get_orders_left(fcoin2,symbol)
        l += get_orders.get_orders_left(fcoin3,symbol)
        l += get_orders.get_orders_left(fcoin4,symbol)
        depth = fcoin4.get_market_depth(level,symbol)
        isfailed = False
        for i in l:
            if 'data' in i:
                i = i['data']
                for order_unit in i:
                    order_unit['price'] = '%.8f eth' %float(order_unit['price'])
                    if order_unit['side'] == 'buy':
                        if order_unit['price'] in buy_dict:
                            buy_dict[order_unit['price']] += round((float(order_unit['amount']) - float(order_unit['filled_amount'])),2)
                        else:
                            buy_dict[order_unit['price']] = round((float(order_unit['amount']) - float(order_unit['filled_amount'])),2)
                    if order_unit['side'] == 'sell':
                        if order_unit['price'] in sell_dict:
                            sell_dict[order_unit['price']] += round((float(order_unit['amount']) - float(order_unit['filled_amount'])),2)
                        else:
                            sell_dict[order_unit['price']] = round((float(order_unit['amount']) - float(order_unit['filled_amount'])),2) 
            else:
                print('没有获取到data\n',i)
                isfailed = True
                break
        if not isfailed:
            for buyprice in buy_dict:
                buy_dict[buyprice] = '%.2f'%buy_dict[buyprice]
            for sellprice in sell_dict:
                sell_dict[sellprice] = '%.2f'%sell_dict[sellprice]
            if 'data' in depth:
                bid = depth['data']['bids']
                ask = depth['data']['asks']
                bid_price,bid_amount,ask_price,ask_amount = [],[],[],[]
                for i in range(0,int(len(bid)/2)):
                    bid_price.append('%.8f eth'%float(bid[i*2]))
                    bid_amount.append('%.2f'%float(bid[i*2+1]))
                for i in range(0,int(len(ask)/2)):
                    ask_price.append('%.8f eth'%float(ask[2*i]))
                    ask_amount.append('%.2f'%float(ask[2*i+1]))
                buyside = {}
                sellside = {}
                for j in range(0,int(len(bid)/2)):
                    if bid_price[j] in buy_dict:
                        buyside[bid_price[j]] = [bid_price[j],bid_amount[j],buy_dict[bid_price[j]],'%.2f%%'%(100*float(buy_dict[bid_price[j]])/float(bid_amount[j]))]
                    else:
                        buyside[bid_price[j]] = [bid_price[j],bid_amount[j],'%.2f'%0,r'0%']
                for j in range(0,int(len(ask)/2)):
                    if ask_price[j] in sell_dict:
                        sellside[ask_price[j]] = [ask_price[j],ask_amount[j],sell_dict[ask_price[j]],'%.2f%%'%(100*float(sell_dict[ask_price[j]])/float(ask_amount[j]))]
                    else:
                        sellside[ask_price[j]] = [ask_price[j],ask_amount[j],'%.2f'%0,r'0%']
                bid_table = PrettyTable(["买价","盘面数量","委托数量","比例"])
                for pb in buyside:
                    bid_table.add_row(buyside[pb])
                bid_table.align["买价"] = 'l'
                bid_table.align["盘面数量"] = 'r'
                bid_table.align["委托数量"] = 'r'
                bid_table.align["比例"] = 'r'
                ask_table = PrettyTable(["卖价","盘面数量","委托数量","比例"])
                for ps in sellside:
                    ask_table.add_row(sellside[ps])
                ask_table.align["卖价"] = 'l'
                ask_table.align["盘面数量"] = 'r'
                ask_table.align["委托数量"] = 'r'
                ask_table.align["比例"] = 'r'
                print('…………………………………………………………………………………………')
                print('时间：',time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                print(Fore.RED + 'MSC卖盘：\n',Fore.RED + ask_table.get_string(sortby="卖价",reversesort=True)) 
                print(Fore.GREEN +'MSC买盘：\n',Fore.GREEN + bid_table.get_string(sortby="买价", reversesort=True))
                print('统计完毕，%d秒后重新获取'%t)
                time.sleep(t)
            
while True:
    try:
        query_orders()
    except Exception as e:
        print('----------------------------------------------------')
        print('出错了！！！！！！！！\nError:', e)
    except:
        print('----------------------------------------------------')
        print('出错了！！！！！！！！')
    finally:
#      此处可以添加提醒，如提示音。另，下一版本对输出内容作保存，交易可以保存到表
        print('----------------------------------------------------')
        print('\n程序意外停止！\n\n5秒后重新运行程序...')
        time.sleep(5)
