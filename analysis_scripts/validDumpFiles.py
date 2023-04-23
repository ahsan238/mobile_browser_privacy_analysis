import json
import os
import jsbeautifier
from tld import get_fld
import hashlib
from multiprocessing import Process
from mitmproxy import http
from mitmproxy.io import FlowReader
import re
from multiprocessing import Pool, TimeoutError, Lock
from functools import partial
from tqdm import tqdm




browsers = ["chrome","firefox","focus","brave","ddg", "Safari"]
# browsers = ['firefox']

threshold_dic = {
    "chrome":8,
    "ddg":8,
    "firefox":8,
    "focus":8,
    "brave":8,
    "Safari":8,
}

def reportAPI_logStatus(file_name,browser):
    if os.path.isfile(file_name):
        s = os.path.getsize(file_name)/1024 # get file size in bytes
        threshold = threshold_dic[browser]
        if s > threshold:
            return True
        else:
            return False
    else:
        return False

def reportDumpStatus(file_name):
    domain = file_name.split("/")[-1]
    # print(domain)
    # checks a dump file for the presence of 200, 300 response status codes. Their presence signifies that the crawl was successful
    try:
        with open(file_name, 'rb') as fp:
            for flow in FlowReader(fp).stream():
                url = re.sub(r'https?://', '', flow.request.url)
                
                # print(url,flow.response.status_code,flow.request.url)
                try:
                    if url[-1]=='/':
                            if domain in url[:-1] and flow.request.method=='GET' and (flow.response.status_code>=200 and flow.response.status_code<=399):
                                return True
                    else:
                        if domain in url and flow.request.method=='GET' and (flow.response.status_code>=200 and flow.response.status_code<=399):
                            return True
                except Exception as error:
                    return False
            fp.close()
        return False
    except Exception as error:
        print(file_name,error)
        return False

def gatherDumpPaths(browser,file_type='mitm'):
    filepaths = []
    browserpath = f'/home/azafar2/OmniCrawl/data/{browser}'

    all_files = os.listdir(browserpath)
    for x in all_files:
        file_dir_path = os.path.join(browserpath,x)
        if file_type == 'mitm':
            filepath = os.path.join(file_dir_path,x)
        elif file_type == 'api':
            filepath = os.path.join(file_dir_path,x+".log.sqlite3")
        filepaths.append(filepath)
    return filepaths

def saveAsJson(data,filename):
    with open(filename,'w') as fp:
        json.dump(data,fp,indent=4)
        fp.close()
    fp.close()

def reportProgress(browser,file_type='mitm'):
    
    filepaths = gatherDumpPaths(browser,file_type)
    # filepaths=filepaths[:40]

    invalid_domains = []
    valid_domains = []
    with Pool(processes=40) as pool:
        if file_type=='mitm':
            with tqdm(total=len(filepaths)) as pbar:
                res = []
                for result in pool.imap(reportDumpStatus,filepaths):
                    res.append(result)
                    pbar.update(1)
        elif file_type=='api':
            res = pool.map(partial(reportAPI_logStatus,browser=browser),filepaths)
        for i,val in enumerate(res):
            domain = (filepaths[i].split('/')[-1]).replace(".log.sqlite3",'')
            if val == True:
                valid_domains.append(domain)
            elif val == False:
                invalid_domains.append(domain)
    # print(browser,len(invalid_domains),file_type)
    return valid_domains
    

def get_valid_domains(browser):
    invalid_mitm_domains = reportProgress(browser,file_type='mitm')
    invalid_api_domains = reportProgress(browser,file_type='api')

    union = set(invalid_mitm_domains).intersection(invalid_api_domains)
    union = list(union)
    print(browser,len(union))
    if browser == 'chrome':
        d = {}
        for i in union:
            d[i] = 1
        saveAsJson(d,'./../data/chrome_valid_domains.json')
    else:
        d = {}
        print(browser)
        for i in union:
            d[i] = 1
        saveAsJson(d,f'./../data/{browser}_valid_domains.json')
    return union


def main():
    browser_domains = []
    for browser in browsers:
        _list = get_valid_domains(browser)
        browser_domains.append(_list)
    result = set(browser_domains[0]).intersection(*browser_domains)
    result = list(result)
    d = {}
    for domain in result:
        d[domain] = 1
    print(f'common domains {len(result)}')
    # saveAsJson(d,'/home/azafar2/mobile_analysis/data/validCommonDomains.json')



main()
# print(reportDumpStatus("/home/azafar2/OmniCrawl/data/brave/youtube.com/youtube.com"))
