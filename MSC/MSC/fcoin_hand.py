import hashlib
import requests
import time
import base64
import hmac
import random
from colorama import init,Fore
import sd_hx_dat as dat
init(autoreset=True) 

class Fcoin():
    def __init__(self,base_url = 'https://api.fcoin.com/v2/'):
        self.base_url = base_url

    def auth(self, key, secret):
        self.key = bytes(key,'utf-8') 
        self.secret = bytes(secret, 'utf-8') 


    def public_request(self, method, api_url, **payload):
        """request public url"""
        r_url = self.base_url + api_url
        try:
            r = requests.request(method, r_url, params=payload)
            r.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)
        if r.status_code == 200:
            return r.json()

    def get_signed(self, sig_str):
        """signed params use sha512"""
        sig_str = base64.b64encode(sig_str)
        signature = base64.b64encode(hmac.new(self.secret, sig_str, digestmod=hashlib.sha1).digest())
        return signature


    def signed_request(self, method, api_url, **payload):
        """request a signed url"""

        param=''
        if payload:
            sort_pay = sorted(payload.items())
            #sort_pay.sort()
            for k in sort_pay:
                param += '&' + str(k[0]) + '=' + str(k[1])
            param = param.lstrip('&')
        timestamp = str(int(time.time() * 1000))
        full_url = self.base_url + api_url

        if method == 'GET':
            if param:
                full_url = full_url + '?' +param
            sig_str = method + full_url + timestamp
        elif method == 'POST':
            sig_str = method + full_url + timestamp + param

        signature = self.get_signed(bytes(sig_str, 'utf-8'))

        headers = {
            'FC-ACCESS-KEY': self.key,
            'FC-ACCESS-SIGNATURE': signature,
            'FC-ACCESS-TIMESTAMP': timestamp

        }

        try:
            r = requests.request(method, full_url, headers = headers, json=payload)

            r.raise_for_status()
        except requests.exceptions.HTTPError as err:
            print(err)
            print(r.text)
        if r.status_code == 200:
            return r.json()


    def get_server_time(self):
        """Get server time"""
        return self.public_request('GET','/public/server-time')['data']


    def get_currencies(self):
        """get all currencies"""
        return self.public_request('GET', '/public/currencies')['data']

    def get_symbols(self):
        """get all symbols"""
        return self.public_request('GET', '/public/symbols')['data']

    def get_market_ticker(self, symbol):
        """get market ticker"""
        return self.public_request('GET', 'market/ticker/{symbol}'.format(symbol=symbol))

    def get_market_depth(self, level, symbol):
        """get market depth"""
        return self.public_request('GET', 'market/depth/{level}/{symbol}'.format(level=level, symbol=symbol))

    def get_trades(self,symbol):
        """get detail trade"""
        return self.public_request('GET', 'market/trades/{symbol}'.format(symbol=symbol))

    def get_balance(self):
        """get user balance"""
        return self.signed_request('GET', 'accounts/balance')

    def list_orders(self, **payload):
#x=fcoin.list_orders(symbol = 'datxeth',states = 'submitted')
        """get orders"""
        return self.signed_request('GET','orders', **payload)

    def create_order(self, **payload):
        """create order"""
        return self.signed_request('POST','orders', **payload)

    def buy(self,symbol, price, amount):
        """buy someting"""
        return self.create_order(symbol=symbol, side='buy', type='limit', price=str(price), amount=amount)

    def sell(self, symbol, price, amount):
        """sell someting"""
        return self.create_order(symbol=symbol, side='sell', type='limit', price=str(price), amount=amount)

    def get_order(self,order_id):
        """get specfic order"""
        return self.signed_request('GET', 'orders/{order_id}'.format(order_id=order_id))

    def cancel_order(self,order_id):
        """cancel specfic order"""
        return self.signed_request('POST', 'orders/{order_id}/submit-cancel'.format(order_id=order_id))

    def order_result(self, order_id):
        """check order result"""
        return self.signed_request('GET', 'orders/{order_id}/match-results'.format(order_id=order_id))
    def get_candle(self,resolution, symbol, **payload):
        """get candle data"""
        return self.public_request('GET', 'market/candles/{resolution}/{symbol}'.format(resolution=resolution, symbol=symbol), **payload)
    
    
class market_adjust():
    def __init__(self,symbol,is_quiet = False):
        self.fcoin = Fcoin()
        self.symbol = symbol
        self.is_quiet = is_quiet
    def auth(self,key,secret):
        self.fcoin.auth(key,secret)
    def adjust(self,k):
        print('时间：',time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()))
        if k == 0:
            return 0
        elif k > 0 and k < 10:
            retry = 0
            dat.hx_set_1()
            while retry < 4:
                sd = dat.get_sd()
                if sd == '1':
                    print('正在刷单，5秒后重试')
                    time.sleep(5)
                    retry += 1
                    continue
                elif sd == '':
                    print('另一程序正在操作')
                    time.sleep(1)
                    retry += 1
                    continue
                elif sd == '0':
                    break
                else:
                    dat.sd_set_0()
                    print('sd.dat内容异常，已置为0')
                    break
            if retry >= 4:
                dat.sd_set_0()
            depth = self.fcoin.get_market_depth('L20',self.symbol)
#            print(depth)
            if depth['status'] == 0:
                market_bid_price,market_ask_price = float(depth['data']['bids'][0]),float(depth['data']['asks'][0])
                goal_bid_price,goal_ask_price = round(market_bid_price + k/100000000,8),round(market_ask_price+ k/100000000,8)
                print('调整后卖一:',Fore.RED+'%.8f'%goal_ask_price)
                print('调整后买一:',Fore.GREEN+'%.8f'%goal_bid_price)
#                监控盘面区间大小是否正常(小于3档或大于15档)
                if round(goal_ask_price - goal_bid_price,8) < (29/1000000000):
                    dat.hx_set_0()
                    print(Fore.BLUE + '区间太小')
                    print('\a')
                    time.sleep(1)
                    print('\a')
                    time.sleep(1)
                    print('\a')
                    if input('解决后输入1继续：') == '1':
                        return self.adjust(k)
                    else:
                        return -7
                if round(goal_ask_price - goal_bid_price,8) > (200/1000000000):
                    dat.hx_set_0()
                    print(Fore.BLUE + '区间太大')
                    print('\a')
                    time.sleep(1)
                    print('\a')
                    time.sleep(1)
                    print('\a')
                    if input('解决后输入1继续：') == '1':
                        return self.adjust(k)
                    else:
                        return -7
                if not self.is_quiet:
                    print(Fore.YELLOW + '输入1确认：')
                    if input() != '1':
                        print('行动取消')
                        return -2
                orders = self.fcoin.list_orders(symbol=self.symbol,states='submitted,partial_filled',limit='1000')
                orders = orders['data']
                has_sell_order = False
                for order_unit in orders:
                    if order_unit['side'] == 'sell' and round(float(order_unit['price']),8) == goal_ask_price and round(float(order_unit['amount'])-float(order_unit['filled_amount']),2) > 300:
                        has_sell_order = True
                    if k != 1:
                        if order_unit['side'] == 'sell' and float(order_unit['price']) < goal_ask_price and round(float(order_unit['amount'])-float(order_unit['filled_amount']),2) < 2001:
                            if round(float(order_unit['price']),8) != round(goal_ask_price-0.00000002,8):
                                print('cancel order ',order_unit['id'],'price',order_unit['price'])
                                self.fcoin.cancel_order(order_unit['id'])
                time.sleep(2)
                depth = self.fcoin.get_market_depth('L20',self.symbol)
                bid_amount = round(random.randint(200,460) + random.random(),2)
                ask_amount = round(random.randint(200,460) + random.random(),2)
                market_ask_amount = 0.0
                i = 0
                while True:
                    if float(depth['data']['asks'][2*i]) < goal_ask_price:
                        market_ask_amount += depth['data']['asks'][2*i+1]
                        i += 1
                    else:
                        break
                if market_ask_amount < 100 and market_ask_amount > 0:
#                    market_ask_amount = round((random.randint(500,600)+random.random()),2)
                    market_ask_amount = round((random.randint(100,200)+random.random()),2)
#                market_ask_amount = round(market_ask_amount+1,2)
                print('ask_amount:%.2f'%ask_amount)
                print('bid_amount:%.2f'%bid_amount)
#                print('上方阻力:%.2f'%(market_ask_amount-1))
                print('上方阻力:%.2f'%(market_ask_amount))
                if not self.is_quiet:
                    print(Fore.YELLOW + '请确认上方是否为我方委托，输入1确认：')
                    if input() != '1':
                        print('行动取消')
                        return -2
                if market_ask_amount >= 1000:
                    dat.hx_set_0()
                    print('\a')
                    time.sleep(1)
                    print('\a')
                    time.sleep(1)
                    print('\a')
                    print(Fore.YELLOW + '吃单大于一千，输入1确认：')
                    if input() != '1':
                        print('行动取消')
                        return -2
                if market_ask_amount > 1:
                    print('吃卖单：buy',market_ask_amount,'at','%.8f'%goal_ask_price)
                    buy_result1 = self.fcoin.buy(self.symbol,goal_ask_price,market_ask_amount)
                    if buy_result1['status'] != 0:
                        print(Fore.BLUE + '下吃单买单失败')
                        return -5
                print('下买一单：buy',bid_amount,'at','%.8f'%goal_bid_price)
                time.sleep(1)
                buy_result = self.fcoin.buy(self.symbol,goal_bid_price,bid_amount)
                if buy_result['status'] != 0:
                    print(Fore.BLUE + '下买一单失败')
                    time.sleep(1)
                    buy_result = self.fcoin.buy(self.symbol,goal_bid_price,bid_amount)
                    if buy_result['status'] != 0:
                        print(Fore.BLUE + '下买一单失败')
                        return -5
                    print('重新下买一单成功')
                time.sleep(1)
                if not has_sell_order:
                    print('下卖一单：sell',ask_amount,'at','%.8f'%goal_ask_price)
                    sell_result = self.fcoin.sell(self.symbol,goal_ask_price,ask_amount)
                    if sell_result['status'] != 0:
                        print(Fore.BLUE + '下卖一单失败')
                        time.sleep(1)
                        sell_result = self.fcoin.sell(self.symbol,goal_ask_price,ask_amount)
                        if sell_result['status'] != 0:
                            print(Fore.BLUE + '下卖一单失败')
                            return -5
                        print('重新下卖一单成功')
                print('三个订单下单成功，三秒后查询调整结果')
                time.sleep(3)
                depth1 = self.fcoin.get_market_depth('L20',self.symbol)
                if depth1['status'] == 0:
                    if float(depth1['data']['bids'][0]) == goal_bid_price and float(depth1['data']['asks'][0]) == goal_ask_price:
                        print('调整成功')
                        return 0
                    else:
                        print(Fore.BLUE + '调整失败')
                        return-4
                else:
                    print(Fore.BLUE + '获取深度失败')
                    return -6
            else:
                print('depth status is not "0"')
                return -3
        elif k < 0 and k > -10:
            retry = 0
            dat.hx_set_1()
            while retry < 4:
                sd = dat.get_sd()
                if sd == '1':
                    print('正在刷单，5秒后重试')
                    time.sleep(5)
                    retry += 1
                    continue
                elif sd == '':
                    print('另一程序正在操作')
                    time.sleep(1)
                    retry += 1
                    continue
                elif sd == '0':
                    break
                else:
                    dat.sd_set_0()
                    print('sd.dat内容异常，已置为0')
                    break
            if retry >= 4:
                dat.sd_set_0()
            depth = self.fcoin.get_market_depth('L20',self.symbol)
#            print(depth)
            if depth['status'] == 0:
                market_bid_price,market_ask_price = float(depth['data']['bids'][0]),float(depth['data']['asks'][0])
                goal_bid_price,goal_ask_price = round(market_bid_price + k/100000000,8),round(market_ask_price+ k/100000000,8)
                print('调整后卖一:',Fore.RED+'%.8f'%goal_ask_price)
                print('调整后买一:',Fore.GREEN+'%.8f'%goal_bid_price)
#                监控盘面区间大小是否正常
                if round(goal_ask_price - goal_bid_price,8) < (29/1000000000):
                    dat.hx_set_0()
                    print(Fore.BLUE + '区间太小')
                    print('\a')
                    time.sleep(1)
                    print('\a')
                    time.sleep(1)
                    print('\a')
                    if input('解决后输入1继续：') == '1':
                        return self.adjust(k)
                    else:
                        return -7
                if round(goal_ask_price - goal_bid_price,8) > (200/1000000000):
                    dat.hx_set_0()
                    print(Fore.BLUE + '区间太大')
                    print('\a')
                    time.sleep(1)
                    print('\a')
                    time.sleep(1)
                    print('\a')
                    if input('解决后输入1继续：') == '1':
                        return self.adjust(k)
                    else:
                        return -7
                if not self.is_quiet:
                    print(Fore.YELLOW + '输入1确认：')
                    if input() != '1':
                        print('行动取消')
                        return -2
                    
                    
                orders = self.fcoin.list_orders(symbol=self.symbol,states='submitted,partial_filled',limit='1000')
                orders = orders['data']
                has_buy_order = False
                for order_unit in orders:
                    if order_unit['side'] == 'buy' and round(float(order_unit['price']),8) == goal_bid_price and round(float(order_unit['amount'])-float(order_unit['filled_amount']),2) > 300:
                        has_buy_order = True
                    if k != -1:
                        if order_unit['side'] == 'buy' and float(order_unit['price']) > goal_bid_price and round(float(order_unit['amount'])-float(order_unit['filled_amount']),2) < 2001:
                            if round(float(order_unit['price']),8) != round(goal_bid_price+0.00000002,8):
                                print('cancel order ',order_unit['id'],'price',order_unit['price'])
                                self.fcoin.cancel_order(order_unit['id'])

                time.sleep(2)
                depth = self.fcoin.get_market_depth('L20',self.symbol)
                bid_amount = round(random.randint(200,460) + random.random(),2)
                ask_amount = round(random.randint(200,460) + random.random(),2)
                market_bid_amount = 0.0
                i = 0
                while True:
                    if float(depth['data']['bids'][2*i]) > goal_bid_price:
                        market_bid_amount += depth['data']['bids'][2*i+1]
                        i += 1
                    else:
                        break
                if market_bid_amount < 100 and market_bid_amount > 0:
#                    market_bid_amount = round((random.randint(500,600)+random.random()),2)
                    market_bid_amount = round((random.randint(100,200)+random.random()),2)
#                market_bid_amount = round(market_bid_amount+1,2)
                print('ask_amount:%.2f'%ask_amount)
                print('bid_amount:%.2f'%bid_amount)
#                print('下方阻力:%.2f'%(market_bid_amount-1))
                print('下方阻力:%.2f'%(market_bid_amount))
                if not self.is_quiet:
                    print(Fore.YELLOW + '请确认下方是否为我方委托，输入1确认：')
                    if input() != '1':
                        print('行动取消')
                        return -2
                if market_bid_amount >= 1000:
                    dat.hx_set_0()
                    print('\a')
                    time.sleep(1)
                    print('\a')
                    time.sleep(1)
                    print('\a')
                    print(Fore.YELLOW + '吃单大于一千，输入1确认：')
                    if input() != '1':
                        print('行动取消')
                        return -2
                if market_bid_amount > 2:
                    print('吃买单：sell',market_bid_amount,'at','%.8f'%goal_bid_price)
                    sell_result1 = self.fcoin.sell(self.symbol,goal_bid_price,market_bid_amount)
                    if sell_result1['status'] != 0:
                        print(Fore.BLUE + '下吃单卖单失败')
                        print(sell_result1)
                        return -5
                time.sleep(1)
                print('下卖一单：sell',ask_amount,'at','%.8f'%goal_ask_price)
                sell_result = self.fcoin.sell(self.symbol,goal_ask_price,ask_amount)
                if sell_result['status'] != 0:
                    print(Fore.BLUE + '下卖一单失败')
                    print(sell_result)
                    time.sleep(1)
                    sell_result = self.fcoin.sell(self.symbol,goal_ask_price,ask_amount)
                    if sell_result['status'] != 0:
                        print(Fore.BLUE + '下卖一单失败')
                        return -5
                    print('重新下卖一单成功')
                time.sleep(1)
                if not has_buy_order:
                    print('下买一单：buy',bid_amount,'at','%.8f'%goal_bid_price)
                    buy_result = self.fcoin.buy(self.symbol,goal_bid_price,bid_amount)
                    if buy_result['status'] != 0:
                        print(Fore.BLUE + '下买一单失败')
                        time.sleep(1)
                        buy_result = self.fcoin.buy(self.symbol,goal_bid_price,bid_amount)
                        if buy_result['status'] != 0:
                            print(Fore.BLUE + '下买一单失败')
                            return -5
                        print('重新下买一单成功')

                print('三个订单下单成功，三秒后查询调整结果')
                time.sleep(3)
                depth1 = self.fcoin.get_market_depth('L20',self.symbol)
                if depth1['status'] == 0:
                    if float(depth1['data']['bids'][0]) == goal_bid_price and float(depth1['data']['asks'][0]) == goal_ask_price:
                        print('调整成功')
                        return 0
                    else:
                        print(Fore.BLUE + '调整失败')
                        return-4
                else:
                    print(Fore.BLUE + '获取深度失败')
                    return -6
            else:
                print(Fore.BLUE + 'depth status is not "0"')
                return -3
        else:
            print('调整量错误,应该在-9到9之间')
            return -1
        
