# -*- coding: utf-8 -*-
"""
Created on Fri Sep 14 12:58:01 2018

@author: My
"""

import random
import time
from fcoin import Fcoin
from colorama import init,Fore
import sd_hx_dat as dat

min_amount = 3000
max_amount = 6000

symbol = 'msceth'
level = 'L20'

init(autoreset=True) 

sell_keys,sell_secrets,sell_accounts,buy_keys,buy_secrets,buy_accounts,account_name,account_name_buy = [],[],[],[],[],[],[],[]
'''
供货账户0：fanbit
'''
account_name.append('')
sell_keys.append('')
sell_secrets.append('')
f1 = Fcoin()
sell_accounts.append(f1)
sell_accounts[0].auth(sell_keys[0],sell_secrets[0])
'''
供货账户1：bitbcn
'''
account_name.append('')
sell_keys.append()
sell_secrets.append()
f2 = Fcoin()
sell_accounts.append(f2)
sell_accounts[1].auth(sell_keys[1],sell_secrets[1])

'''---------------------------------------------'''
'''---------------------------------------------'''
'''---------------------------------------------'''
'''
进货账户0：fanbit
'''
account_name_buy.append()
buy_keys.append('')
buy_secrets.append('')
bf1 = Fcoin()
buy_accounts.append(bf1)
buy_accounts[0].auth(buy_keys[0],buy_secrets[0])
'''
进货账户1：bitbcn
'''
account_name_buy.append('')
buy_keys.append('')
buy_secrets.append('')
bf2 = Fcoin()
buy_accounts.append(bf2)
buy_accounts[1].auth(buy_keys[1],buy_secrets[1])
'''
进货账户2：fiteth1
'''
account_name_buy.append('')
buy_keys.append('')
buy_secrets.append('')
bf3 = Fcoin()
buy_accounts.append(bf3)
buy_accounts[2].auth(buy_keys[2],buy_secrets[2])


sum_amount = 0.00
in_amount = 0.00
def transport():
    def query_avg():
        try:
            candles =buy_accounts[0].get_candle('M1',symbol,limit=20)
            if candles['status'] != 0:
                print('candles response status is not "0"')
                print(candles)
                print('3秒后重试')
                time.sleep(3)
                return query_avg()
            candles = candles['data']
            closes = 0
            for candle in candles:
                closes += float(candle['close'])
            avg_p = closes/len(candles)
            return avg_p
        except:
            print('请求K线出错，3秒后重试')
            time.sleep(3)
            return query_avg()
    def rest():
        t = 60
        if random.randint(0,4) == 4:
            t = random.randint(20,40)
        else:
            t = random.randint(40,90)
        print('成交结果请手动查看账户。\n休息%d秒后继续……' % t)
        time.sleep(t)
    global sum_amount
    global in_amount
    while True:
        print('----------------------------------------------------')
        print('----------------------------------------------------')
        print('时间：',time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        
#       随机选择供货账户：
        i = random.randint(0,1)
#        i=0
        sell_account = sell_accounts[0]
        if i > 0:
            sell_account = sell_accounts[1]
        ii = random.randint(0,2)
        buy_account = buy_accounts[ii]
        
            
#       随机确定交易数量(整数或浮点数)：
        amount = 0.00
        int_num = random.randint(min_amount,max_amount)
        fl_num = 0.00
        if random.randint(0,2) > 1:
            fl_num = round(random.random(),2)
        amount = int_num + fl_num

#       随机确定买方成交或卖方成交：
        sell_or_buy = random.randint(0,1)

#       获取市场深度：
        depth = {}
        depth = sell_account.get_market_depth(level,symbol)
        if 'data' not in depth:
            print('没有获取到市场深度！\n5秒后重试')
            time.sleep(5)
            continue
        depth = depth['data']
        
#       判断刷单空间是否足够：
        print('区间：','%.8f'%float(depth['bids'][0]),'——','%.8f'%float(depth['asks'][0]))
        print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
#        下方用0.00000002929而不是0.00000003是因为前两个相减计算出来的值会略小于实际的值（计算机计算方法导致）
        if round(float(depth['asks'][0]) - float(depth['bids'][0]),8) < 0.000000029:
            print('买一卖一价差过小，请打开3档或以上的空间。\n2秒后重试')
            time.sleep(2)
            continue

        retry = 0
        dat.sd_set_1()
        while retry < 4:
            hx = dat.get_hx()
            if hx == '1':
                print('正在画线，5秒后重试')
                time.sleep(5)
                retry += 1
                continue
            elif hx == '':
                print('另一程序正在操作')
                time.sleep(1)
                retry += 1
                continue
            elif hx == '0':
                break
            else:
                dat.hx_set_0()
                print('hx.dat内容异常，已置为0')
                return
        if retry >= 4:
            dat.hx_set_0()
            
#       同时防止被卡单出货(轮询十次)：
        print('开始十次轮询，防止被出货')
        for m in range(0,10):
            depth1 = sell_account.get_market_depth(level,symbol)['data']
            if float(depth1['asks'][0]) != float(depth['asks'][0]):
                print('盘面卖单有变，本次刷单中止')
                return
        print('十次轮询没有发现卖单变化')
#       在买一卖一中间随机确定刷单价格：
        price = round(random.uniform(float(depth['bids'][0])+0.00000001,float(depth['asks'][0])-0.00000001),8)
#       判断是否区间过大(大于10)，若过大则看是否被拉高或砸低，被拉高则在高位刷单，被拉低则在低位刷单
        if float(depth['asks'][0]) - float(depth['bids'][0]) > 0.00000010:
            if query_avg() < (float(depth['bids'][0])+float(depth['asks'][0]))/2:
                price = round(random.uniform(float(depth['asks'][0])-0.00000010,float(depth['asks'][0])-0.00000001),8)
            else:
                price = round(random.uniform(float(depth['bids'][0])+0.00000001,float(depth['bids'][0])+0.00000010),8)
                
        if sell_or_buy == 0:
            print('价格：',Fore.GREEN + '%.8f'%price)
        else:
            print('价格：',Fore.RED + '%.8f'%price)
        

#       下卖单和买单：
        if sell_or_buy == 0:
            '''
            先下卖单，如果卖单失败就2秒后重新开始；
            如果卖单成功，买单下单失败则撤卖单后2秒重新开始，撤单失败则停止程序。
            '''
            sell_result = {'status':1}
            buy_result = {'status':1}
            sell_result = sell_account.sell(symbol,price,amount)
            if sell_result['status'] == 0:
                print('先卖，账户',account_name[i],'供货【卖】单下单成功，单量：',Fore.RED + str(amount))
            else:
                print(sell_result)
                print('！！！下单失败：供货【卖】单下单失败，单量：',amount,'\n2秒后重新开始……')
                time.sleep(2)
                dat.sd_set_0()
                continue  
            buy_result = buy_account.buy(symbol,price,amount)     
            if buy_result['status'] == 0:
                print('后买，账户',account_name_buy[ii],'进货【买】单下单成功，单量：',Fore.GREEN + str(amount))
                if ii == 2:
                    in_amount += amount
                sum_amount += amount
                print('总量：%.2fMSC\n进货：%.2fMSC'%(sum_amount,in_amount))
            else:
                print('！！！下单失败：进货【买】单下单失败，单量：',amount,'现在重试……')
                time.sleep(1)
                buy_result = buy_account.buy(symbol,price,amount)     
                if buy_result['status'] == 0:
                    print('后买，账户',account_name_buy[ii],'进货【买】单下单成功，单量：',Fore.GREEN + str(amount))
                    if ii == 2:
                        in_amount += amount
                    sum_amount += amount
                    print('总量：%.2fMSC\n进货：%.2fMSC'%(sum_amount,in_amount))
                else:
                    print('！！！下单失败：进货【买】单下单失败，单量：',amount,'\n现在撤回已下单的卖单……')
                    if sell_account.cancel_order(sell_result['data'])['status'] == 0:
                        print('撤销卖单成功！\n2秒后重新开始……')
                        time.sleep(2)
                        dat.sd_set_0()
                        continue
                    else:
                        print('撤销卖单失败！重新尝试撤单……')
                        time.sleep(1)
                        if sell_account.cancel_order(sell_result['data'])['status'] == 0:
                            print('撤销卖单成功！\n2秒后重新开始……')
                            time.sleep(2)
                            dat.sd_set_0()
                            continue
                        else:
                            print('撤销卖单失败！请手动查看账户后重新开始程序')
                            dat.sd_set_0()
                            break
        else:
            '''
            先下买单，如果买单失败就2秒后重新开始；
            如果买单成功，卖单下单失败则撤买单后2秒重新开始，撤单失败则停止程序。
            '''
            buy_result = {'status':1}
            sell_result = {'status':1}
#            buy_result = buy_account.buy(symbol,price,amount)
            buy_result = buy_account.buy(symbol,price,amount)  
            if buy_result['status'] == 0:
                print('先买，账户',account_name_buy[ii],'进货【买】单下单成功，单量：',Fore.GREEN + str(amount))
            else:
                print(buy_result)
                print('！！！下单失败：进货【买】单下单失败，单量：',amount,'\n2秒后重新开始……')
                time.sleep(2)
                dat.sd_set_0()
                continue
            sell_result = sell_account.sell(symbol,price,amount)
            if sell_result['status'] == 0:
                print('后卖，账户',account_name[i],'供货【卖】单下单成功，单量：',Fore.RED + str(amount))
                if ii == 2:
                    in_amount += amount
                sum_amount += amount
                print('总量：%.2fMSC\n进货：%.2fMSC'%(sum_amount,in_amount))
            else:
                print('！！！下单失败：供货【卖】单下单失败，单量：',amount,'现在重试……')
                time.sleep(1)
                sell_result = sell_account.sell(symbol,price,amount)  
                if sell_result['status'] == 0:
                    print('后卖，账户',account_name[i],'供货【卖】单下单成功，单量：',Fore.RED + str(amount))
                    if ii == 2:
                        in_amount += amount
                    sum_amount += amount
                    print('总量：%.2fMSC\n进货：%.2fMSC'%(sum_amount,in_amount))
                else:
                    print('！！！下单失败：供货【卖】单下单失败，单量：',amount,'\n现在撤回已下单的买单……')
                    if buy_account.cancel_order(buy_result['data'])['status'] == 0:
                        print('撤销买单成功！\n2秒后重新开始……')
                        time.sleep(2)
                        dat.sd_set_0()
                        continue
                    else:
                        print('撤销卖单失败！重新尝试撤单……')
                        time.sleep(1)
                        if buy_account.cancel_order(buy_result['data'])['status'] == 0:
                            print('撤销买单成功！\n2秒后重新开始……')
                            time.sleep(2)
                            dat.sd_set_0()
                            continue
                        else:
                            print('撤销买单失败！请手动查看账户后重新开始程序')
                            dat.sd_set_0()
                            break
            
#       随机休息（1/5概率分布在40到70秒，4/5的概率分布在70到120秒）
#        t = 60
#        if random.randint(0,4) == 4:
#            t = random.randint(40,70)
#        else:
#            t = random.randint(70,120)
#        print('成交结果请手动查看账户。\n休息%d秒后继续……' % t)
#        time.sleep(t)
        time.sleep(3)
        dat.sd_set_0()
        rest()
        
while True:
    try:
        transport()
    except Exception as e:
        print('----------------------------------------------------')
        print('出错了！！！！！！！！\nError:', e)
    except:
        print('----------------------------------------------------')
        print('出错了！！！！！！！！')
    finally:
#      此处可以添加提醒，如提示音。另，下一版本对输出内容作保存，交易可以保存到表
        print('----------------------------------------------------')
        print('\n程序意外停止！\n\n【注意查看买卖单有无错误！】\n\n5秒后重新运行程序...')
        time.sleep(5)
        
#transport()
