
# coding: utf-8

# In[ ]:

import requests
import time
import json
import lxml.html
from lxml.cssselect import CSSSelector
from urllib.request import urlopen
from bs4 import BeautifulSoup
import codecs
from lxml import etree

url = "https://api.nytimes.com/svc/mostpopular/v2/mostviewed/all-sections/1.json?"
params={
    'api-key':'*'
}
r = requests.get(url, params=params)
data=json.loads(r.text)


# In[ ]:

article=[]
for news in data['results']:
    beautiful = requests.get(news['url']).content
    tree=lxml.html.fromstring(beautiful)
    sel=CSSSelector('.e2kc3sl0')
    results=sel(tree)
    content=''
    for i in results:
        if i.text:
            content+=i.text+' '
    article.append(content)
# match=results[m]
# daf=match.get('href')
# daf1=match[1].text


# In[ ]:

beautiful = requests.get("https://data.cityofnewyork.us/browse?q=").content
tree=lxml.html.fromstring(beautiful)
sel=CSSSelector('.browse2-result-name-link')
results=sel(tree)
dataset=[]
for match in results:
    dataset.append((match.get('href'),match.text))


# In[ ]:

new=dataset[0][0]
html = urlopen(new)
obj = BeautifulSoup(html, 'html.parser')
t1 = obj.find_all('a')
for t2 in t1:
    t3 = t2.get('href')
    print(t3)


# In[ ]:

r = requests.get(new)
r.encoding = r.apparent_encoding
dom = etree.HTML(r.text)
re=dom.xpath('//*[@id="export-flannel"]')

