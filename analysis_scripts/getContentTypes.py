from errno import ESTALE
import json
import os
from mitmproxy import http
from mitmproxy.io import FlowReader
from bs4 import BeautifulSoup
from multiprocessing import Pool, TimeoutError
from functools import partial

valid_common_domains_file = '/home/azafar2/mobile_analysis/data/validCommonDomains_round_2.json'
browsers = ['Safari']
browsers = ['ddg','Safari','chrome','brave','firefox','focus']

def returnMappedContent(content):
    if 'image' in content:
        return 'image'
    elif 'text/html' in content:
        return 'text/html'
    elif 'javascript' in content:
        return 'javascript'
    elif 'json' in content:
        return 'json'
    elif 'audio' in content:
        return 'audio'
    elif 'video' in content:
        return 'video'
    elif 'octet-stream' in content:
        return 'octet-stream'
    elif 'css' in content:
        return 'css'
    elif 'xml' in content:
        return 'xml'
    elif 'font' in content:
        return 'font'
    elif 'plain' in content:
        return 'plain'
    elif 'x-protobuffer' in content:
        return 'x-protobuffer'
    else:
        return 'other'

# browser specific requests that need to be ignored
with open("/home/azafar2/mobile_analysis/data/browser_specific_requests.json") as fp:
    browser_spec_reqs = json.load(fp)
    fp.close()


def saveAsJson(data,filename):
    with open(filename,'w') as fp:
        json.dump(data,fp,indent=4)
        fp.close()
    fp.close()

def processDumpFile(filepath):
    domain = filepath.split('/')[-1]
    browser = filepath.split('/')[-3]
    data = {}
    with open(filepath,'rb') as fp:
        try:
            for flow in FlowReader(fp).stream():
                try:
                    if flow.request.url in browser_spec_reqs[browser]:
                        continue
                    if '240.240.240.240' in flow.request.url:
                        continue
                    
                    headers = flow.response.headers
                    if 'Content-Type' in headers:
                        content_type = headers['Content-Type']
                        content_type = returnMappedContent(content_type)
                        if content_type not in data:
                            data[content_type] = 1
                        else:
                            data[content_type] += 1
                except:
                    continue
        except:
            return [domain,{}]
            
    return [domain,data]


def getValidCommonDomains():
    with open(valid_common_domains_file) as fp:
        data = json.load(fp)
        fp.close()
    domains = list(data.keys())
    return domains

def sortDict(dic):
    return {k: v for k, v in sorted(dic.items(), key=lambda item: item[1], reverse=True)}
        
def main():
    domains = getValidCommonDomains()
    # domains = domains[:100]
    browsers_content = {}
    for browser in browsers:
        filepaths = []
        browser_contents = {}

        for domain in domains:
            filepath = f'/home/azafar2/OmniCrawl/data_round_2/{browser}/{domain}/{domain}_round_2'
            if os.path.exists(filepath):
                filepaths.append(filepath)

        # filepaths = filepaths[:1000] # test for 100 files only
        with Pool(processes=100) as pool:
            res = pool.map(processDumpFile,filepaths)
        print(f'browser checked: {browser}')
        # print(res)
        
        for entry in res:
            domain = entry[0]
            domain_contents = entry[1]
            for content in domain_contents:
                if content not in browser_contents:
                    browser_contents[content] = domain_contents[content]
                else:
                    browser_contents[content] += domain_contents[content]

        browser_contents = sortDict(browser_contents)
        browsers_content[browser] = browser_contents
        save_to_path = f'/home/azafar2/mobile_analysis/data/contents_round_2.json'
        saveAsJson(browsers_content,save_to_path)
    save_to_path = f'/home/azafar2/mobile_analysis/data/contents_round_2.json'
    saveAsJson(browsers_content,save_to_path)


main()