
# Mobile Browser Analysis

## Research Paper
This document describes the analysis of the mobile browser. You can read more about the analysis in our [paper](https://anupamdas.org/paper/CODASPY2023.pdf). Consider citing our work in your paper:
``` tex
@inproceedings{ahsan-codaspy2023,
		author  = {Ahsan Zafar and Anupam Das},
		title   = {Comparative Privacy Analysis of Mobile Browsers},
		booktitle = {Proceedings of the 13th ACM Conference on Data and Application Security and Privacy (CODASPY)},
		year ={2023},
		doi = {10.1145/3411763.3451633}
	}
```

## Data Methodology



### Overview
Our data collection methodology borrows crawling design from [OmniCrawl](https://github.com/OmniCrawl/OmniCrawl). We assume that the readers are capable of insantiating the OmniCrawl setup using their desired browser and can crawl the web using the documentation provided therein.

The OmniCrawl crawler produces two main files with each crawl:
1. Mitmdump file (request/responses)
2. API usage file (dynamic execution of APIs)

Additionally, you can find our enhanced tracking heuristics in  ```analysis_scripts/prelim.ipynb```

We are using 6 browsers in this privacy study:

1. Chrome
2. Brave
3. Firefox
4. Firefox Focus
5. DuckDuckGo
6. Safari

The table below lists the version number for each of these browsers that we have used. 

Additionally, it shows the base size of a valid file logged through mitmproxy. For example, if a website like ``microsoftonline.com`` is loaded on one of these browsers, the website may not be loaded properly since it is invlaid, however, in loading the website, each browser may make additional requests to the server to load configuration files.

| Browser       | Version | Size (KB) |
| ------------- | ------- | --------- |
| Chrome        | 83      | 160       |
| Firefox       | 96      | 1970      |
| Firefox Focus | 95      | 7800      |
| Brave         | 1.34    | 12        |
| Duck Duck Go  | 5.107   | 0         |
| Safari        | 15.4.1  | NA (=0)   |







### Data Cleaning

While preliminary cleansing relies on file size and does the basic job for us, we rely on programmatically purging dump files that fail to generate website data.

With regards to the crawled data, there are two files that are relevant to our analysis.

1. Mitmproxy dump file (e.g. google.com)
2. API log files (e.g. google.com.log.sqlite3)


To validate an mitmdump file, we look for a first-party response (200-399) in the dump file. If such a response exists, we can confirm that the website was indeed visited. 

The next step is to make sure that we have the valid API log files. This is simple as the base size file of a API log file is 8KB. If the browsers fails to get any valid response while visiting a website, the skeleton API log file that is created is 8KB minimum. This implies that any instance of a crawl which produced a file size that is greater than 8KB is most likely a valid file. Therefore, just by looking at this file size too, we can differentiate between valid and invalid file sizes.

Both cleaning steps are provided in `validDumpFiles.py`



## Analysis



The focus here is going to be the results derived from analysis on the mitmdump files and the API log files. The following analysis are performed:

1. Classification of trackers
   1. Statically compare ASTs of ground truth tracking scripts with the ones in our dataset.
   1. Dynamic Analysis

The analysis notebook can be found at `prelim.ipynb`

2. Prevelance of trackers in crawled dataset
   1. Tracker vendors and ratio of fingerprinting trackers and prevalence of tracking scripts among all scripts
The analysis notebook can be found at `prelim.ipynb`

3. Privacy test using ground truth from EasyList, EasyPrivacy, Disconnect and WhoTracksMe

The analysis scripts can be found at `prelim.ipynb`

4. Cookie analysis
   
   Cookie based analysis focuses on the cookies that were set by first and third party cookies. Note that there are 2 primary methods that can set cookies:
   1. JavaScript API `Cookie`
   2. Response Header `set-cookie`

   These analysis methods can be found in `analysis_scripts/cookie_info.py`
   


      




#### JS Collection

For JS Collection, we will be extracting content from the dump files (NOTE: we can also use OmniCrawl dump logs but since mitm dump logs are arguably more complete, we should extract js from there).

There are two kinds of JavaScripts in our dataset. The following code snippets will show how each is captured:

1. Inline JavaScripts

   1. ````javascript
      if 'Content-Type' in headers and 'text/html' in headers['Content-Type']:
        try:
        content = flow.response.content.decode('utf-8')
        soup = BeautifulSoup(content,'html.parser')
        _script_tags = soup.find_all('script')
        for script_tags in _script_tags:
          if script_tags:
            script_tag_contents = script_tags.string
          if script_tag_contents:
            script_tag_contents = jsbeautifier.beautify(script_tag_contents)
      			# save the JS
      ````

2. External JavaScripts

   1. ````javascript
      def getExternalScript(flow,content_encoding):
          code = ''
          # gzip encoding
          try:
              code = flow.response.content.decode('utf-8')
              code = jsbeautifier.beautify(code)
          except Exception as error:
              code = ''
              print('error< ',error)
          return code
      ````

​	Note: these snippets are from ``analysis_scripts/extractJs.py``

The name structure for these JS files is as follows:

1. Inline JavaScript

   1. ````javascript
      inline_js_hash = hashlib.sha1(script_tag_contents.encode('utf-8')).hexdigest()
      js_file_name = f'{website}_{domain}_inline_{inline_count}_{inline_js_hash}.js'
      ````

      Where website is the site that is being visited (e.g. ``bbc.com``) and domain is the response server like, inline_count is the order in which this particular js occurs in the html

2. External JavaScript

   1. ````javascript
      url_hash = hashlib.sha1(js_code.encode('utf-8')).hexdigest()
      js_file_name = f"{website}_{domain}_external_{url_hash}.js"
      ````

3. JsLog.json

   1. ````json
      "failures": [], # append all the flow.request.url
      "external_success" : {flow.request.url:code_hash},
      'internal_success' : {flow.request.url:[]} # append the inline scripts in order
      ````



#### Tracker Classification

##### Ground Truth

In order to identify the types of trackers in our dataset, we need a data source detailing the trackers and their classes. Following are some of the links I have discovered online that provide information on the trackers.

1. AdGaurd WhotracksMe [trackers](https://github.com/AdguardTeam/AdGuardHome/blob/master/client/src/helpers/trackers/whotracksme.json)
2. Disconnect Tracker [list](https://disconnect.me/trackerprotection#trackers-we-dont-block)
   1. Note there are **unblocked trackers** in the *Content* section of ``entities.json``
3. EasyPrivacy also stores infromation about the trackers.
4. Datasets available from earlier [works](https://www.pimcity-h2020.eu/publication/unveiling-web-fingerprinting-in-the-wild-via-code-mining-and-machine-learning/)

Our basic approach will be to crawl the known trackers and extract features out of them. To reduce noise, features that contain Web API information will be captured only. One approach that has been done in earlier [works](https://arxiv.org/pdf/2008.04480.pdf) is to use AST representation of the code, tokenize the output and extract ```parent:child``` relation that has child as the function or property of some Web API.



##### Methodology

We will be using two methods to identify fingerprinting APIs and Scripts in our datasets: Static Analysis and Dynamic Analysis

###### Static Analysis

The methodology in [previous works](https://www.pimcity-h2020.eu/publication/unveiling-web-fingerprinting-in-the-wild-via-code-mining-and-machine-learning/) have shown how Static Code Analysis can be used to identify fingerprinting scripts. 

Briefly, a set of patterns that closely resemble those found in fingerprinting scripts are generated. These patterns can be generated from ground truth or manually by creating AST expressions for code snippets that use enumerations of plugins, fonts or that probe properties of objects known for fingerprinting. It is better if we generate these patterns using code-snippets from or own dataset of suspected fingerprinters.

Next, these patterns are matched against AST expressions of scripts found in the wild. Note that after obtaining AST's of these scripts, to remove unnecessary subtrees, we only keep ``parent:child`` expressions that contain property, name or method that matches with the [Web APIs](https://developer.mozilla.org/en-US/docs/Web/API). For matching, we compute the Jaccard similarity score, computed as follows
$$
J(A,B) = \frac{|A \cap B|}{|A \cup B|} \\
$$
Where ``A`` is the collection of ground-truth patterns of fingerprinters and ``B`` is the collection of ``parent:child`` expressions of the script in the wild. Note that we will only be keep those ``parent:child`` expressions that have matches with Web APIs.

We associate this Jaccard score with the script. To classify a script as fingerprinter, we will need to define a threshold beyond which we can confidently establish a script as fingerprinter.

Note: We can also apply machine learning approach as used in earlier works.



**Challeneges**:

1. ``parent:child`` pair extraction
2. assembling list of Web APIs, their methods, properties and names





#### URL Categorization

The OpenWPM paper mentions that they gather the categories of the URLS by crawling ``sitereview.norton.com`` , however, when I attempted to do this, the website was able to catch automation and cloaked the original response by sending a template response that gave back nothing. Additionally, it seems that JavaScript is required to get the response since there is some redirection involved. Lastly, based on [github issues](https://github.com/PoorBillionaire/sitereview/issues/15), there is also an IP based restriction on the number of requests that can be made. 

Update: I confirmed, there was a restriction of 200 queries per session. After which, you have to manually verify a bot detection test.

``nortan_crawler.py``:

````python
with open('proxylog','rb') as fp:
  for flow in FlowReader(fp).stream():
    try:
      if flow.request.method=='POST' and response_url in flow.request.url:
        data = flow.response.content.decode('utf-8')

        data = jsbeautifier.beautify(data)
        data = json.loads(data)

        if 'resolvedDetail' in data and data['resolvedDetail']['resolveEnabled'] == False:
          iserror=True
          if str(domain) not in str(data['url']):
            iserror=True

          except Exception as error:
            print(error)
            data = {}
            iserror = True
````








### Safari Crawl
To my knowledge, there are two options for automation on Safari. 

1. The first option is to use **safaridriver** in MacOS to send REST API requests to the iOS device. Basically, since iOS 13, a remote automation feature was introduced in Safari that lets it be operated through safari webdriver from a MacOS. [This process](https://developer.apple.com/documentation/webkit/testing_with_webdriver_in_safari) is another selenium-based automation method for Safari. Currently, I have been testing this method but I have been running into a problem: even when I enable remote automation on Safari, the webdriver sends an error message that the remote automation is switched off. There is [an issue on GitHub](https://github.com/sitespeedio/sitespeed.io/issues/3160) that discusses this.
    

2. The second method involves using Appium along with SafariLauncher to automate the safari interactions. The purpose of SafariLauncher is to launch the browser on your app. Thereafter, Appium takes over the interactions between the browser and your client desktop. This method seems clean but I have run into a problem. In order to install SafariLauncher on your iOS device, you need to sign the binary of the app inside XCode. Now this is trivial if you have a developer credential however, it seems that with the developer profile that latest XCode manages, it won't allow the binary to be signed. Therefore, the build of the SafariLauncher fails.

We use the second method for the paper and the crawler script can be found at `crawler_scripts/safariCrawler.py`


### Android Crawl
For android, we use adb shell to automate user interactions to emulate organic web crawls. The process is simple and easy to follow as outlined in `crawler_scripts/client.py`

### Server
Additionally, we provide a server script that is initiates mitmproxy connections and gathers data. We assume that the users are able to leverage OmniCrawl as it also captures API executions. The server script can be found as `crawler_scripts/client.py`











