# -*- coding: utf-8 -*-
"""
Simple MC tool for whale options, static volatility

"""
import sys
sys.path.append(r'I:\trial\whale option')
import numpy as np
import matplotlib.pyplot as plt
from RNG import RNGenerator
#==============================================================================
# from pricer import eq
# from pricer import eqEO
# from pricer import eqAT
# from pricer import eqDD
from tradeslist import tradeslist
from tradeslist import RSoption
from tradeslist import WhaleOption
# from tradeslist import Autocall
# from tradeslist import DDoption
#==============================================================================

from datetime import date
from datetime import timedelta
import math
import copy as copy
from PFE import PFEs
import matplotlib.pyplot as plt
import csv
r=np.array([[1]])
rnseed=12345

numOPath=10
InterestRate = 0.01
today = date.today()
dealdate = today
terminationdate = date(2021, 7, 13)
step=7
d = terminationdate-today
steps = int(math.ceil((float(d.days))/float(step)))

randomvariables = RNGenerator(r, rnseed ,numOPath , steps)

# Here if we simulate strikes and stock prices together that would be more convinient.
trade=[]
""" here we can define trade type = put, call, strangle
"""
def discount(inputmatirx,discto):
    #print(inputmatirx[:,0])
    #if(inputmatirx[:,2].max()> 0):
    #    print('error, buy put < 0')
    #    return 0.12345
    return (inputmatirx[:,0].mean()+inputmatirx[:,2].mean())




def simulateStock(p0,marketdata,today,step,steps,eq_vol):
    """ From the trade termsheets we received before, the option always stays OTM and the restriking always 
    tries to pull delta closer to one when the spot trend is pushing the option further OTM.  
    for puts, the option strike = initial strike + max(0, the increase of the stock if it is greater than threshold)
    for calls, when the underlying price drops: the option strike = initial + min(0, the drop of stock if it is greater than the threshold)
    """
    
    
    [m, n] = marketdata[0].shape
    ONEs = np.ones(n)
    newpricenode = ONEs    
    for j in range(0,steps):
        # remaining days in year
        #BS_T = ((trade.getterminationdate() - today).days - j * step) /365.25    
        
        #newpricepass = []
        #todayprice = marketdata[j][trade.getassetid()]        
        
        if(j == 0):
            newprice = ONEs * np.exp(-0.5*(eq_vol**2)*step/365.25 + np.array(marketdata[j])*eq_vol*((step/365.25)**.5))
            #newpricenode = np.array(newprice)
            newpricenode = np.vstack((newpricenode, newprice))
            #print('size ',newpricenode.shape,'j = ',j)
        else:
            #print(newpricenode[j-1])
            #print(np.array(marketdata[j][trade.getassetid()]))
            if(newpricenode.ndim == 1):
                newprice = newpricenode*np.exp(-0.5*(eq_vol**2)*step/365.25+np.array(marketdata[j])*eq_vol*((step/365.25)**.5))
            else:
                newprice = newpricenode[j,:]*np.exp(-0.5*(eq_vol**2)*step/365.25+np.array(marketdata[j])*eq_vol*((step/365.25)**.5))
                #print('newpricenode[j-1,:]' , newpricenode[j-1,0],'newprice',newprice[0])
            newpricenode =np.vstack((newpricenode, newprice))
    newpricenode=p0*newpricenode
    return newpricenode

def SimOptionPriceWO(trade,randomvariables,spotpricePaths,step,steps,vol):
    '''I want to define a new function that can simulate from spot price("today"'s price)
    step: what step we are on today
    steps: how many steps are there until maturity
    '''
    p0=trade.getp0()
    observation=trade.getobs()
    obs=math.floor(observation/step) 
    '''note here we get the observation is how many times of step length'''
    K=trade.getstrike()
    initialPrice=trade.getp0()
    threshold=trade.getthreshold()
    [m,n]=spotpricePaths.shape
#    print('spot',[m,n])
    
    spotprice=spotpricePaths[m-1,:]
    newpricemtx=[]
    payoff=[[]]
    for i in range(0,steps):
        PriceDate= today+timedelta(days=step*i)
        if i==0:
            newprice = spotprice * np.exp(-0.5*(vol**2)*step/365.25 + np.array(randomvariables[i])*vol*((step/365.25)**.5))
            newpricemtx = np.vstack((spotprice,newprice))
            
        else:
            #print(newpricenode[j-1])
            #print(np.array(marketdata[j][trade.getassetid()]))
            newprice = newpricemtx[i,:]*np.exp(-0.5*(vol**2)*step/365.25+np.array(randomvariables[i])*vol*((step/365.25)**.5))
                #print('newpricenode[j-1,:]' , newpricenode[j-1,0],'newprice',newprice[0])
            newpricemtx =np.vstack((newpricemtx, newprice))
    '''NOTE HERE I HAVE TO GET MAX PRICE AND MIN PRICE OF EACH PATH, IT IS TRICKY, NEED TO INCLUDE PREVIOUS PRICES'''        
#    print('newpricemtx',newpricemtx.shape)
#    wholemtx=np.vstack((spotpricePaths,newpricemtx))
#    print('whole',wholemtx.shape)
#    observed=wholemtx[::obs,:]
    cp = trade.getcp()
    
    if cp == -1:
            
       
        payoff=np.maximum(np.zeros(numOPath), (K - newpricemtx[steps-1,:])*(K/newpricemtx[steps-1,:]))
    elif cp == 1 :
        
        payoff=np.maximum(np.zeros(numOPath), (newpricemtx[steps-1,:]- K )*(newpricemtx[steps-1,:]/K))
             
             
         
    print(payoff.shape)
#    payoff=discount(payoff, priceDate) 
    optionprice=np.average(payoff)
#==============================================================================
#         payoffmtx=np.vstack((payoffmtx,payoff))        
#==============================================================================
    return optionprice   
    

#==============================================================================
# def Getstrike(trade,initial_strike, todayPrice):
#     
#     cp = trade.getcp()
#     if cp == 'put':
#                 today_strike = initial_strike + threshold * max(0, math.floor((todayPrice - initialPrice)/threshold))
#     if cp =='call':
#                 today_strike = initial_strike + threshold * min(0, math.floor((initialPrice-todayPrice)/threshold))   
#==============================================================================
def priceWhaleOption(trade, newpricenode, today,step,steps,vol,randomvariables):
    ls = 0
    #print(trade.getls())
    if('l' == trade.getls()):
        ls = 1.0
    if('s' == trade.getls()):
        ls = -1.0
    try:
        if(len(trade.getsettlement())>1):
            Autofag = 1
    except:
        Autofag = 0

    
#==============================================================================
#     
#     settlementsteps = []
#     for getsettlementarray in range(0,len(trade.getsettlement())):
#         
#         settlementsteps.append(int(math.ceil((float(((trade.getsettlement()[getsettlementarray]-today)).days))/float(step))))
# 
#==============================================================================
    
    price0 = []
    
    #print(temp, temp.shape)
    
    
    
    #print('len(newpricenode[0]',len(newpricenode[0]))
    price0npath = []
    #print(newpricenode[0])
    #for pathloop in range(0, len(newpricenode[0,:])):
    for pathloop in range(0,len(newpricenode[0,:])):
        price0node = []
        terminatePath = steps+1
        payment = []
#        lenofsteps = len(settlementsteps)  
        price0node0 = []
#        print('newpricenodeAMC',newpricenodeAMC.shape)
        for j in range(0,steps):
            priceDate = today+timedelta(days=step*j)
            '''here I need to change today price to include previous price'''
            todayPrice = newpricenode[j,:]
            todayPricePath = newpricenode[:j+1,:]
            k = priceDate
#==============================================================================
#             todayPricePath = todayPrice[0][0][pathloop]
# 
#==============================================================================
#            print(j)
            payoff = SimOptionPriceWO(trade,randomvariables,todayPricePath,step,steps-j,vol)
#            price0node0=discount(payoff,priceDate)
             
            '''
            
            temp = np.zeros((len(newpricenode[0,j,:]), 3)) #here needs get notional, function from tradeslist.py
            temp[:,] = (trade.getnotional(), nostrike,0)
            #print('temp',temp.shape)            
            furturedays = int(math.ceil((float((trade.getsettlement()[0]-k).days))/float(step)))
            for noasset in range(0, len(trade.getstrike())):
                #print(todayPricePath[noasset].shape,newpricenodeAMC[noasset,furturedays,:].shape)
                #print(temp.shape)
#                print(temp)
#                print(noasset)
                if(trade.getcp()[noasset] == 1) :
                    temp[(todayPricePath[noasset]*newpricenodeAMC[noasset,furturedays,:]*100 < trade.getstrike()[noasset]) \
                    * (temp[:,1] == nostrike)] \
                    = (0,noasset,0) 
#                    print(1,nostrike,trade.getstrike()[noasset],todayPricePath[noasset])
                else:
#                    print(todayPricePath[noasset],newpricenodeAMC[noasset,furturedays,:],trade.getstrike()[noasset])
                    temp[(todayPricePath[noasset]*newpricenodeAMC[noasset,furturedays,:]*100 > trade.getstrike()[noasset]) \
                    * (temp[:,1] == nostrike)] \
                    = (0,noasset,0)
#                    print(-1,nostrike,trade.getstrike()[noasset],todayPricePath[noasset])
#                print(temp)
#            print(temp)
            
            price0node0 = discount(temp, priceDate)
            price0node.append(price0node0)
            
            '''
           
            price0node.append(payoff)
            
            
                
        
        price0node = np.asarray(price0node)
#        print(price0node.shape)
        
        price0npath.append(price0node)
#        print('price0npath',len(price0npath))
#    price0 = newpricenode[j,:]
    price0npath=ls*price0npath
    price0 = np.asarray(price0npath)
#    print('price0',price0.shape)
    #print('price0 = ',price0,'priceDate',priceDate)
    return np.array(np.swapaxes(price0,0,1)) #originally price0
#def __init__(self, ls, id, settlement, callput, strike, nnotional,inputterminationdate,p0=100,inputdealdate=date.today())  
#tradeslist.__init__(self, ls, id, nnotional,inputterminationdate,p0=100,inputdealdate=date.today())  
def price(newTrade0, vol):
    '''here I add a new function: display option delta, possible extension:gamma?'''
    #here we define the simulation step lenth
    step = 7
              
    #here we define the number of path in simulation
#    numOPath = 1000      
#==============================================================================
#     #here we define the randam seed
#     rnseed = 1234567
#     #InterestRate is not simulated
#     InterestRate = 0.01
#     today = date.today()
#     dealdate = today
#     terminationdate = date(2020, 12, 5)
# #    terminationdate = newTrade0[8]
#     d = terminationdate-today
#     steps = int(math.ceil((float(d.days))/float(step)))
#==============================================================================
#    cp = 'put'
#    threshold=0.05
#    observation = 0.25 *365.25
    r=np.array([[1]])
    rnseed=12345
    rnseed2=50020
    numOPath=10
    InterestRate = 0.01
    today = date.today()
    dealdate = today
    terminationdate = date(2021, 7, 13)
    step=7
    d = terminationdate-today
    steps = int(math.ceil((float(d.days))/float(step)))

    randomvariables = RNGenerator(r, rnseed ,numOPath , steps)
    
    #ls, id, settlement, callput, strike,threshold,observation, nnotional,inputterminationdate,p0=100,inputdealdate=date.today()
    #print('steps = '+str(steps))

    # Then create an empty list
    #Range('Test', 'A1').value = newTrade0
    if newTrade0.ndim == 2:
        [tradem,traden] = newTrade0.shape
        newTrades = newTrade0[1:]
        
        tradem -= 1
        print('trade dimension = ', tradem)
    if newTrade0.ndim == 1:
        # no trades there
        tradem = 1
        traden = newTrade0.shape[0]
        newTrades = []
        newTrades.append(newTrade0)
                
    simpleList = []    
    tradem
    traden


    [rm,rn] = r.shape
    if (rm != rn):
        print('Covariance matrix is not square!')
        
    
    # here we prepare randam number
    marketdata = RNGenerator(r, rnseed2 ,numOPath , steps)   #################################################Here we define the path
    teststockprice=[]
    pvlist = []
    deltapath= []
#    here we price all the trade
    print(tradem)
    for count in range(0,tradem):
        # each iteration creates a slightly different attribute value, and then prints it to
    # prove that step is working
    # but the problem is, I'm always updating a reference to 'x' and what I want to add to
    # simplelist is a new instance of x that contains the updated attribute
        print('count=',count)
        newWOTrade = WhaleOption(newTrade0[1],count,newTrade0[3],newTrade0[4],newTrade0[6],newTrade0[7])
#        newpricenode=simulateStock(newRSTrade.getp0(),marketdata,today,step,steps,vol)
#        teststockprice.append(newpricenode)
#        print(newpricenode)
        if str(newTrades[count][0]) == "EQ":
            simpleList.append(copy.copy(newTrade))
        elif str(newTrades[count][0]) == "EO":
            simpleList.append(copy.copy(newEOTrade))
            simpleList[count].setcp(str(newTrades[count][8]))
            simpleList[count].setstrike(float(newTrades[count][7]))
        elif str(newTrades[count][0]) == "AT":
            simpleList.append(copy.copy(newATTrade))
            simpleList[count].setsettlement(newTrades[count][9])
            simpleList[count].setcouponbarrier(newTrades[count][10])
            simpleList[count].setknockout(newTrades[count][11])
            simpleList[count].setknockin(newTrades[count][12])
            simpleList[count].setcoupon(newTrades[count][13])
        elif str(newTrades[count][0]) == "DD":
            simpleList.append(copy.copy(newDDTrade))
            simpleList[count].setcp((newTrades[count][8]))
            simpleList[count].setstrike((newTrades[count][7]))
            simpleList[count].setsettlement(newTrades[count][9])
        elif str(newTrades[count][0] == "RS"):
            simpleList.append(copy.copy(newRSTrade))
            simpleList[count].setcp((newTrades[count][3]))
            simpleList[count].setstrike((newTrades[count][4]))
        elif str(newTrades[count][0]=="WO"):
            simpleList.append(copy.copy(newWOTrade))
            simpleList[count].setcp((newTrades[count][3]))
            simpleList[count].setstrike((newTrades[count][4]))               
        #simpleList.append(newTrades)
        #newTrades.setassetid(newTrades.getassetid()+1)
#==============================================================================
#         simpleList[count].setlongshort(str(newTrades[count][1]))
# #        simpleList[count].setnotional(float(newTrades[count][3]))
#         simpleList[count].setassetid((newTrades[count][2]))
#         simpleList[count].setterminationdate(newTrades[count][4])
#         simpleList[count].setTradeprice(float(newTrades[count][5]))
#         simpleList[count].setdealdate(newTrades[count][6])
#==============================================================================
#        print(simpleList)
#==============================================================================
#         for i in range(0,traden):
#             print(newTrades[count][i])
#             print("test print")
#==============================================================================
#==============================================================================
        if str(newTrades[count][0]) == 'WO':
#            print("1")
#==============================================================================
            pvlist.append(priceWhaleOption(simpleList[count],newpricenode,today, step,steps,vol,randomvariables))
#==============================================================================
#         elif str(newTrades[count][0]) == "EO":
#             pvlist.append(eqEO(simpleList[count],marketdata,today,step,steps,vol,InterestRate))
#         elif str(newTrades[count][0]) == "AT":
#             pvlist.append(eqAT(simpleList[count],marketdata,today,step,steps,vol,InterestRate))
#         elif str(newTrades[count][0]) == "DD":
#             pvlist.append(eqDD(simpleList[count],marketdata,today,step,steps,vol,InterestRate))
#==============================================================================
    print(pvlist)
    #Range('Test', 'A1').value = pvlist
    nppvlist = np.asarray(pvlist)
    
    print(nppvlist.shape)
#    print(nppvlist)
    # here we do net up
    (PFE, portfolionode) = PFEs(nppvlist,simpleList,tradem,0.977)
    print('largest PFE is '+str(max(PFE)))
    #everything after here is for data show
    t = np.arange(0., steps+1, 1)
    t0 = np.arange(0., steps, 1)
    print(np.average(portfolionode,axis=1).shape)
    print(t.shape)
    t20 = np.arange(0., steps-1, 1)
 #   try:
    plt.plot(t , np.average(portfolionode,axis=1))
    plt.show()
    print(portfolionode.shape)
    plt.plot(t, portfolionode)
    plt.show()
    plt.plot(t, PFE)
    plt.show()
    print('PFE value is ',PFE)
    t2 = np.arange(0., steps, 1)
    marginRpv = np.diff(portfolionode, axis=0)
    #print(marginRpv.shape)
    plt.plot(t2, marginRpv)
    plt.show()
    marginRpvPF = np.percentile(marginRpv, 0.977*100, axis=1) 
    #print(marginRpvPF.shape)  
    plt.plot(t2, marginRpvPF)
    plt.show()
    print(marginRpvPF)
    print(portfolionode.shape)
    plt.plot(np.arange(0., numOPath , 1), np.sort(portfolionode[steps,:]))
    plt.show()
#==============================================================================
#  '''   except:
#         plt.plot(t0 , np.average(portfolionode,axis=1))
#         plt.show()
#         print(portfolionode.shape)
#         plt.plot(t0, portfolionode)
#         plt.show()
#         plt.plot(t0, PFE)
#         plt.show()
#         print('PFE value is ',PFE)
#         
#         marginRpv = np.diff(portfolionode, axis=0)
#         #print(marginRpv.shape)
#         plt.plot(t20, marginRpv)
#         plt.show()
#         marginRpvPF = np.percentile(marginRpv, 0.977*100, axis=1) 
#         #print(marginRpvPF.shape)  
#         plt.plot(t20, marginRpvPF)
#         plt.show()
#         print('daily margin PFE value is ',marginRpvPF)
# #    np.savetxt("output.csv", nppvlist, delimiter=",") '''
#==============================================================================
    return teststockprice





###
p0=100
vol=0.123
strike=100



 #Note here you need to enter obervation in days. e.g. if it is quarterly observed, the observation = 0.25*365
'''def __init__(self, ls, id, callput, strike,threshold,observation, nnotional,inputterminationdate,p0=100,inputdealdate=date.today()):'''
newTrade = np.asarray(['WO','s',1,1,strike,100,terminationdate,p0,today])
pvmatrix=price(newTrade,vol)
