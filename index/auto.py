import requests
import time
import hashlib
import json
import os
import pandas as pd
from elasticsearch import Elasticsearch
from elasticsearch import helpers
import random  


def search(es_client, es_source, source, city):
    es_search_options ={
        "query": {
            "bool": {
                "must":[{"term":{"source":source}},
                    {"match_phrase":{"cityName":city}}]
                }
                   },    
        "_source": [
            "",
            "",
            "",
            "",
            "",
            ""
                 ]
        }
    
    es_result = helpers.scan(
        client=es_client,
        query=es_search_options,
        scroll='5m',
        index=es_source,
        timeout="1m"
    )
     
    def get_result_list(es_result):
        final_result = []
        for item in es_result:
            final_result.append(item['_source'])
        return final_result
        
    final_result = get_result_list(es_result)
    
    return final_result


# 从点评api获取poi数据
def get_session(app_key, app_secret):
    url = ''
    params = {
        'app_key': app_key,
        'app_secret': app_secret,
        'grant_type': 'authorize_platform'  
    }
    r = requests.get(url, params=params)
    return json.loads(r.text)["access_token"]


def _sign(app_secret, param):
    lists = []
    param_str = app_secret
    for item in param:
        lists.append(item)

    lists.sort()

    for key in lists:
        param_str = param_str + key + param[key]

    param_str += app_secret
    param_str = param_str.strip()

    md5 = hashlib.md5()
    md5.update(param_str.encode("utf-8"))

    return md5.hexdigest()


def query_poi(longitude, latitude, radius, page, app_key, session, app_secret):
    url = ''

    params = {
        'app_key': app_key,
        'timestamp': time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())),
        'session': session,
        'format': "json",
        'v': "1",
        'sign_method': "MD5",
        'deviceId': 'ma',
        "page": str(page),
        "latitude": str(latitude),
        "longitude": str(longitude),
        "radius": str(int(radius + 0.5)),
        "sort": "7"}

    sign_str = _sign(app_secret, params)

    params['sign'] = sign_str
    r = requests.get(url, params=params)
    return json.loads(r.text)


def get_charging_poi(charging, distance, file_name, APP_KEY, SESSION, APP_SECRET):
    count=0

    def poi_k(k):
        lon=k["location"]["lon"]
        lat=k["location"]["lat"]
        raw=query_poi(lon, lat, distance, 1, APP_KEY, SESSION, APP_SECRET)
        poi=raw['data']['records']
        page=min(raw['data']['total_number']//25+1,100)
        for i in range(2,page+1):
            poi.extend(query_poi(lon, lat, distance, i, APP_KEY, SESSION, APP_SECRET)['data']['records'])
        for i in poi:
            cat = i['categories']
            i['cate'] = [,,,]
        result={,,,}
        return(result)
    
    with open(os.path.dirname(os.path.realpath(__file__))+'/'+file_name,'w',encoding='utf-8') as file_object:
        for k in charging:
            attempt = False
            while attempt == False:    
                try:
                    result=poi_k(k)
                    json.dump(result,file_object,ensure_ascii=False)
                    file_object.write('\n')
                    count=count+1
                    print(count)
                    attempt = True
                except:
                    print("connecting ...")
                    time.sleep(5)

        print('Done')
        
    file_object.close()



if __name__ == "__main__":
    APP_SECRET = 
    APP_KEY =
    SESSION = get_session(APP_KEY, APP_SECRET)

    es_client = Elasticsearch([{"host": "", "port": }])
    es_source = ""
    source = ""
    city = ""
    result = search(es_client, es_source, source, city)
    
    c=pd.DataFrame(result)
    c=c.sort_index(by='',axis=0,ascending=True)
    charging=c.to_dict('')
 
    group = 500
    n = len(charging)//group  
    distance = 1000

    for i in range(n):
        file_name = city+'_'+source+'_'+str(i)+'.json'
        get_charging_poi(charging[500*n:500*(n+1)], distance, file_name, APP_KEY, SESSION, APP_SECRET)
        print(file_name+'saved')
    
    file_name = city+'_'+source+'_'+str(n)+'.json'  
    get_charging_poi(charging[500*(n+1):], distance, file_name, APP_KEY, SESSION, APP_SECRET)
    print(file_name+'saved')
