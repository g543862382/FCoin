# -*- coding: utf-8 -*-
"""
Created on Wed Sep  5 10:58:03 2018

@author: even
"""
import os
import time
from fcoin import Fcoin
from prettytable import PrettyTable
from colorama import init,Fore
import get_orders


init(autoreset=True) 
limit = '1000'
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
#        print(depth)
        print('买:',len(depth['data']['bids'])/2,'档')
        print('卖:',len(depth['data']['asks'])/2,'档')
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
#                print(depth)
                bid = depth['data']['bids']
                ask = depth['data']['asks']
                bid_price,bid_amount,ask_price,ask_amount = [],[],[],[]
                for i in range(0,int(len(bid)/2)):
                    bid_price.append('%.8f eth'%float(bid[i*2]))
                    bid_amount.append('%.2f'%float(bid[i*2+1]))
                for k in range(0,int(len(ask)/2)):
                    ask_price.append('%.8f eth'%float(ask[2*k]))
                    ask_amount.append('%.2f'%float(ask[2*k+1]))
                buyside = {}
                sellside = {}
                for m in range(0,int(len(bid)/2)):
                    if bid_price[m] in buy_dict:
                        buyside[bid_price[m]] = [bid_price[m],bid_amount[m],buy_dict[bid_price[m]],'%.2f%%'%(100*float(buy_dict[bid_price[m]])/float(bid_amount[m]))]
                    else:
                        buyside[bid_price[m]] = [bid_price[m],bid_amount[m],'%.2f'%0,r'0%']
                for n in range(0,int(len(ask)/2)):
                    if ask_price[n] in sell_dict:
                        sellside[ask_price[n]] = [ask_price[n],ask_amount[n],sell_dict[ask_price[n]],'%.2f%%'%(100*float(sell_dict[ask_price[n]])/float(ask_amount[n]))]
                    else:
                        sellside[ask_price[n]] = [ask_price[n],ask_amount[n],'%.2f'%0,r'0%']
                        
#               买累积
                for price1 in bid_price:
                    sum_amount = 0.00
                    sum_eth = 0.0
                    sum_amount_own = 0.00
                    sum_amount_eth = 0.00
                    for price2 in bid_price:
                        if float(price2[:10]) >= float(price1[:10]): 
                            sum_amount += float(buyside[price2][1])
                            sum_eth += float(price2[:10])*float(buyside[price2][1])
                            if price2 in buy_dict:
                                sum_amount_eth += float(price2[:10])*float(buy_dict[price2])
                            else:
                                sum_amount_eth = sum_amount_eth
                    sum_amount = '%.2f'%sum_amount
                    sum_eth = '%.8f eth'%sum_eth
                    buyside[price1].insert(2,sum_amount)
                    buyside[price1].insert(3,sum_eth)
                    for price3 in buy_dict:
                        if float(price3[:10]) >= float(price1[:10]):
                            sum_amount_own += float(buy_dict[price3])
                    sum_amount_own = '%.2f'%sum_amount_own
                    buyside[price1].insert(6,sum_amount_own)
                    sum_amount_eth = '%.8f eth'%sum_amount_eth
                    buyside[price1].insert(7,sum_amount_eth)
#               卖累积
                for price1 in ask_price:
                    sum_price = 0.00
                    sum_eth = 0.0
                    sum_amount_own = 0.00
                    sum_amount_eth = 0.00
                    for price2 in ask_price:
                        if float(price2[:10]) <= float(price1[:10]): 
                            sum_price += float(sellside[price2][1])
                            sum_eth += float(price2[:10])*float(sellside[price2][1])
                            if price2 in sell_dict:
                                sum_amount_eth += float(price2[:10])*float(sell_dict[price2])
#                                print(sum_amount_eth)
                            else:
                                sum_amount_eth = sum_amount_eth
                    sum_price = '%.2f'%sum_price
                    sum_eth = '%.8f eth'%sum_eth
                    sellside[price1].insert(2,sum_price)
                    sellside[price1].insert(3,sum_eth)
                    for price3 in sell_dict:
                        if float(price3[:10]) <= float(price1[:10]):
                            sum_amount_own += float(sell_dict[price3])
                    sum_amount_own = '%.2f'%sum_amount_own
                    sellside[price1].insert(6,sum_amount_own)
                    sum_amount_eth = '%.8f eth'%sum_amount_eth
                    sellside[price1].insert(7,sum_amount_eth)
                
                bid_table = PrettyTable(["买价","盘面数量","累积","累积eth","我方委托数量","比例","我方累积","我方累积eth"])
                for pb in buyside:
                    bid_table.add_row(buyside[pb])
                bid_table.align["买价"] = 'l'
                bid_table.align["盘面数量"] = 'r'
                bid_table.align["我方委托数量"] = 'r'
                bid_table.align["累积"] = 'r'
                bid_table.align["比例"] = 'r'
                bid_table.align["我方累积"] = 'r'
                bid_table.align["我方累积eth"] = 'r'
                ask_table = PrettyTable(["卖价","盘面数量","累积","累积eth","我方委托数量","比例","我方累积","我方累积eth"])
                for ps in sellside:
                    ask_table.add_row(sellside[ps])
                ask_table.align["卖价"] = 'l'
                ask_table.align["盘面数量"] = 'r'
                ask_table.align["我方委托数量"] = 'r'
                ask_table.align["累积"] = 'r'
                ask_table.align["比例"] = 'r'
                ask_table.align["我方累积"] = 'r'
                ask_table.align["我方累积eth"] = 'r'
                print('…………………………………………………………………………………………')
                print('时间：',time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
                result_path = os.getcwd() + '\\msc_results'
                print(result_path)
                if not os.path.exists(result_path):
                    os.mkdir(result_path)
                with open(result_path + '\\' + time.strftime("%Y-%m-%d %H-%M-%S", time.localtime())+'.html', 'w') as f:
#                    f.write('时间：%s<br>买：%d档<br>卖：%d档<br>MSC卖盘:<br>%s<br><br>MSC买盘：<br>%s<br>'%(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()),len(bid_price),len(ask_price),ask_table.get_html_string(sortby="卖价", reversesort=True),bid_table.get_html_string(sortby="买价", reversesort=True)))
                    f.write('<!DOCTYPE html><html><head><style type="text/css">div.ask table {color:#ff5353} div.bid table {color:#06b07c} body {background-color: #1e2b34;color:#e3ecf0;} table {text-align:right;border-collapse:collapse;}table,th,td {border:1px solid #2f3d45;} th {font-size:1.1em} th,td {width:150px}</style></head><body><h1>时间：%s<br>买：%d档<br>卖：%d档</h1><br><h2>MSC卖盘:</h2><br><div class=\"ask\">%s</div><br><br><h2>MSC买盘：</h2><br><div class=\"bid\">%s</div><br></body></html>'%(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime()),len(bid_price),len(ask_price),ask_table.get_html_string(sortby="卖价", reversesort=True),bid_table.get_html_string(sortby="买价", reversesort=True)))
                print(Fore.RED + 'MSC卖盘：\n',Fore.RED + ask_table.get_string(sortby="卖价",reversesort=True)) 
                print(Fore.GREEN +'\n\nMSC买盘：\n',Fore.GREEN + bid_table.get_string(sortby="买价", reversesort=True))
#                print('统计完毕，%d秒后重新获取'%t)
#                time.sleep(t)
                input('统计完毕，已输出到文件，按enter刷新……')
            
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