
import pandas as pd 
import json
import codecs
import re
import numpy as np


def general_opening_time_format_conflict(obj,tag_org):
    
    def print_warning(time_group,time_raw):
        print()
        print('Warning:',time_group,'is not logged before!')
        print('         The whole text is showed below:')
        print(time_raw)
    
    def print_warning_small(time_group):
        print()
        print('Warning:',time_group,'is not logged before!')        
    
    def time_order_exchange(openhour_temp,closehour_temp):
        if openhour_temp == '24:00' and closehour_temp == '00:00':
            openhour_temp = '00:00'
            closehour_temp = '24:00'
        
        return openhour_temp,closehour_temp
    
    week = {}
    year = {}
    week_list = []
    week_back = {}     


    def season_solving(time_group):
        time_group = ''.join(re.findall('[\u4e00-\u9fff,、，]+',time_group))
        time_group = time_group[:time_group.rfind('季')+1]
        Seasons = 0
        for time in re.split('[,、，]',time_group):
            if time != '旺季' and time != '淡季':
                Seasons = Seasons+2**year[time]
                
        bin_seasons = Seasons
        
        return bin_seasons
    
    def day_solving(time_group):
        if '周1-5' in time_group:
            Days = sum([2**n for n in range(0,4)])
        else:
            if '闭馆' not in time_group:
                time_group = ''.join(re.findall('[\u4e00-\u9fff,、，—~/]+',time_group))
                time_group = time_group[time_group.index('周'):]
                Days = 0
        
                for time in re.split('[、,，；;]',time_group):
                    if '至' in time:
                        position = time.index('至')
                        begin = week[time[position-2:position]]                    
                        end = week[time[position+1:position+3]]
                        Days = Days+sum([2**n for n in range(begin,end+1)])
           
                    elif '—' in time:
                        position = time.index('—')
                        begin = week[time[position-2:position]]                    
                        end = week[time[position+1:position+3]]
                        Days = Days+sum([2**n for n in range(begin,end+1)])
        
                    elif '到' in time:
                        position = time.index('到')
                        begin = week[time[position-2:position]]                    
                        end = week[time[position+1:position+3]]
                        Days = Days+sum([2**n for n in range(begin,end+1)])
                            
                    elif '~' in time:
                        position = time.index('~')
                        begin = week[time[position-2:position]]                    
                        end = week[time[position+1:position+3]]
                        Days = Days+sum([2**n for n in range(begin,end+1)])
                            
                    elif '/' in time:
                        position = time.index('/')
                        begin = week[time[position-2:position]]                    
                        end = week[time[position+1:position+3]]
                        Days = Days+sum([2**n for n in range(begin,end+1)])
        
                    elif time == '周末':
                        Days = Days+sum([2**n for n in range(5,7)])
                    
                    elif len(time) == 2:
                        Days = Days+2**week[time]
                    
                    else:
                        print_warning_small(time_group)
            
            else:
                close_day = []
                position = time_group.index('闭馆')
                while(time_group[position-2:position] in week_list):
                    close_day.append(time_group[position-2:position])
                    position = position-2
                Days = sum([2**week[n] for n in list(set(week_list) - set(close_day))])
                
        bin_days = Days
        
        return bin_days
 
    def timeRange_solving(time_group):
        fromto = re.split('[-—]',re.sub('[\u4e00-\u9fa5]','',time_group))
        if '' in fromto:
            [fromto.remove('') for i in range(fromto.count(''))]
        [From,To] = fromto
        From_h = From.split(':')[0]
        To_h = To.split(':')[0]
        
        From = '0'*(2-len(From_h))+From
        To = '0'*(2-len(To_h))+To
        fromto = [From,To]

        return fromto

    def time_solving(time_list,time_raw,season=15,days=127,timeRange=[],time_ans=[],season_flag=0,day_flag=0):         
        timeRange=[]
        time_ans=[]
        time_ans_temp={}
        time_ans_temp['season']=season
        time_ans_temp['days']=days
        while(time_list != [] and time_list is not None):
    
            time_group = time_list.pop(0)
           
            timeRange_rule = ('：' in time_group or ':' in time_group) and ('-' in time_group or '—' in time_group)
            season_rule = '季' in time_group
            days_rule = '周' in time_group
            
            if season_rule:
                if season_flag == 0:
                    try:
                        season = season_solving(time_group)
                        time_ans_temp['season'] = season
                        season_flag = 1 
                    except KeyError as e:
                        print_warning(time_group,time_raw)
                        time_ans_temp['season'] = None
    
                else:
                    time_list.insert(0,time_group)
                    time_ans,time_list = time_solving(time_list,time_raw)
                    
            elif days_rule and not timeRange_rule:
                if day_flag == 0:
                    try:
                        days = day_solving(time_group)
                        time_ans_temp['days'] = days
                        day_flag = 1
                    except KeyError as e:
                        print_warning(time_group,time_raw)
                        time_ans_temp['days'] = None
                    
                else:
                    time_list.insert(0,time_group)
                    time_ans,time_list = time_solving(time_list,time_raw,season=season,season_flag=season_flag)
    
            elif timeRange_rule and not days_rule:
                try:
                    [From,To] = timeRange_solving(time_group)
                    timeRange.append({'from':From,'to':To})
                    time_ans_temp['timeRange'] = timeRange
                except ValueError as e:
                    print_warning(time_group,time_raw)
            
            elif time_group == '全天' or time_group == '全天;':
                timeRange.append({'from':'00:00','to':'24:00'})
                time_ans_temp['timeRange'] = timeRange
            
            elif timeRange_rule and days_rule:
                try:
                    time_group = re.split('[、,，；; ]',time_group)
                    if len(time_group) != 1:
                        time_ans_temp = time_solving(time_group,time_group)[0][0]  
                    else:
                        time_group = [re.sub('[\u4e00-\u9fa5（）]','',time_group[0]),''.join(re.findall('[\u4e00-\u9fff（）]+',time_group[0]))]
                        time_ans_temp = time_solving(time_group,time_group)[0][0]  
                        
                        
                except (KeyError,ValueError):
                   print_warning(time_group,time_raw)
                    
            else:
                time_ans_temp['season']=None
                time_ans_temp['days']=None
                time_ans_temp['timeRange'] = [{'from':'','to':''}]
                print_warning(time_group,time_raw)
                
        time_ans.append(time_ans_temp)
    
        return time_ans,time_list    

    if obj == None:
        return None
    
    tag = tag_org.lower()
    
    if '***' not in obj.keys():
        obj['***'] = {}
    
    obj['***']['openingHours'] = {}
    
    opening_hours = {'time':[{'days':None,'timeRange':[{'from':'','to':''}],'season':None}],'timeText':''}
    
    if tag == '':
        #
            
    else:
        print(tag_org+' '+'is not exist')
        return None

    return obj
