import os
import re
import json
import time
import requests
import pandas as pd

from .user_promo_module import *
from mixpanel_api import Mixpanel
from datetime import datetime, timedelta
from django.views.decorators import csrf
from django.shortcuts import render, render_to_response


def start(request):
    return render(request, "start.html", {'status': ''})

    
def collect_data(request):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    try:
        days = int(request.GET['days'])
    except:
        days = 7
    collect_events(days, BASE_DIR + '/data')
    collect_promotion(BASE_DIR + '/data')
    return render(request, "start.html", {'status': ' {}-day Data Successfully Downloaded! '.format(days)})

    
def generate(request):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    recommendation = main(BASE_DIR + '/data/coupon.xml', BASE_DIR + '/data/tapped_buy_button.json',
                          BASE_DIR + '/data/added_product_to_wish_list.json', BASE_DIR + '/data/removed_product_from_wish_list.json',
                          BASE_DIR + '/data/viewed_product.json')
    new = get_username(BASE_DIR + '/data/people_export.json', recommendation)
    return render(request, "result.html", {'recommendation': json.loads(new.to_json(orient='records'))})


def view_event(request):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    event = pd.read_csv(open(BASE_DIR + '/data/all_event.csv', 'r'))
    new_event = get_username(BASE_DIR + '/data/people_export.json', event).sort_values('name')
    return render(request, "event.html", {'events': json.loads(new_event.to_json(orient='records'))})
    
    
def view_coupon(request):
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    coupon = pd.read_csv(open(BASE_DIR + '/data/all_promo.csv', 'r', encoding='utf-8'))\
        .sort_values(['advertisername', 'days_left'], ascending=[True, True])
    return render(request, "coupon.html", {'coupons': json.loads(coupon.to_json(orient='records'))})
    
    
def collect_promotion(BASE_DIR):
    headers = {'Authorization': }
    data = {
               'grant_type': 'password',
               'username': ,
               'password': ,
               'scope': 

            }
    token = requests.post('https://api.rakutenmarketing.com/token', headers = headers, data = data)
    key = 'Bearer ' + json.loads(token.text)['access_token']
    
    new_headers = {'Authorization': key}
    i, page = 1, 10000
    while i <= page:
        param = {
            'pagenumber': i,
            'resultsperpage': 500
        }
        coupon = requests.get('https://api.rakutenmarketing.com/coupon/1.0', headers=new_headers, params = param)
        if coupon.status_code == 200:
            text = coupon.text
            m = re.search('<couponfeed><TotalMatches>.*</TotalMatches><TotalPages>(.*)</TotalPages><PageNumberRequested>.*</PageNumberRequested>', coupon.text[:150]) 
            page = int(m.group(1))
            if i != page:
                text = text.replace('</couponfeed>', '++++')
            if i != 1:
                text = text.replace(m.group(0), '')
            if i == 1:
                with open(BASE_DIR + '/coupon.xml', 'w', encoding='utf-8') as f:
                    f.write(text)
            else:
                with open(BASE_DIR + '/coupon.xml', 'a', encoding='utf-8') as f:
                    f.write(text)
            i += 1
        else:
            time.sleep(5)

    
def collect_events(days, BASE_DIR):
    m = Mixpanel('', token='')
    fromdate = datetime.strftime(datetime.now() - timedelta(days), '%Y-%m-%d')
    todate = datetime.now().strftime("%Y-%m-%d")
    for i in ['Tapped Buy Button', 'Added Product to Wish List', 'Removed Product from Wish List', 'Viewed Product']:
        m.export_events(BASE_DIR + '/' + i.lower().replace(' ', '_') + '.json', {
            'event': '[\"' + i + '\"]',
            'to_date': todate,
            'from_date': fromdate
        })
    m.export_people(BASE_DIR + '/' + 'people_export.json')
    # json.dump(data, open(BASE_DIR + '/' + i.lower().replace(' ', '_') + '.json', 'w'), indent=4)
    # m.export_events(BASE_DIR + '/buy_button.txt', {"from_date": fromdate, "to_date": todate, 'event':'["Tapped Buy Button"]'})
    # m.export_events(BASE_DIR + '/wish_list.txt', {"from_date": fromdate, "to_date": todate, 'event':'["Added Product to Wish List"]'})
    # m.export_events(BASE_DIR + '/remove.txt', {"from_date": fromdate, "to_date": todate, 'event':'["Removed Product from Wish List"]'})
    

def get_username(BASE_DIR, recommendation):
    file = json.load(open(BASE_DIR, 'r'))
    _id, username, name = [], [], []
    for i in file:
        _id.append(i['$distinct_id'])
        name.append(i['$properties'].get('$name', ''))
        username.append(i['$properties'].get('userName', ''))
    users = pd.DataFrame({'id': _id, 'name':name, 'username': username})
    new = pd.merge(recommendation, users, left_on='initiatorId', right_on='id', how='left')
    return new