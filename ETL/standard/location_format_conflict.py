
import pandas as pd
import numpy as np


def parking_location_format_conflict(data, source_lower):
    
    if '***' not in data:
        data['***']={}
   
    if source_lower.lower()=='etcp':
            
        if 'passageWay' in data:
            if data['passageWay']!=[]:
                d=pd.DataFrame(data['passageWay'])
                ee=d['type']
                d=d.replace('出口','exit').replace('入口','entrance').replace('出入口','entrance/exit')
                
                d['location']=d[['lon','lat']].astype('float64').to_dict(orient='records')
                d['gridCode']=['']*len(d)
           
                if 'aliasName' in data:
                    d['pointName']=data['aliasName']+ee
                else: d['pointName']=ee
                    
                new=d[['id','type','location','gridCode','pointName']]
                new=new.rename(columns={'id':'pointID','type':'locationType'})
                new=new.to_dict(orient='records')                
                data['***']['locationPoint']=new
            else: data['***']['locationPoint']=[]
        else: 
            data['***']['locationPoint']=[]
            print('passageWay not found')
 
    elif source_lower.lower()=='amap':

        if 'name' in data:
            name=data['name']
        else:
            name=''
            
        new=[] 
     
        if all(t in data for t in ['longitude_entrance','latitude_entrance']):
            if all(len(data[t])>0 for t in ['longitude_entrance','latitude_entrance']): 
                new.append({'location':{'lat': float(data['latitude_entrance']),'lon':float(data['longitude_entrance'])},'locationType': 'entrance', 'pointID': data['id']+'-'+str(len(new)+1),'gridCode':'','pointName':name+'入口'})
        else: print('longitude_entrance, latitude_entrance not found')
            
        if all(t in data for t in ['longitude_exit','latitude_exit']):
            if all(len(data[t])>0 for t in ['longitude_exit','latitude_exit']): 
                new.append({'location': {'lat':float(data['latitude_exit']),'lon':float(data['longitude_exit'])},'locationType': 'exit', 'pointID': data['id']+'-'+str(len(new)+1),'gridCode':'','pointName':name+'出口'})
        else: print('longitude_exit, latitude_exit not found')
        
        data['***']['locationPoint']=new

    elif source_lower.lower()=='parkopedia': 
        
        data['***']['locationPoint']=[]

    else: 
        print(data)
        
        data['***']['locationPoint']=[]

    return(data)