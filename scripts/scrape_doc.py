import requests
import urllib.request
from bs4 import BeautifulSoup

import os
import re
import time
import pandas as pd

from multiprocessing import cpu_count
from multiprocessing.pool import ThreadPool



begin = time.time()



######################################################################################################
""" Change the variables to get the desired documents """

# create a folder to store the downloaded files, change the path name to your preference
new_path = "files"

# change the range to scrape more pages, the range is inclusive, the number is the page number
pages = range(88, 89) 
    
# change "sjyw1/list_106" in the url to scrape from different categories
cat = "sjyw1/list_106"

headers = {'User-Agent': 'python-requests/2.28.1', 
           'Accept-Encoding': 'gzip, deflate, br', 
           'Accept': '*/*', 'Connection': 'keep-alive'}



######################################################################################################
""" get list of book names from each page number """

def get_table(url):
    response = requests.get(url, headers=headers)
    
    assert response.status_code == 200, "Page not found"
    
    page = BeautifulSoup(response.content, 'html.parser')
    
    return page.find_all("table")


list_tb = []
# iterate through the page numbers to get the list of tables, change the range to scrape more pages
for nb in pages:        
    url = f"https://www.shijuan1.com/a/{cat}_{nb}.html"    # link of pages to scrape from
    html = get_table(url)
    table = pd.read_html(str(html))[0]

    list_tb.append(table)
    df = pd.concat(list_tb) 

df.columns = df.iloc[0]
df = df.drop(df.index[0])
df.head()

# get list of doc names
doc_list = df.iloc[:, 0].to_list()

print("Number of documents: " + str(len(doc_list)))



######################################################################################################
""" get list of download urls and list of their directories """ 

def get_link(url):
    response = requests.get(url, headers=headers)
    response.encoding = 'GBK' # encoding in Chinese characters
    
    assert response.status_code == 200, "Page not found"
    
    page = BeautifulSoup(response.content, 'html.parser')

    list_doc_html = []
    for x in doc_list:
        doc = page.find_all(lambda tag: tag.name == "a" and x in tag.text)

        for d in doc:
            li = "https://www.shijuan1.com" + d.get('href')
            list_doc_html.append(li)
            
    return list_doc_html


# get list of download urls 
download_urls = []
# iterate through the page numbers to get the list of doc html, change the range to scrape more pages
for nb in pages:
    url = f"https://www.shijuan1.com/a/{cat}_{nb}.html"     # link of pages to scrape from
    list_doc_html = get_link(url)

    # iterate through the list of doc hltm in each page number
    for l in list_doc_html:
        r = requests.get(l, headers=headers)
        r.encoding = 'GBK'
        soup = BeautifulSoup(r.text, 'html.parser')
            
        # iterate through the list of urls in each doc html and find the download url
        for link in soup.find_all(lambda tag: tag.name == "a" and "本地下载" in tag.text):
            a = "https://www.shijuan1.com" + link.get('href')
            download_urls.append(a)


# create a folder to store the downloaded files
if not os.path.exists(new_path):
    os.mkdir(new_path)

# get the list of file directories from the download urls
file_dir = []
for x in download_urls:
    result = new_path + '/' + re.search('/1-(.*)', x).group(1)
    file_dir.append(result)

print("Number of download_urls: " + str(len(file_dir)))



######################################################################################################
""" download the files and save them in the newly created folder """

def download_url(args):
    url, fn = args[0], args[1]
    urllib.request.urlretrieve(url, fn)   


# Download multiple files in parallel
def download_parallel(args):
    cpus = cpu_count()
    results = ThreadPool(cpus - 1).imap_unordered(download_url, args)
    for result in results:
        result


download_parallel(zip(download_urls, file_dir))



end = time.time()



print("Download completed")
print("Time taken: " + str(round((end - begin)/60, 2)) + " minute(s)")
