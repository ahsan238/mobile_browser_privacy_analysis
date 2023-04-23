from adblockparser import AdblockRules
import json
import os
from mitmproxy import http
from mitmproxy.io import FlowReader
from multiprocessing import Pool, TimeoutError
from functools import partial
from publicsuffix import PublicSuffixList
import tldextract
import sqlite3
import zlib


browsers = ['focus','firefox','chrome','ddg','Safari','brave']


# browser specific requests that need to be ignored
with open("/home/azafar2/mobile_analysis/data/browser_specific_requests.json") as fp:
    browser_spec_reqs = json.load(fp)
    fp.close()

class _DB():
	def __init__(self,db_file):
		self.db = sqlite3.connect(db_file)

	def read(self):
		pools = []
		cur = self.db.cursor()
		for row in cur.execute('SELECT data FROM crawl'):
			data =json.loads(zlib.decompress(row[0]).decode())
			pools.append(data)

		return pools


def get_tldextract(url_str):
    try:
        extracted_obj = tldextract.extract(url_str)
        res = extracted_obj.domain + "." + extracted_obj.suffix
        return res
    except:
        return ''

def getSetHeaderCookies(filepath):
    domain = filepath.split('/')[-1].replace("_round_3","")
    browser = filepath.split('/')[-3]
    # print(browser,domain)
    data = []
    with open(filepath,'rb') as fp:
        try:
            for flow in FlowReader(fp).stream():
                try:
                    if flow.request.url in browser_spec_reqs[browser]:
                        continue
                    if '240.240.240.240' in flow.request.url:
                        continue
                    # get content type
                    headers = flow.response.headers
                    if 'set-cookie' in headers:
                        request_domain = get_tldextract(flow.request.url)
                        flow_entry = {"url":request_domain}
                        data.append(flow_entry)
                except:
                    continue
        except:
            return [domain,{}]


    # JS Cookies
    websiteData,websiteName = getJSSetCookies(domain,browser)
    for entry in data:
        url = entry['url']
        if url in websiteData:
            websiteData[url] += 1
        else:
            websiteData[url] = 1
            
    return [domain,websiteData]



def getJSSetCookies(websiteName,browser):
    websiteData = {}
    # print(websiteName)
    filePath = "/home/azafar2/OmniCrawl/data_round_3/{}/{}/{}_round_3.log.sqlite3".format(browser,websiteName,websiteName)
    if os.path.isfile(filePath):
        db = _DB(filePath)
        pools= db.read()
        count =0
        for j,p in enumerate(pools):
            try:
                for i,x in enumerate(p['frames']):
                    for entry in p["frames"][i]["js_logs"]:
                        try:
                            if entry['filename'] in browser_spec_reqs[browser]:
                                continue
                            api = (entry["api"])
                            if api == 'Document.cookie' and entry['method'] == "SET":
                            # domain
                                domainName = get_tldextract(entry['filename'])
                                if domainName not in websiteData:
                                    websiteData[domainName] = 1
                                else:
                                    websiteData[domainName] += 1
                        except:
                            count += 1
            except Exception as e:
                print(e)
                continue
        if count != 0:
            print (count)
    return websiteData,websiteName

# filepath = "/home/azafar2/OmniCrawl/data_round_3/chrome/microsoft.com/microsoft.com_round_3"
# results = getSetHeaderCookies(filepath)

# filepath = "/home/azafar2/OmniCrawl/data_round_3/chrome/microsoft.com/microsoft.com_round_3"
# results = getJSSetCookies("microsoft.com","chrome")
# print(results)

def getValidCommonDomains():
    valid_common_domains_file = '/home/azafar2/mobile_analysis/data/validCommonDomains_round_3.json'
    with open(valid_common_domains_file) as fp:
        data = json.load(fp)
        fp.close()
    domains = list(data.keys())
    return domains

def main():
    domains = getValidCommonDomains()
    for browser in browsers:
        filepaths = []
        browser_blocked_domains = {}

        for domain in domains:
            filepath = f'/home/azafar2/OmniCrawl/data_round_3/{browser}/{domain}/{domain}_round_3'
            if os.path.exists(filepath):
                filepaths.append(filepath)
        # filepaths = filepaths[:10] # test for 100 files only
        with Pool(processes=100) as pool:
            res = pool.map(getSetHeaderCookies,filepaths)
        data = {}
        for entry in res:
            domain = entry[0]
            flow_data = entry[1]
            data[domain] = flow_data
        
        # save the data
        with open(f"/home/azafar2/mobile_analysis/data/cookie_info/{browser}.json","w") as fp:
            json.dump(data,fp,indent=4)
            fp.close()
        print(f'browser checked: {browser}')

main()