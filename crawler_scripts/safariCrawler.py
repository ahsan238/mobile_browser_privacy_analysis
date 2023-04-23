from xml.dom.xmlbuilder import DOMEntityResolver
from selenium.webdriver.common.by import By
from selenium import webdriver
import unittest, time
 # /opt/homebrew/Caskroom/android-sdk/4333796/tools

import os
import sys
import json
import socket
import time
import shutil
import os
import platform
import base64

import argparse

import csv
import pandas as pd
# from zmq import device
from timeout import timeout

ip = '192.58.122.65'
# ip = '127.0.0.1'
# ip = '152.14.92.31'
# browser = sys.argv[1]
# phone_id = sys.argv[2]
# appium_port = 4723

# iphone_id = '00008101-0005689C3C11001E' # Ahsan iPhone
iphone_id = '00008030-0014446C3C28C02E' # lab iPhone

isAndroid = False
platform_name = 'iOS'

mitmport_map = {"chrome":50001,"brave":50002,"ddg":50003,"firefox":50004,'focus': 50005,'Safari':50007} # not relevant at the moment

port = 50006 # the port at which the server accepts all client conn
TIMEOUT = 30 # change this to 30

trancoFilename = "../tranco_87WV.csv"

crawledFile = 'crawled.json'
failedFile = 'failed.json'

crawledWebsites = {}
failedWebsites = {}


EMPTY_URLS = {
    "Safari": "about:blank",
    "chrome": "about:blank",
    "brave": "about:blank",
    "focus": "about:blank",
    "firefox": "about:blank",
    "ddg": "about:blank"

}



def getTrancoList():
    csv = pd.read_csv(trancoFilename)

    website_list = [row.values[1] for ind, row in csv.iterrows()]
    website_list = website_list[:10000]

    return website_list
    
def getAndroidBrowserConfigurations(browserName):
    if browserName == "chrome":
        return {"appPackage":"com.android.chrome","appActivity":"com.google.android.apps.chrome.Main"}
    elif browserName == "firefox":
        return {"appPackage":"org.mozilla.firefox","appActivity":".App"}
    elif browserName == "focus":
        return {"appPackage":"org.mozilla.focus","appActivity":"org.mozilla.focus.activity.MainActivity"}
    elif browserName == "ddg":
        return {"appPackage":"com.duckduckgo.mobile.android","appActivity":"com.duckduckgo.app.launch.Launcher"}
    elif browserName == "brave":
        return {"appPackage":"com.brave.browser","appActivity":"com.google.android.apps.chrome.Main"}
    
def getCapabilities(browserName="",platformName='Android',deviceName="",appPackage="",appActivity="",):
    common_caps = {
        "platformName": platformName,
        "deviceName": deviceName,
    }
    android_caps = {
        **common_caps,
        "appPackage": appPackage,
        "appActivity":appActivity,
    }
    ios_caps = {
        **common_caps,
        "browserName": browserName,
        'automationName': 'XCUITest',
        'udid': iphone_id,
        "xcodeOrgId": "4M3EPJW8BX", 
        "xcodeSigningId": "iPhone Developer",
    }
    return android_caps if platformName=='Android' else ios_caps

class Crawler():
    def __init__(self,browser,appium_port,capabilities,phone_id):
        self.browser = browser
        self.appium_port = appium_port
        self.capabilities = capabilities
        self.phone_id = phone_id

    @timeout(120)
    def visitWebsite(self,website_url,img_path):
        adbInitCommand = "adb -s {} ".format(self.phone_id)
        swipeBottom = adbInitCommand + "shell input touchscreen swipe 530 1420 530 250"
        try:
            # Load website
            self.driver = webdriver.Remote('http://localhost:{}/wd/hub'.format(str(self.appium_port)), self.capabilities)
            self.driver.set_page_load_timeout(5)
            self.driver.set_script_timeout(100)
            self.driver.get(website_url)
            time.sleep(TIMEOUT/2)

            # Swipe down
            if self.browser == 'Safari':
                self.driver.execute_script('mobile: scroll', {'direction': 'down'})
            else:
                if os.system(swipeBottom) != 0:
                    print("Failed opening tab manager")
                    return
                time.sleep(TIMEOUT/2)

            # Take a screenshot
            screenshotBase64 = self.driver.get_screenshot_as_base64()
            imgdata = base64.b64decode(screenshotBase64)
            with open(img_path, "wb") as fh:
                fh.write(imgdata)
            time.sleep(TIMEOUT/2)

            # Quit session
            emptyurl = EMPTY_URLS[self.browser]
            self.driver.get('http://240.240.240.240/stop')
            if self.browser=='Safari':
                self.driver.execute_script("mobile: terminateApp", {'bundleId': 'com.apple.Safari'})
            self.driver.quit()
        except Exception as e:
            print("Error visiting website: ",e)



def establishConnection(ip,port):
    s = socket.socket()
    print('establishing',ip,port)
    s.connect((ip,port))
    print('connection established')
    return s


def resetLogFiles():
  with open("crawled.json",'w') as fp:
    json.dump({},fp,indent=4)
    fp.close()

  with open("failed.json",'w') as fp:
    json.dump({},fp,indent=4)
    fp.close()

  if os.path.isdir("./screenshots"):
    shutil.rmtree("./screenshots")
    os.mkdir("./screenshots")


def initLogFiles():
  t1 = {} # crwaled
  t2 = {} # failed
  
  if os.path.isfile("crawled.json"):
    with open("crawled.json") as fp:
      t1 = json.load(fp)
      fp.close()
  else:
    with open("crawled.json",'w') as fp:
      json.dump({},fp,indent=4)
      fp.close()

  if os.path.isfile("failed.json"):
    with open("failed.json") as fp:
      t2 = json.load(fp)
      fp.close()
  else:
    with open("failed.json",'w') as fp:
      json.dump({},fp,indent=4)
      fp.close()
  
  return t1, t2

def updateLogWithWebsite(logfile, logDict, website,val):
  if website not in logDict:
    logDict[website] = val
  else:
    logDict[website] += val

  with open(logfile) as fp:
    temp = json.load(fp)
    fp.close()

  if website not in temp:
    temp[website] = val
  else:
    temp[website]+= val

  with open(logfile,'w') as fp:
    json.dump(temp,fp,indent=4)
    fp.close()

def initDir():
  if not os.path.isdir("./screenshots"):
    os.mkdir("./screenshots")

def removeWebsiteFromLog(logfile,logDict,website):
    if website in logDict:
        del logDict[website]
    with open(logfile) as fp:
        temp=json.load(fp)
        fp.close()
    del temp[website]
    if website in temp:
        del temp[website]
    with open(logFile,'w') as fp:
        json.dump(temp,fp,indent=4)
        fp.close()


def start(args):
    # onboarding
    # resetLogFiles()
    failedCount = 0
    crawledWebsites, failedWebsites = initLogFiles()
    websites = getTrancoList()
    # websites = ['google.com','ahsan238.github.io','microsoft.com']
    crawled = list(crawledWebsites.keys())
    failed = list(failedWebsites.keys())
    # crawled = []
    initDir()

    # crawler initiation
    conf = ''
    if args.platform_name=='Android':
        conf = getAndroidBrowserConfigurations(args.browser)
        device_capabilities = getCapabilities(browserName=args.browser,platformName=args.platform_name,deviceName=args.phone_id,appPackage=conf['appPackage'],appActivity=conf['appActivity'])
    else:
        device_capabilities = getCapabilities(browserName=args.browser,platformName=args.platform_name,deviceName=args.phone_id,appPackage='',appActivity='')
    
    print()

    crawler = Crawler(args.browser,appium_port=args.appium_port,capabilities=device_capabilities,phone_id=args.phone_id)

    # initiate connection with proxy server
    s = establishConnection(ip,port)

    s.send(args.browser.encode()) # step 1: send the browser name

    s.recv(1024).decode() # step 1.1: get confirmation

    exceptionSites = ['ted.com']
    exceptionSites = []

    for w in websites:
        if failedCount >= 5:
            break

        if w not in failed:
            print(w," already crawled")
            continue

        print('crawling ',w)

        s.send(w.encode()) # step 2: send the website name

        sig = s.recv(1024).decode() # step 2.1: if signal == "1", this means server has mitmproxy server up and running. the client can start loading the website.

        websitename = "http://"+w

        crawler.visitWebsite(websitename,'./screenshots/{}.jpg'.format(w))

        s.send("0".encode()) # step 3: send success code

        fileExistsSig = s.recv(1024).decode() # step 3.1: make sure the dump file exists at the server end

        if fileExistsSig == "0":
            failedCount=0
            print('website loaded successfully')
            removeWebsiteFromLog('failed.json',failedWebsites,w)
            updateLogWithWebsite("crawled.json",crawledWebsites,w,1)
        elif fileExistsSig == "-1":
            print('first launch failed')
            s.send("1".encode()) # step 3.1b: onboarding has been completed. Ask the server to start the proxy
            relaunchStatus = s.recv(1024).decode() # step 3.2: signal from server to confirm if they are ready for another launch
            if relaunchStatus == "1": # the server has set up another mitm instance. launch the website again
                websitename = "http://www"+w
                crawler.visitWebsite(websitename,'./screenshots/{}.jpg'.format(w))
            s.send("0".encode()) # step 3.3: send success code so that server can close the mitmproxy instance
            sig = s.recv(1024).decode() # step 3.4: ask server if the website was loaded successfully. if not then keep it in the log

            if sig == "0":
                failedCount=0
                print('second launch successful')
                removeWebsiteFromLog('failed.json',failedWebsites,w)
                updateLogWithWebsite("crawled.json",crawledWebsites,w,1)
            elif sig =="-1":
                failedCount+=1
                print('second launch failed')
                # updateLogWithWebsite("crawled.json",crawledWebsites,w,-1)
                updateLogWithWebsite("failed.json",failedWebsites,w,1)
        sys.stdout.flush()
        sys.stderr.flush()

    s.send("-1".encode()) # signal for crawl completion
    return





@timeout(10)
def hangout():
    try:
        time.sleep(20)
        print("hey there")
    except:
        print('exception in function')
    
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--browser", default="Safari",help="specify the name of mobile browser", choices=['Safari','ddg','chrome','firefox','focus','brave'])
    parser.add_argument("--phone_id",help="phone id of mobile (='iPhone' if iPhone)",default="iPhone")
    parser.add_argument("--appium_port",help="port number on which appium server is listening",default=4723,type=int)
    parser.add_argument("--platform_name",default='iOS',help='iOS or Android',choices=['iOS','Android'])
    args = parser.parse_args()
    print(args.browser,args.phone_id,args.platform_name)
    start(args)

        

        
