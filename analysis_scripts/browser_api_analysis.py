import json
import os
import data_processing_utilities as utils
import zlib
import sqlite3
from itertools import repeat
from functools import partial
from multiprocessing import Pool, TimeoutError


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


def getListOfCrawledWebsites(browser):
    pathto = "/home/azafar2/mobile_analysis/data/validCommonDomains_round_4.json"
    with open(pathto) as fp:
        domains = json.load(fp)
        fp.close()
    return domains

def saveAsJson(filename,data):
	with open(filename,'w') as fp:
		json.dump(data,fp,indent=4)
	fp.close()

with open("/home/azafar2/mobile_analysis/data/browser_specific_requests.json") as fp:
    browser_spec_reqs = json.load(fp)
    fp.close()


def getAPIList(websiteName,browser):
	websiteData = {}
	# print(websiteName)
	filePath = "/home/azafar2/OmniCrawl/data_round_4/{}/{}/{}_round_4.log.sqlite3".format(browser,websiteName,websiteName)
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
								print(browser, entry['filename'])
								continue
							api = (entry["api"])
							if api not in websiteData:
								websiteData[api] = {"count":1,"files":[entry['filename']]}
							else:
								websiteData[api]["count"] += 1
								websiteData[api]["files"].append(entry['filename'])
						except:
							count += 1
			except Exception as e:
				print(e)
				continue
		if count != 0:
			print (count)
	return websiteData,websiteName

def start():
	browsers = ["chrome",'brave','Safari','firefox','focus','ddg']
	for browser in browsers:
		d = {"gatheredAPIs": [],"websites":{}}
		files = list(getListOfCrawledWebsites(browser).keys())
		with Pool(processes=100) as pool:
			# res = pool.map(getAPIList,zip(files,repeat(browser)))
			res = pool.map(partial(getAPIList,browser=browser),files)
		for i in res:
			websiteData, websiteName = i[0], i[1]
			foundapis = list(websiteData.keys())
			d["gatheredAPIs"] = list(set(d["gatheredAPIs"]+foundapis))
			d["websites"][websiteName] = websiteData
		print(browser," Total websites: ",len(list(d['websites'].keys())))
		# saveAsJson(f"/home/azafar2/mobile_analysis/data/api_accesses/{browser}_temp.json",d)
		saveAsJson(f"/home/azafar2/mobile_analysis/data/api_accesses_round_4/{browser}_temp.json",d)

start()