#!/usr/bin/env python
#! -*- coding: utf-8 -*-

import requests
import sys
import json

class Stock():

    symbol = ""
    stock_name = ""
    high_price = 0.0
    low_price = 100_000_000.0
    price = 0.0
    prev_close = 0.0
    diff = 0.0

    def __init__(self, symbol, stock_name):
        
        self.symbol = symbol
        self.stock_name = stock_name


    def update(self):
        
        url = "https://query1.finance.yahoo.com/v7/finance/chart/{s}?interval=1d".format(s=self.symbol)

        timeout = 10
        # need to have good user agent
        headers = {'User-agent': "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36"}
        stock_json = {}
        try:
            r = requests.get(url, headers=headers, timeout=timeout)
            # 403 = forbidden
            stock_json = json.loads(r.text)
        except requests.exceptions.RequestException:
            print("Stock - Request exception")

        except requests.exceptions.Timeout:
            print("Stock - Request timeout")
        except requests.exceptions.TooManyRedirects:
            print("Stock - Request too many redirects")
        except json.decoder.JSONDecodeError:
            print("Stock - json decode error")
            
        #print("status: {}".format(r.status_code))

        #stock_json = json.loads(r.text)
        if stock_json.get("chart"):
                
            price_result = stock_json.get('chart', {}).get('result', [])

            if price_result:
                price = price_result[0].get("meta", {}).get("regularMarketPrice", 0.0)
                prev_close = price_result[0].get("meta", {}).get("chartPreviousClose", 0.0)
                if prev_close > 0:
                    self.prev_close = prev_close
                    
                if price > 0:
                    self.price = price
                if price > self.high_price:
                    self.high_price = price
                if price < self.low_price:
                    self.low_price = price

                self.diff = self.price - self.prev_close

            #print(json.dumps(stock_json, indent=2))

    def __str__(self):
        plus_str = "+" if float(self.diff) > 0.0 else ""

        stock_msg = "{}: {:.2f} {}{:.2f}".format(self.stock_name, float(self.price), plus_str, float(self.diff))
        return stock_msg
    
    
    #def __repr__(self):
    #    return ""

if __name__ == '__main__':
    #Bitcoin USD (BTC-USD), oil = CL=F
    s_list = ["GOOGL", "BRK-A", "^DJI", "^SPX", "^IXIC", "BTC-USD", "CL=F", "GC=F"]
    so_list = []
    for s in s_list:
        s = Stock(s, "X")
        so_list.append(s)

    for so in so_list:
        so.update()
        print("Stock: {} ({}), price: {}, {}".format(so.stock_name, so.symbol, so.price, so.diff))    
        print("- {}".format(so))
    
    
    sys.exit(0)

