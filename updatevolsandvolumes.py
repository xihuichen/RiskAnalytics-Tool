# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""

from __future__ import print_function
from __future__ import division
import numpy as np
import pandas as pd
import matplotlib as plt
data=pd.read_excel('G:/Credit Risk/EMEA CRA Team/Xihui/Liquidity Risk Write up/Current_database_replaced0.xlsx','Sheet2')



#data.replace(data['VOLUME'][0],0)
#print(data['VOLUME'][0])

#print(data['NAME'][0] == data['NAME'][1])
"""
for i in range(0,2):
    if data['NAME'][i] == data['NAME'][i+1]:
        print(i)
    else:
        print(i+1)
"""
count=[]


for i in range(0,len(data['NAME'])-1):
    if data['NAME'][i] == data['NAME'][i+1]:
        count.append(1)
        data.loc[i+1,'VOLATILITY']=max(data['VOLATILITY'][i+1],data['VOLATILITY'][i])
        data.loc[i+1,'VOLUME']=data['VOLUME'][i+1]+data['VOLUME'][i]
    else:
        j=sum(count)
        print(j)
        for m in range(i-j,i):
            data.loc[m,'VOLATILITY']=data['VOLATILITY'][i]
            data.loc[m,'VOLUME']=data['VOLUME'][i]
        count=[]
            
data.to_excel('G:/Credit Risk/EMEA CRA Team/Xihui/Liquidity Risk Write up/Current_database_replaced.xlsx', sheet_name='updated')
