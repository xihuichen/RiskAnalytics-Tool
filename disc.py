# -*- coding: utf-8 -*-
"""
Created on Fri Jul 20 10:35:50 2018

@author: xc36456
"""
import sys
sys.path.append(r'I:\corridor varswap confirm')
import csv
import pandas as pd
import datetime
from datetime import timedelta
from pandas.tseries.offsets import BDay

df=pd.read_excel("I:\corridor varswap confirm\spxhsci.xls")
df=df.dropna()
upper=1
lower=0.6

start = df['Date'][0] - BDay(3*261)
start = start.date()


df['just_date'] = df['Date'].dt.date
calc_start= start - BDay(3*261) 
calc_start = calc_start.date()
index = df[df['just_date']==start].index.values[0]
loc=df.index.get_loc(index)
index2=df[df['just_date']==calc_start].index.values[0]
endloc=df.index.get_loc(index2)
endloc2=df.index.get_loc(1566)

date=[]
conditiondays=[]
corridor_disc=[]


for i in range(0,loc):
    d=df.iloc[loc-i]['just_date']
    date.append(d)
    corridor_up = upper * df.iloc[endloc2-i]['.HSCE, Index Level']
    corridor_down = lower * df.iloc[endloc2-i]['.HSCE, Index Level']
    dftrunc=df.truncate(before=loc-i,after=endloc2-i)
#==============================================================================
#     corridor_up = upper * df.get_value(index2.values[0]-i,'.HSCE, Index Level')
#     corridor_down=lower * df.get_value(index2.values[0]-i,'.HSCE, Index Level')
#     dftrunc=df.truncate(before=index.values[0]-i,after=index2.values[0]-i)
#==============================================================================
    condition=dftrunc[(dftrunc['.HSCE, Index Level']<=corridor_up) &(dftrunc['.HSCE, Index Level']>=corridor_down)].count()['.HSCE, Index Level']
    print(condition)
    temp=float(condition)/dftrunc.count()['.HSCE, Index Level']
    conditiondays.append(condition)
    corridor_disc.append(temp)

record=pd.DataFrame([date,corridor_disc])
record=record.T
writer=pd.ExcelWriter('disc.xls')
record.to_excel(writer,'Sheet1')  
writer.save()  