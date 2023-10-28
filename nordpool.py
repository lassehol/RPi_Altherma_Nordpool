#!/usr/bin/python
# -*- coding:utf-8 -*-

import RPi.GPIO as GPIO
from entsoe import EntsoePandasClient
import pandas as pd
import csv
import statistics
import datetime
import calendar
import datetime
import requests
from time import sleep
from apscheduler.schedulers.blocking import BlockingScheduler


Relay_Ch1 = 26
Relay_Ch2 = 20
Relay_Ch3 = 21

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)

GPIO.setup(Relay_Ch1,GPIO.OUT)
GPIO.setup(Relay_Ch2,GPIO.OUT)
GPIO.setup(Relay_Ch3,GPIO.OUT)

GPIO.output(Relay_Ch1,GPIO.HIGH)
GPIO.output(Relay_Ch2,GPIO.HIGH)
GPIO.output(Relay_Ch3,GPIO.HIGH)

print("Setup The Relay Module is [success]")

now2 = datetime.datetime.now()
prices = []
average = 0
low2 = 0

def highhour():
    global now2
    global prices
    global average
    faverage = f"{average:.2f}"
    now2 = datetime.datetime.now()
    now_hour = int(now2.strftime("%H"))
    #print(now_hour)
    #print(prices)
    if prices[12] > average:
        print(prices[12]," >= ",faverage)
        return True
    else:
        print(prices[12]," < ",faverage)
        return False
    
def lowhour():
    global now2
    global prices
    global average
    global low2
    now2 = datetime.datetime.now()
    now_hour = int(now2.strftime("%H"))
    #print(now_hour)
    #print(prices)
    if prices[12] <= low2:
        print(prices[12]," <= ",low2)
        return True
    else:
        print(prices[12]," > ",low2)
        return False
        
daikin = "on"

p=1
#try:
def program():
    try:
        global now2
        global prices
        global average
        global low2
        now2 = datetime.datetime.now()
        today = datetime.date.today()
    
        d1 = today.strftime("%Y%m%d")
        m12 = now2 - datetime.timedelta(hours=12)
        p12 = now2 + datetime.timedelta(hours=12)
        t1 = m12.strftime("%Y%m%d%H")
        t2 = p12.strftime("%Y%m%d%H")
        year = int(today.strftime("%Y"))
        month = int(today.strftime("%m"))
        day = int(today.strftime("%d"))
        #print(year, month, day)
        

        #print(d1)

        client = EntsoePandasClient(api_key="1b2c7e55-3c21-45a5-b337-6b9a65fe9bfd")
        start = pd.Timestamp(t1 + '00', tz='Europe/Helsinki')
        #start = pd.Timestamp('20221216'+'0000', tz='Europe/Helsinki')
        end = pd.Timestamp(t2 + '00', tz='Europe/Helsinki')
        #end = pd.Timestamp('20221216'+'2300', tz='Europe/Helsinki')
        country_code = 'FI'  # Finland
        type_marketagreement_type = 'A01'
        contract_marketagreement_type = 'A01'
        

        ts = client.query_day_ahead_prices(country_code, start=start, end=end)
        ts.to_csv('outfile.csv')

        file = open('outfile.csv')
        type(file)

        csvreader = csv.reader(file)

        matrix = []
        for row in csvreader:
            matrix.append(row)
            
        transposed = []
        for i in range(2):
            transposed.append([row[i] for row in matrix])
            
        del transposed[0]
        del transposed[0][0]
        transposed = transposed[0]
        prices = []
        for i in range(len(transposed)):
            prices.append(float(transposed[i]))
        average = sum(prices)/len(prices)
        median = statistics.median(prices)
        res = []

        for idx in range(0, len(prices)):
            if prices[idx] <= median:
                res.append(idx)

        high = max(prices)
        highidx = prices.index(high)
        prices2 = []
        for e in prices:
            prices2.append(e)
        high_prices6=[]
        for e in prices:
            high_prices6.append(e)
        while len(high_prices6) > 6:
            lowidx = high_prices6.index(min(high_prices6))
            del high_prices6[lowidx]
        high2 = min(high_prices6)
        high6idx=[]
        for e in range(len(prices)):
            if prices[e] >= high2 and len(high6idx) < 6:
                high6idx.append(e)
        low_prices6=[]
        for e in prices:
            low_prices6.append(e)
        while len(low_prices6) > 6:
            higidx = low_prices6.index(max(low_prices6))
            del low_prices6[higidx]
        low2 = max(low_prices6)
        print(low2)
        low6idx=[]
        for e in range(len(prices)):
            if prices[e] <= low2 and len(low6idx) < 6:
                low6idx.append(e)
        hightimee = datetime.datetime(year,month,day,highidx,0,0).timestamp()
        now2 = datetime.datetime.now()
        print(high2)

            



        #print(prices)
        #print(average)
        #print(median)
        #print(res)
        print(high6idx)
        print(low6idx)
        #print(hightimee)
        #print(high_prices6)

            

        if highhour():
            print('high')
            GPIO.output(Relay_Ch1,GPIO.HIGH)
            GPIO.output(Relay_Ch2,GPIO.LOW)
            daikin = "off"
            print(now2)
            print(daikin)
            
            
        elif lowhour():
            print('low')
            GPIO.output(Relay_Ch1,GPIO.LOW)
            GPIO.output(Relay_Ch2,GPIO.LOW)
            daikin = "buffer"
            print(now2)
            
        else:
            print('medium')
            GPIO.output(Relay_Ch1,GPIO.HIGH)
            GPIO.output(Relay_Ch2,GPIO.HIGH)
            GPIO.output(Relay_Ch3,GPIO.HIGH)
            daikin = "on"
            print(now2)
            print(daikin)
            
    except:
        GPIO.output(Relay_Ch1,GPIO.HIGH)
        GPIO.output(Relay_Ch2,GPIO.HIGH)
        GPIO.output(Relay_Ch3,GPIO.HIGH)
        daikin = "on"
        print('Something went wrong')
        now2 = datetime.datetime.now()
        print(now2)
        print(daikin)
        
pass
scheduler = BlockingScheduler()
scheduler.add_job(program, 'cron', minute=0)
scheduler.start()
        
    
