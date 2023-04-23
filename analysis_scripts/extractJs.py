from functools import partial
import os
from os import listdir
from os.path import isfile, join
import bz2
from bz2 import BZ2File
from pathlib import Path
import json
import hashlib
import threading
from multiprocessing import Process, Pool
import multiprocessing
from tld import get_fld
import jsbeautifier
from urllib.request import Request, urlopen
import zlib
from mitmproxy import http
import sys
from mitmproxy.io import FlowReader
from bs4 import BeautifulSoup
from tqdm import tqdm


import data_processing_utilities as helper
from collections import Counter
import time
import tld


collection_path = '/home/azafar2/OmniCrawl/data_round_3'


# browser specific requests that need to be ignored
with open("/home/azafar2/mobile_analysis/data/browser_specific_requests.json") as fp:
    browser_spec_reqs = json.load(fp)
    fp.close()

def saveJs(code,filepath):
    with open(filepath,'w') as fp:
        fp.write(code)
        fp.close()

def saveAsJson(data,filepath):
    with open(filepath,'w') as fp:
        json.dump(data,fp,indent=4)
        fp.close()

def getExternalScript(flow,content_encoding):
    code = ''
    # gzip encoding
    try:
        code = flow.response.content.decode('utf-8')
        code = jsbeautifier.beautify(code)
    except Exception as error:
        code = ''
        # print('error< ',error)
    return code


def processDumpFile(filepath,output_dir):
    success_count = 0
    failure_count = 0
    external = 0
    inline = 0
    total_req = 0

    browser = filepath.split('/')[-3]
    website = filepath.split('/')[-2]

    js_log = {"failed":[],"external_success":{},'inline_success':{}} # keeps logs of sha1 of js extracted and notes any failed extractions
    js_path_to_save = f"/home/azafar2/mobile_analysis/js_scripts_round_3/{browser}/{website}"

    # check if output_dir exists
    if not os.path.exists(output_dir):
        print(f'{output_dir} does not exist')
        quit()
    # check if browser_dir exists
    browser_dir = os.path.join(output_dir,browser)
    if not os.path.exists(browser_dir):
        os.mkdir(browser_dir)
    # check if js_path_to_save exists
    js_path_to_save = os.path.join(browser_dir,website)
    if not os.path.exists(js_path_to_save):
        os.mkdir(js_path_to_save)

    js_log_path_to_save = os.path.join(js_path_to_save,'js_extraction_log.json')

    # js_log_path_to_save = f"/home/azafar2/mobile_analysis/js_scripts/{browser}/{website}/js_extraction_log.json"

    try:
        with open(filepath,'rb') as fp:
            for flow in FlowReader(fp).stream():
                total_req += 1
                if not hasattr(flow,'request'):
                    continue
                # ignore injected urls
                try:
                    if flow.request.url in browser_spec_reqs[browser]:
                            continue
                    if '240.240.240.240' in flow.request.url:
                        continue
                except AttributeError:
                    print(f'Attribute Error')

                # extract javascripts
                try:
                    domain = get_fld(flow.request.url)
                    headers = flow.response.headers
                    
                    # external javascript
                    if 'Content-Type' in headers and 'javascript' in headers['Content-Type']:
                        if 'Content-Encoding' in headers:
                            content_encoding = headers['Content-Encoding']
                        else:
                            content_encoding = ''
                        js_code = getExternalScript(flow,content_encoding)
                        if js_code == '':
                            js_log['failure'].append(flow.request.url)
                        else:
                            # save the external js
                            external+= 1
                            code_hash = hashlib.sha1(js_code.encode('utf-8')).hexdigest()
                            js_file_name = f"{website}_{domain}_external_{code_hash}.js"
                            js_file_path = os.path.join(js_path_to_save,js_file_name)
                            saveJs(js_code,js_file_path)
                            js_log['external_success'][flow.request.url] = js_file_name

                    
                    # in-line javascripts
                    if 'Content-Type' in headers and 'text/html' in headers['Content-Type']:
                        try:
                            content = flow.response.content.decode('utf-8')
                            soup = BeautifulSoup(content,'html.parser')
                            _script_tags = soup.find_all('script')
                            inline_count = 0
                            for script_tags in _script_tags:
                                if script_tags:
                                    script_tag_contents = script_tags.string
                                    if script_tag_contents:
                                        script_tag_contents = jsbeautifier.beautify(script_tag_contents)
                                        inline_count += 1
                                        inline += 1
                                        # save the inline js
                                        inline_js_hash = hashlib.sha1(script_tag_contents.encode('utf-8')).hexdigest()
                                        js_file_name = f'{website}_{domain}_inline_{inline_count}_{inline_js_hash}.js'
                                        inline_js_file_path = os.path.join(js_path_to_save,js_file_name)
                                        if flow.request.url not in js_log['inline_success']:
                                            js_log['inline_success'][flow.request.url] = []
                                        js_log['inline_success'][flow.request.url].append(js_file_name)
                                        saveJs(script_tag_contents,inline_js_file_path)
                                        
                        except Exception as error:
                            failure_count += 1
                            # print(flow.request.url, error)

                except Exception as error:
                    continue
                    print(f'error @ flow reader: {error}')
    
    
        saveAsJson(js_log,js_log_path_to_save)
                
        fp.close()
    except:
        print (f'Error while handling website :{website}, browser :{browser}')
    # print(f'external: {external}')
    # print(f'inline: {inline}')
    # print(f'failure count: {failure_count}')



def _main():
    browsers = ['brave']
    cpu_to_spare = 4
    cpu_to_use = multiprocessing.cpu_count() - cpu_to_spare
    output_dir = '/home/azafar2/mobile_analysis/js_scripts_round_3/'
    # dumpFilePath = f'/home/azafar2/OmniCrawl/data/chrome/bbc.com/bbc.com'
    for browser in browsers:
        common_domains_dumps = helper.get_common_dump_paths(browser)
        with Pool(processes=100) as pool:
            with tqdm(total=len(common_domains_dumps)) as pbar:
                res = []
                for result in pool.imap(partial(processDumpFile,output_dir=output_dir),common_domains_dumps):
                    res.append(result)
                    pbar.update(1)



if __name__ == "__main__":
    _main()

