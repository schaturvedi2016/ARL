# -*- coding: utf-8 -*-
"""
Created on Tue Feb  7 08:00:54 2017

@author: Shubham
"""
import os
import pandas
import math
import numpy as np
import matplotlib.pyplot as plt
from scipy.special import lambertw
from scipy.optimize import differential_evolution

#   Budget Allocation
budget = 1000000000 #1e9
#   Epsilon - Small positive constant
eps = 0.001

#   Ba - Budget allocated to availability improvement
#Ba = 2e7

#   Budget Allocation for availability gamma
#Ba_g1 = 8000000

padding = -1
#   Empty List
A_opt = []  #   List for appending the max optimal value of system availability.   

ngamma = []
xaxis = []
gammaData = []
bounds = []
GammaComp = []
AvailabilityData = []
etaData = []
GComp = []
'''
    Component Description    
    
    L       --> Lifecycle
    c1      --> Cost to replace subsystem
    Ma      --> Initial A-mode failure rate (In paper it is Lamba A)
    Mb      --> Initial B-mode failure rate (In paper it is Lamda B)
    c0      --> Cost of operating TAAF phase (TAAf - Test, analyze, and fix)
    mub     --> Average value of cost increment
    mud     --> Average B-mode failure fix effectiveness factor
    cv      --> Coefficient of variationof initial B-mode failures
    gamma   --> Cost to achieve desired MTBEFF (Mean time between essential function failure)
    MTTRi   --> Mean time to repair of subsystem i
'''

'''
   Equation Number 11
   MTTF as a function of reliability investment 
'''
df = []#pandas.read_excel(os.getcwd() + '/sample.xlsx')
#values = df[ColumnName[col]].values[row]
component = 0#int(input("enter the number of components ")) #just to test the limited number of components

def mttf(data2,G3):
    la = 1 / float(data2['Ma'].values[0])
    lb = 1 / float(data2['Mb'].values[0])
   
    exp_part_a = ((data2['c0'].values[0] + (math.pow(data2['cv'].values[0], 2) * G3))/data2['mub'].values[0])
    
    pl = ((data2['c0'].values[0] * math.exp(exp_part_a))/data2['mub'].values[0])
    #   Lambert w function
    w = lambertw(pl)
    b = (data2['c0'].values[0] * data2['mud'].values[0])/(data2['mub'].values[0] * w)
    c = la + lb * (1 - data2['mud'].values[0] + b)
    M = 1 / c
    #print("MTTF  "+str(np.real(M)))
    return(np.real(M))

'''
   The average number of times subsystem i must be replaced over a system lifecycle of length L.
   Where eps > 0 is a small constant.
'''
data1 =[]
def repParts(data1,G2):
    #   P --> Number of subsystem i replacements over system lifecycle.
    P = ((data1['L'].values[0] / mttf(data1,G2))) - eps    
   # print("P value"+ str(P))
    return math.floor(P)

'''
   The average cost of the initial subsystem i and its replacements over the system lifecycle. 
'''
data =[]
def C(data,G1):
    #   Ci --> Cost of subsystem i over system lifecycle
    Ci = data['c1'].values[0]*(1 + repParts(data,G1))
    #print("Ci value"+ str(Ci))
    return Ci

'''
   Equation Number 12 (Paper AHS_CA)
   Steady state availability of subsystem i
'''
comp1=[]
def sysAvail(comp1,g):
    deno = mttf(comp1,g) + comp1['MTTRi'].values[0]
    Ai = (mttf(comp1,g)/deno*padding)
    #print("Avalability"+ str(Ai))
    return Ai

'''
    Equation Number 13 (Paper AHS_CA)
    Maximizing availability through reliability investment.
    Constraints needs to be added. (Remaining)
'''
def sys(g):
    arr =[] 
    product =1
    
    for c in range (0,component):
       A = sysAvail(df[c:c+1],g[c])
       arr.append(A) 
       product *= arr[c]
    return product
    #print (product)

'''
    Equation Number 16 (Paper AHS_CA)
    The cost of the initial n subsystems and their replacements over the system life cycle.
'''
comp = []
def UnitCost(comp,GammaData):
    CsSum=[]
 
    for g in range (0,component):
        Cs = C(df[g:g+1],GammaData[g])
        CsSum.append(Cs)
    #print("UnitCost value"+ str(sum(CsSum)))
    return sum(CsSum)

'''
    Equation Number 17 (Paper AHS_CA)
    Number of systems that can be purchased and supported with a budget of B (In our case budget) > Ba
    Fleet size
'''
def eta(GammaData):
    
    nGamma = ((-budget + sum(GammaData)) / (UnitCost(df[0:component],GammaData))) 
    #print(budget)    
    return math.ceil(nGamma)
    

'''
    Paper AHS_RE --> Graph plotting functions. ********
'''
#   Function for ploting graph of subsystem lifecycle cost and Investment in reliability.
def reliabilityEngineering(comp):
    gamma_range = []
    mttf_range = []
    cost_range = []
    
    for g in range (0, comp['gamma'].values[0], 10000):
        gamma_range.append(g)
     
        
        '''
           Calculation till equation 11 - Paper AHS_RE
           MTTF as a function of reliability investment
        '''        
                   
        mttf_range.append(mttf(comp,g))
        P = ((comp['L'].values[0] /mttf(comp,g))) - eps #np.real(M)
        '''
           Equation Number 13
           Define single component replacement costs and part replacement costs over system lifecycle.
           Ci --> Cost of subsystem i over system lifecycle
        '''
        """
        equation 15
        """
        
        Ci = comp['c1'].values[0]*(1 + P)
        cost_range.append(Ci)
       # cost_range.append(cost(comp, g))
    return (mttf_range, gamma_range, cost_range)
    


"""
Taking care under GUI 
"""

"""
def graph_Mtbf_Investment(x, y, g):
        plt.figure(1)
        plt.plot(x, y) #, label = 'Component '+str(g+1)
        plt.xlabel('INVESTMENT')
        plt.ylabel('MTBF')
        plt.legend()
       # plt.show()
    
'''
        Graph for Cost versus Investment (Paper AHS_RE)
'''
def graph_Cost_Investment(x, y, g):
        plt.figure(2)
        plt.plot(x, y) #label = 'Component '+str(g+1)
        plt.xlabel('INVESTMENT')
        plt.ylabel('COST')
        plt.legend()
        #plt.show()
"""
'''    
    Graph of Investment in reliability (G_opt) and System Availability (A_opt)
    Impact of optimal investment in reliability improvement on system availability.
'''
  
def reliAvail_graph(x, y):
            plt.figure(3)
            plt.plot(x, y)
            plt.xlabel('Investment in reliability')
            plt.ylabel('System Availability (A)')
            #plt.show()
    
'''
        Graph of Investment in reliability (G_opt) a  nd Fleet Size (ngamma)
        Impact of optimal investment in reliability improvement on fleet size.
'''
    
def reliFleet_graph(x, y):
            plt.plot(x, y)
            plt.xlabel('Investment in reliability')
            plt.ylabel('Fleet Size')
           #plt.show()
    
'''
        Graph of Fleet Size (ngamma) and System Availability (A_opt)
        Optimal availability and fleet size for various investments
'''
    
def availFleet_graph(x, y):
        plt.plot(x, y)
        plt.xlabel('System Availability (A)')
        plt.ylabel('Fleet Size')
        #plt.show()

def ahs_Re(result):
          
    '''
       Graph for MTBF versus Investment (Paper AHS_RE)
       Need to update the loop implementation to plot the graph
    '''  
    result1 =   result
    """
    for g in range(0,component):
        
        df.set_value(g, "gamma", result1.x[g])
        set_comp = reliabilityEngineering((df[g:g+1]))
        graph_Cost_Investment(set_comp[1], set_comp[2],g)
        graph_Mtbf_Investment(set_comp[0], set_comp[2],g)
    """
    etaData.append((result1.fun)*padding)  
    AvailabilityData.append(sys(result1.x))
    
    """
    ahs_ca --> main function start
    """

def ahs_Ca():
        for budg in range(7000000,100000000,10000000):
           # global budget
            #budget = budg
            xaxis.append(budg)
            f = (0,budg)
            bounds =[f]*component 
                  
            
            # Differential evolution finds the global maximum of a multivariate function.
            resultEta = differential_evolution(eta, bounds, maxiter = 4000)
            #resultAva = differential_evolution(sys, bounds, maxiter = 4000)
           # print("LoopEtaData")
            #print(resultEta)
           # print("LoopAvaData")
            #print(resultAva)
            ahs_Re(resultEta)
            #AvailabilityData.append(resultAva.fun)    
            #sys(resultAva)
        print("etaData With Differential Evolution")
        print(etaData)
        print("Avalability Data With Differential Evolution")
        print(AvailabilityData)
        #plt.show()
        #print("G_opt vs A_opt")
        reliAvail_graph(xaxis, AvailabilityData)
    
        #print("G_opt vs ngamma")
        reliFleet_graph(xaxis, etaData)
    
        #print("A_opt vs etaData")
        availFleet_graph(AvailabilityData,etaData)
        #plt.show()
        
#ahs_Ca()
