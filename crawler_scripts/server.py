# Multi-client server: This script accepts requests from multiple clients. For 5 browsers, We need
# 5 + 5 open ports. Each client needs a port where it can connect to the server. Further, an open port is needed so that
# that client's device can connect to an instance of mitmproxy and record/log the requests

# 1. Accept connection from client
# 2. Receive client credentials ([a] Browser name (that the client represents), [b] Website name (to be visited))

import os
import sys
import signal
import json
import socket
import subprocess, time, signal
import multiprocessing
import threading
from _thread import *
import asyncio

from mitmproxy import ctx
from mitmproxy.options import Options
from mitmproxy.proxy.config import ProxyConfig
from mitmproxy.proxy.server import ProxyServer
from mitmproxy.tools.dump import DumpMaster
from mitmproxy.io import FlowReader
from mitmproxy import http


ip = '172.16.122.65'
# ip = '152.14.92.31'
port = 50006
# phone_id = sys.argv[0]
client_count = 1 # expected number of clients to connect to. later this will be set to 6, representing the six browsers
mitmport_map = {"chrome":50001,"brave":50002,"ddg":50003,"firefox":50004,'focus': 50005}


# proc1 = subprocess.Popen("mitmproxy --listen-port 5580 --set block_global=false -w {}".format(website),shell=True)

class ProxyMaster(DumpMaster):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def run(self):
        try:
            DumpMaster.run(self)
        except KeyboardInterrupt:
            self.shutdown()


def createSocket():
    cleanSockets()
    thread_dict = {}
    s = socket.socket()
    print("binding to the following ip,port:",ip,port)
    s.bind((ip,port))
    s.listen()

    # p = multiprocessing.Pool(1)

    while True:
        print('socket is listening')
        c,addr = s.accept()
        browser_name = c.recv(1024).decode() # step 1: receive the browser name
        c.send("1".encode())
        print("browser name: ",browser_name)
        # main(c,browser_name)
        # break
        t = multiprocessing.Process(target=main,args=(c,browser_name,))
        # t = p.apply_async(main,args=(c,browser_name,))
        thread_dict[browser_name] = t # each client will be handled by a threaded main function that will only deal that particular browser
        t.start()

    # p.close()

def setupProxy(browser,website):
    options = Options(listen_host=ip, listen_port=mitmport_map[browser])
    # options.set(block_global=False)
    config = ProxyConfig(options)
    master = ProxyMaster(options, with_termlog=False, with_dumper=False)
    master.options.set('block_global=false')
    master.options.set('save_stream_file=./{}/{}'.format(browser,website))
    master.server = ProxyServer(config)
    # master.run()
    return master

# see source mitmproxy/master.py for details
def loop_in_thread(loop, m):
    asyncio.set_event_loop(loop)  # This is the key.
    m.run_loop(loop.run_forever)

def handleProxyClient(m):
    m.run()
    
def reportStatus(file_name):
    # checks a dump file for the presence of 200, 300 response status codes. Their presence signifies that the crawl was successful
    with open(file_name, 'rb') as fp:
        for flow in FlowReader(fp).stream():
            try:
                if flow.response.status_code >= 200 and flow.response.status_code <= 400:
                    return True
            except Exception as error:
                return False
        fp.close()
    return False

def cleanSockets():
    print("Cleaning ports and associated sockets")
    for br in mitmport_map:
        sock_port = mitmport_map[br]
        r = subprocess.Popen("kill -9 $(lsof -ti :{})".format(sock_port), shell =True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        out, err = r.communicate()
        if err:
            print("Error cleaning mitm instance associated with {} at portn {}: {}".format(br,sock_port,err))
        else:
            print("LOGS ({}): {} ".format(br,out))

    print("Cleaning previous server if it exists")
    r = subprocess.Popen("kill -9 $(lsof -ti :{})".format(port), shell =True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    out, err = r.communicate()
    if err:
        print("error cleaning previous server at port {}: {}".format(port,err))
    else:
        print("successfully cleaned previous server")
        


def main(c,browser_name):
    instance_port = mitmport_map[browser_name] 

    while True:
        website = c.recv(1024).decode() # step 2: receive the website to load

        if website == "-1": # step 4: receive abort code - all websites have loaded - close down the process
            print("aborting")
            c.close()
            return 0


        print("received website: {}, opening proxy instance".format(website))

        m = setupProxy(browser_name,website)
        # m.run()

        p = multiprocessing.Process(target=handleProxyClient,args=(m,))
        p.start()

        # wait for mitmproxy to start
        while True:
            r = subprocess.Popen("lsof -nP -i4TCP:{} | grep LISTEN".format(instance_port), shell =True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            out, err = r.communicate()
            for l in out.splitlines():
                if str(instance_port) in l.decode():
                    found = 1
                    break
            if found:
                break

        time.sleep(4)
        

        c.send("1".encode()) # step 2.1: mitm instance up and running. signal the client to start loading the website

        print("Process id {}".format(p.pid))

        sig = c.recv(1024).decode() # step 3: wait for stop signal before closing instnace
        if sig == "0":
            dumpFilePath = './{}/{}'.format(browser_name,website)
            dumpExists = reportStatus(dumpFilePath)

            if dumpExists: # first crawl successful
                ctx.master.shutdown()
                os.system("kill -9 $(lsof -ti :{})".format(instance_port)) # make sure that the spawned mitm process is killed, otherwise next instance wont begin
                print("killing instance, crawl timeout completed")
                c.send("0".encode()) # step 3.1: sending 0 signal to client to let it know that the website has loaded properly and a useable dump file exists
            else: # first crawl unsuccessful
                ctx.master.shutdown()
                os.system("kill -9 $(lsof -ti :{})".format(instance_port)) # make sure that the spawned mitm process is killed, otherwise next instance wont begin
                print("killing instance, website not loaded properly")

                c.send("-1".encode()) # step 3.1: -1 signifies to the client that the website wasnt loaded properly, prepare for the second attempt

                c.recv(1024).decode() # step 3.1b the client has completed onboarding, the server can now run the proxy

                p = multiprocessing.Process(target=handleProxyClient,args=(m,))
                p.start()
                # add delay here so the proxy has time to set up properly
                c.send("1".encode()) # step3.2: ask the client to load the website now 
                second_attempt_sig = c.recv(1024).decode() # step 3.3: wait for stop signal before closing instnace

                ctx.master.shutdown()
                os.system("kill -9 $(lsof -ti :{})".format(instance_port)) # make sure that the spawned mitm process is killed, otherwise next instance wont begin
                print("killing instance, crawl timeout completed")
                dumpFilePath = './{}/{}'.format(browser_name,website)
                dumpExists = reportStatus(dumpFilePath)
                if dumpExists:
                    c.send("0".encode()) # step 3.4: inform client if the second crawl was successful
                else:
                    c.send("-1".encode()) # step 3.4: inform client if the second crawl was unsuccessful

        print("mimtproxy has been shut down")
createSocket()


