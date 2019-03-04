
import json
import math
import numpy as np
import pyproj
from scipy import reshape, sqrt, identity, spatial
import cookielib
import urllib2,socket
import requests
import time
import os 


def mapping(type_list,number_xxx_Type):
    for i in range(number_xxx_Type):
        for j in range(len(type_list[i])):
            if type_list[i][j]['***']==0.0: 
                type_list[i][j]['***']=0.7
            else:
                type_list[i][j]['***']=float(type_list[i][j]['***'])/5.0

            if type_list[i][j]['---']==0.0:
                type_list[i][j]['---']=0.7
            else:
                type_list[i][j]['---']=float(type_list[i][j]['---'])/10.0

            if type_list[i][j]['']==0.0:
                type_list[i][j]['+++']=0.7
            else:
                type_list[i][j]['+++']=float(type_list[i][j]['+++'])/10.0

            if type_list[i][j]['===']==0.0:
                type_list[i][j]['===']=0.7
            else:
                type_list[i][j]['===']=float(type_list[i][j]['==='])/10.0
            
            if type_list[i][j]['///']==0.0:
                type_list[i][j]['///']=0.7
            elif float(type_list[i][j]['///'])>=1000.0:
                type_list[i][j]['///']=0.1
            else:
                temp = int(type_list[i][j]['///']/100)
                type_list[i][j]['///']=round(1.0-temp/10.0,1)
            
            type_list[i][j]['distance']=type_list[i][j]['distance']/1000
    return type_list
    

def Index(type_list_new,xxxs_Index,number_xxx_Type,q): 
    with open("Index.txt",'a') as Findex:
        xxxs_Index.append([])
        xxx_list = []
        for i in range(number_xxx_Type):
            if type_list[i]==[]:
                xxxs_Index[q].append('Non')
                Findex.write('Non'+'\t')
            else:
                for j in range(len(type_list[i])):
                    xxx_INDEX = 0.2*(type_list[i][j]['***'])+0.1*(type_list[i][j]['---'])+0.1*(type_list[i][j]['+++'])+0.1*(type_list[i][j]['==='])+0.1*(type_list[i][j]['has_deal'])+0.2*(type_list[i][j]['///'])+0.2*(type_list[i][j]['distance'])
                    xxx_list.append(xxx_INDEX)
                temp = np.median(xxx_list)
                xxxs_Index[q].append(temp)
                Findex.write(str(temp)+'\t')
        Findex.write('\n')
        

def MyCount(type_list,Count,number_xxx_Type,q):
    Count.append([])
    with open("Count.txt",'a') as FCount:
        for i in range(number_xxx_Type):
            Count_xxx_Type = len(type_list[i])
            Count[q].append(Count_xxx_Type)
            FCount.write(str(Count_xxx_Type)+'\t')
        FCount.write('\n')

        
def Ripley(type_list,Degree_Cluster,DistanceToCluster,Mykey,Location_xy,number_xxx_Type,q):
    global Mykey_index
    Degree_Cluster.append([])
    DistanceToCluster.append([])
    area = math.pi * 1000 * 1000
    
    with open("Cluster.txt",'a') as FCluster:
        with open("Distance.txt",'a') as FDistance:
            for i in range(number_xxx_Type):
                xxxnts1 = []
                for j in range(len(type_list[i])): 
                    xy = (type_list[i][j]['`'],type_list[i][j]['>'])
                    xxxnts1.append(xy)
                distmatrix = caldistmatr(xxxnts1) 
                if distmatrix==[]:
                    Degree_Cluster[q].append('Non')
                    DistanceToCluster[q].append('Non')
                    FCluster.write('Non'+'\t')
                    FDistance.write('Non'+'\t')
                else:
                    clu = calckfunction(distmatrix,100,3,area)
                    Degree_Cluster[q].append(clu)
                    FCluster.write(str(clu)+'\t')
                    center = findclusters(distmatrix, 100)
                    orgin_X = Location_xy[0]
                    orgin_Y = Location_xy[1]
                    xxx_X = type_list[i][center]['`']
                    xxx_Y = type_list[i][center]['>']
                    Mydistance = Accessibility(Mykey,orgin_X,orgin_Y,xxx_X,xxx_Y)
                    
                    try:
                        if float(Mydistance)>=1000.0:
                            pass
                    except TypeError:
                        Mykey_index = Mykey_index + 1
                        Mydistance = Accessibility(Mykey,orgin_X,orgin_Y,xxx_X,xxx_Y)
                    if float(Mydistance)>=1000.0:
                        DistanceToCluster[q].append('0.1')
                        FDistance.write('0.1'+'\t')
                    elif float(Mydistance)<=100.0:
                        DistanceToCluster[q].append('1')
                        FDistance.write('1'+'\t')
                    else:
                        temp = int(float(Mydistance)/100)
                        temp2=round(1.0-temp/10.0,1)+0.1 
                        DistanceToCluster[q].append(temp2)
                        FDistance.write(str(temp2)+'\t')
            FCluster.write('\n')
            FDistance.write('\n')

            
def Index_Category(xxxs_Index,Count,Degree_Cluster,Default_increment,DistanceToCluster,xxxs_Category,number_xxx_Type,q):
    with open('Index_Category.txt','a') as FIndex_Category:
        xxxs_Category.append([])
        for i in range(number_xxx_Type):
            if Count[q][i]==0:
                xxxs_Category[q].append('Non')
                FIndex_Category.write('Non'+'\t')
            else:
                xxx_Category = float(xxxs_Index[q][i]) * float(Count[q][i]) * float((Degree_Cluster[q][i]+Default_increment)) * float(DistanceToCluster[q][i])
                xxxs_Category[q].append(xxx_Category)
                FIndex_Category.write(str(xxx_Category)+'\t')
        FIndex_Category.write('\n')

def Index_Standerize(xxxs_Category,number_charging,number_xxx_Type,result_file):
    xxxs_list =[]
    
    for j in range(number_xxx_Type):
        xxxs_list.append([])
        
    for i in range(number_charging):
        for j in range(number_xxx_Type):
            if xxxs_Category[i][j]=="Non":
                pass
            else:
                xxxs_list[j].append(xxxs_Category[i][j])
                
    for i in range(number_charging):
        for j in range(number_xxx_Type):
            temp_max = max(xxxs_list[j])
            temp_min = min(xxxs_list[j])
            if xxxs_Category[i][j]=="Non":
                result_file.write('0'+'\t')
            else:
                temp = (float(xxxs_Category[i][j])-float(temp_min))/(float(temp_max)-float(temp_min)) 
                result_file.write(str(temp)+'\t')
        result_file.write('\n')


def caldistmatr(xxxnts1):
    xxxnts2 = proj_trans(xxxnts1)
    if xxxnts2==[]:
        distmatrix=[]
    else:
        distmatrix = spatial.distance.cdist(xxxnts2,xxxnts2)
    return distmatrix

    
def proj_trans(xxxnts1):
    xxxnts2 = []
    p1 = pyproj.Proj(init="epsg:4326")  
    p2 = pyproj.Proj(init="epsg:3857") 
    for i in range(len(xxxnts1)):
        lon = xxxnts1[i][0]
        lat = xxxnts1[i][1]
        x1, y1 = p1(lon, lat)
        x2, y2 = pyproj.transform(p1, p2, x1, y1, radians=True)
        xy = (x2,y2)
        xxxnts2.append(xy)
    return xxxnts2

    
def calckfunction(distancematrix1, lagd, lagn,area):
    numxxxnts = len(distancematrix1)
    kfunc_o = [0]*lagn
    lfunc_o = [0]*lagn
    for a in range(0,lagn):
        lagdistance = lagd * (a+1)
        Nlst = []
        for i in range (0, numxxxnts):
            N = 0
            N2 = 0
            w = 1
            for j in range (0, numxxxnts):
                if i is not j:
                    t = distancematrix1[i][j] < lagdistance
                    N=N+int(t)
            Nlst.append(N*w) 
        kfunc_o[a] = (area*np.sum(Nlst))/(numxxxnts**2)
        lfunc_o[a] = np.sqrt(kfunc_o[a]/np.pi) - lagdistance
    lfunc_avg =(lfunc_o[0]+lfunc_o[1]+lfunc_o[2])/3.0
    return lfunc_avg 

    
def findclusters(distancematrix1, lagd):
    Nlst = []
    sumNlst = []
    numxxxnts = len(distancematrix1)
    for i in range (0, numxxxnts):
        N = 0
        N2 = 0
        w = 1
        for j in range (0, numxxxnts):
            if i is not j:
                t = distancematrix1[i][j] > lagd
                N=N+int(t)
        Nlst.append(N*w)
    max_index = Nlst.index(max(Nlst))
    return max_index

def getURLInfo(url):
    user_agent = 
    header = {'User-Agent': user_agent}
    header['Host'] = 
    cookie = cookielib.CookieJar()
    cookie_handler = urllib2.HTTPCookieProcessor(cookie)
    opener = urllib2.build_opener(cookie_handler)
    urllib2.install_opener(opener)
    req = urllib2.Request(url, headers = header)
    try:
        con = urllib2.urlopen(req)
    except urllib2.URLError:
        sleep(5)
        con = urllib2.urlopen(req)
    doc = con.read()
    con.close()
    return doc

def Accessibility(Mykey,orgin_X,orgin_Y,xxx_X,xxx_Y):
    Url = 
    url = 
    jsonData = getURLInfo(url)
    Data = eval(jsonData)
    
    try:
        duration = Data['results'][0]['distance']
        return duration
    except:
        Mykey_index = Mykey_index +1
        Accessibility(Mykey,orgin_X,orgin_Y,xxx_X,xxx_Y)
