# Chinese Documents Scraping
Scripts to scrape Chinese test papers from different websites for ma friend :chicken:


* https://www.shijuan1.com/

```
$ python scripts/scrape_doc_shijuan1.py cat start_range end_range fpath
```

* https://www.xkb1.com/

```
$ python scripts/scrape_doc_xkb1.py cat start_range end_range fpath
```

## Arguments to pass
```
- cat: Category of documents to scrape from, retrieved from the url 
    eg. sjyw2/list_107 (https://www.shijuan1.com/a/sjyw2/list_107_1.html)
    or  yuwen/2/list_12 (https://www.xkb1.com/yuwen/2/list_12_1.html)  
- start_range: Start of page to scrape from, eg. 1
- end_range: End of page, eg. 3
- fpath: Folder to save the files, name to your preference, eg. download_files
```
