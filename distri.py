# -*- coding: utf-8 -*-
"""
Created on Tue Feb 14 18:32:50 2017

@author: hm08400
"""

import numpy as np
import pandas as pd
from scipy import stats


def get_Stat(data,binn=None):
    if not binn:
        binn = 50
    histData = np.histogram(data,bins = binn,density=True)
    tt = histData[1][:-1]
    tmp = {'Variable':tt,'Prob':histData[0]}
    dx = histData[1][1] - histData[1][0]
    tmp['Cumulative'] = np.cumsum(histData[0])*dx
    return tmp
    
def dist_xlsx(writer,data, ProbType):
    
    
    title = ['Statistics']
    indd = ['mean','std','skew','kurtosis']
    fff = []
    fff = [np.mean(data),np.std(data),stats.skew(data),stats.kurtosis(data)]  
   
    df = pd.DataFrame(fff,columns = title, index = indd)
    df.to_excel(writer, sheet_name=ProbType, startcol = 0, startrow = 1  ,index=True)
    
    StatData = get_Stat(data)
    title = ['Variable','Prob','Cumulative']
    df = pd.DataFrame.from_records(StatData,columns = title)
    position = [3,1]
    df.to_excel(writer, sheet_name=ProbType, startcol = position[0], startrow = position[1]  ,index=True)
     
    Ytarget = 'Cumulative'
    Xtarget = 'Variable'
    workbook = writer.book
    worksheet = writer.sheets[ProbType]
    chart = workbook.add_chart({'type': 'scatter'})
    
    colY = title.index(Ytarget) + position[0]+ 1
    colX = title.index(Xtarget) + position[0]+ 1
    max_row = len(StatData[Xtarget])
    chart.add_series({
            'name':       [ProbType, position[1], colY],
            'categories': [ProbType, position[1]+1, colX, position[1] + max_row, colX],
            'values':     [ProbType, position[1]+1, colY,  position[1] + max_row, colY],
            'marker':     {'type': 'circle', 'size': 7},
        })
    
    chart.set_x_axis({'name': 'X'})
    chart.set_y_axis({'name': Ytarget,
                      'major_gridlines': {'visible': False}})
    worksheet.insert_chart('J2', chart)
    
    Ytarget = 'Prob'
    Xtarget = 'Variable'
    workbook = writer.book
    worksheet = writer.sheets[ProbType]
    chart = workbook.add_chart({'type': 'scatter'})
    
    colY = title.index(Ytarget) + position[0]+ 1
    colX = title.index(Xtarget) + position[0]+ 1
    max_row = len(StatData[Xtarget])
    chart.add_series({
            'name':       [ProbType, position[1], colY],
            'categories': [ProbType, position[1]+1, colX, position[1] + max_row, colX],
            'values':     [ProbType, position[1]+1, colY,  position[1] + max_row, colY],
            'marker':     {'type': 'circle', 'size': 7},
        })
    
    chart.set_x_axis({'name': 'X'})
    chart.set_y_axis({'name': Ytarget,
                      'major_gridlines': {'visible': False}})
    worksheet.insert_chart('J20', chart)


    

N = 100000
writer = pd.ExcelWriter('DistExample.xlsx',engine='xlsxwriter')

m = 0
st = 1
data = np.random.normal(m,st,N)
dist_xlsx(writer,data, 'Normal')

m = 1.0
st = 0.28
data = np.random.lognormal(m,st,N)
dist_xlsx(writer,data, 'LogNormal')


alp = 1.1
xm = 2
data = (np.random.pareto(alp,N) + 1 )*xm
dist_xlsx(writer,data, 'Pareto')

writer.save()

