import argparse
import os
import time

import pandas as pd
import re

import requests
import urllib.request
from bs4 import BeautifulSoup

from multiprocessing import cpu_count
from multiprocessing.pool import ThreadPool


headers = {'User-Agent': 'python-requests/2.28.1', 
           'Accept-Encoding': 'gzip, deflate, br', 
           'Accept': '*/*', 'Connection': 'keep-alive'}
# get url
def get_page(url):

    response = requests.get(url, headers=headers)

    assert response.status_code == 200, "Page not found"
    
    page = BeautifulSoup(response.content, 'html.parser')
    
    return page


# get list of doc names from each page number 
def list_doc_names(cat, start_range, end_range):

    pages = range(start_range, end_range)

    list_tb = []
    # iterate through the page numbers to get the list of tables 
    for nb in pages:        
        url = f"https://www.xkb1.com/{cat}_{nb}.html"   
        page = get_page(url)
        html = page.find_all("table")
        table = pd.read_html(str(html))[6]
        table = table.drop(table.index[0:9])
        table = table.dropna()

        list_tb.append(table)
        df = pd.concat(list_tb) 

    # get list of doc names
    doc_list = df.iloc[:, 0].to_list()
    return doc_list


# get list of download urls and list of their directories 
def get_lists(cat, start_range, end_range, fpath):
    """
        cat: category of the documents, retrieved from the url
        start_range: start page number
        end_range: end page number
        fpath: file path to store the downloaded files, name of the folder
    """
    pages = range(start_range, end_range)

    # get list of download urls 
    download_urls = []
    # iterate through the page numbers to get the list of doc html
    for nb in pages:
        url = f"https://www.xkb1.com/{cat}_{nb}.html"   
        page = get_page(url)

        list_doc_html = []
        for x in list_doc_names(cat, start_range, end_range):
            doc = page.find_all(lambda tag: tag.name == "a" and x in tag.text)

            for d in doc:
                li = "https://www.xkb1.com"  + d.get('href')
                list_doc_html.append(li)

        # iterate through the list of doc hltm in each page number
        for l in list_doc_html:
            r = requests.get(l)
            r.encoding = 'GBK'
            soup = BeautifulSoup(r.text, 'html.parser')
                
            # iterate through the list of urls in each doc html and find the download url
            for link in soup.find_all(lambda tag : tag.name== "a" and "进入下载地址列表" in tag.text):
                doc_url_2 = "https://www.xkb1.com" + link.get('href')

                r2 = requests.get(doc_url_2)
                r2.encoding = 'GBK'
                soup2 = BeautifulSoup(r2.text, 'html.parser')
                        
                # iterate through the list of urls in each doc html and find the download url
                for link2 in soup2.find_all(lambda tag : tag.name=="a" and "下载地址一:点击下载" in tag.text):
                    downloaded_url = "https://www.xkb1.com" + link2.get('href')
                    download_urls.append(downloaded_url)

    # remove duplicated urls
    download_urls = list(dict.fromkeys(download_urls))


    # create a folder to store the downloaded files
    if not os.path.exists(fpath):
        os.mkdir(fpath)

    # get the list of file directories from the download urls
    file_dir = []
    for x in download_urls:
        name = re.search('id=(.*)&', x.rsplit('/', 1)[-1]).group(1) + ".rar"
        filename = os.path.join(fpath, name)
        file_dir.append(filename) 

    print("Number of download_urls: " + str(len(file_dir)))

    return zip(download_urls, file_dir)


# Download the file if it does not exist
def download_url(args):
    downloaded_url, filename = args[0], args[1]
    try: 
        if not os.path.isfile(filename):
            urllib.request.urlretrieve(downloaded_url, filename)
    except Exception:
        pass

# Download multiple files in parallel
def download_parallel(args):
    cpus = cpu_count()
    results = ThreadPool(cpus - 1).imap_unordered(download_url, args)
    for result in results:
        result
        

if __name__ == "__main__":

    begin = time.time()

    parser = argparse.ArgumentParser()
    parser.add_argument("cat", help="Category of documents to scrape from, retrieved from the url")
    parser.add_argument("start_range", help="Start of page to scrape from", type=int)
    parser.add_argument("end_range", help="End of page", type=int)
    parser.add_argument("fpath", help="Path to save the files")

    args = parser.parse_args()

    CAT = args.cat
    START = args.start_range
    END = args.end_range
    FPATH = args.fpath

    download_parallel(get_lists(CAT, START, END, FPATH))

    end = time.time()

    print("Download completed")
    print("Time taken: " + str(round((end - begin)/60, 2)) + " minute(s)")
