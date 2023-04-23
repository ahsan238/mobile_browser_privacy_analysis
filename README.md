# mobile_browser_privacy_analysis

---
tags: Mobile Browser
---
# Mobile Browser Analysis

This document describes the analysis of the mobile browser

## Data Methodology



### Overview

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



I have manually checked some of the files on Safari data, valid and invalid, and there seems to be no base file size that can differentiate between valid and invalid. Most likely this is because in each iteration (crawl of a website), the Safari browser seems to be making random requests to the server (or OS level requests). We need to filter out invalid websites from the Android browsers and purge them from Safari. Next, we will need to load the remaining mitm dump files and purge the ones that are not loaded properly. Lastly, we need to look at API logs that were created and check which websites logs were not loaded properly. These three steps will purge all the unecessary website data from our browsers. We should then perform analysis only on those website data that are left behind.



### Data Cleaning

With regards to the crawled data, there are two files that are relevant to our analysis.

1. Mitmproxy dump file (e.g. google.com)
2. API log files (e.g. google.com.log.sqlite3)

Since we are interested in only the valid website data for our analysis, we keep these two files in consideration for data cleaning process. More specifically, we have to find out a way to ensure that both the Mitmproxy dump file and the API log file are valid (by valid, I mean they are populated). If either of the two files are incomplete or corrupted, we may not be able to produce a fair comparison between the browsers. 

To validate an mitmdump file, we look for a first-party response (200-399) in the dump file. If such a response exists, we can confirm that the website was indeed visited. 

The next step is to make sure that we have the valid API log files. This is simple as the base size file of a API log file is 8KB. If the browsers fails to get any valid response while visiting a website, the skeleton API log file that is created is 8KB minimum. This implies that any instance of a crawl which produced a file size that is greater than 8KB is most likely a valid file. Therefore, just by looking at this file size too, we can differentiate between valid and invalid file sizes.

We use both these methods to find invalid files and take their unions. The results are following:

| Browser    | Valid |
| ---------- | ----- |
| Chrome     | 9358  |
| Brave      | 9074  |
| Firefox    | 8756  |
| Focus      | 7100  |
| DuckDuckGo | 9217  |
| Safari     | 8609  |

Note: These results were produced using the following script: ``/home/azafar2/mobile_analysis/scripts/validDumpFiles.py``. These readings were taken at *04/26/2022:7:28AM*



#### URL Categories

About 6798 domains were found to be common at this point. The figure below shows the categories of these domains

![Common Domains Category 2022-04-26 at 7.54.15 AM](/Users/ahsanzafar/Desktop/Common Domains Category 2022-04-26 at 7.54.15 AM.png)

It is possible that the total counts shown in this plot rise beyond the number of common domains. This is because each domain can have more than one category.

#### Content

I also took the first 1000 common requests and looked at the top content. Results shown in the table below.

| Browser | Image | javascript | html  | Json  | css  | font | plain | video | Audio | octet-stream | Xml  | Other |
| ------- | ----- | ---------- | ----- | ----- | ---- | ---- | ----- | ----- | ----- | ------------ | ---- | ----- |
| Safari  | 50468 | 31979      | 12866 | 8994  | 5937 | 3609 | 4217  | 792   | 32    | 1185         | 660  | 523   |
| Chrome  | 53064 | 32222      | 16882 | 8985  | 6127 | 3031 | 5510  | 288   | 25    | 1124         | 218  | 271   |
| Brave   | 50883 | 32188      | 16430 | 9694  | 6062 | 3011 | 4471  | 318   | 26    | 1058         | 225  | 328   |
| Firefox | 45293 | 33463      | 13014 | 11406 | 6150 | 3843 | 4182  | 260   | 25    | 3028         | 264  | 847   |
| Focus   | 46808 | 30943      | 16614 | 14092 | 5740 | 3366 | 4462  | 276   | 52    | 2115         | 276  | 365   |
| DDG     | 38230 | 18291      | 6944  | 5729  | 4335 | 2981 | 975   | 246   | 20    | 911          | 47   | 507   |



## Analysis

#### Research Plan

The focus of this section is going to be the results derived from analysis on the mitmdump files and the API log files. Note that the list is non-exhaustive and still a work in progress. These results are performed on the top 1K website data. The following analysis are intended to be performed:

1. Classification of trackers
   1. Statically compare ASTs of ground truth tracking scripts with the ones in our dataset.
   1. Dynamic Analysis (yet to be decided)

2. Prevelance of trackers in crawled dataset
   1. Tracker vendors and ratio of fingerprinting trackers and prevalence of tracking scripts among all scripts

3. Privacy test using ground truth from EasyList, EasyPrivacy and Disconnect.
   1. Can also do whotracksme

4. Cookie analysis

   1. Refer to [this](https://www3.cs.stonybrook.edu/~mikepo/papers/firstparty.www21.pdf) paper

5. Web Cloaking - script behavior changes across browser

   1. Comparing the dynamic execution pattern of fingerprintinig APIs in common scripts

   2. Compare Jaccard Similarity Index among scripts (from various browser) to show change in behavior

   3. Use prominence metric to show the impact of cloacking scripts based on the sites they appear on. To give a concrete example, ``google-analytics.js`` is an analytic script that appears on top 90 domains in Tranco's list. To establish it's prominence, we aggregate the prominence value of hosting domains (domains where this script was executed).

      Prominence metric is as follows:
      $$
      Prominence(t) = \sum\nolimits_{edge(s,t)} = \frac{1}{rank(s)}
      $$
      




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

​	Note: these snippets are from ``/home/azafar2/mobile_analysis/scripts/extractJs.py``

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





#### BackLog

1. Loggin execution context of known trackers by embedding those scripts in an empty HTML and logging the API Calls. That is your ground truth (for Dynamic Analysis) and then you can compare it with the logs of scripts found in the wild.

2. Do dynamically injected inline scripts get recorded on mitmproxy log? To test this, embed the following code in an empty HTML and test?

   ````javascript
   (function() {
       var hostName = window.location.host;
       if (!((hostName.indexOf('content-') >= 0) || (hostName.indexOf('pre-production') >= 0) || (hostName.indexOf('localhost') >= 0))) {
           document.write('<script src="https:\/\/cdn-ukwest.onetrust.com\/scripttemplates\/otSDKStub.js" data-document-language="true" type="text\/javascript" charset="UTF-8" data-domain-script="2a76c653-4097-454f-9172-b4ab95061efd"><\/script>');
       }
   })();
   ````

3. How is our paper different? Make a table that shows previous works and compares the core findings/analysis done in each paper and compare it with what you have done. Something like [this](https://dl.acm.org/doi/pdf/10.1145/2976749.2978313).

### 



### Safari Crawl
To my knowledge, there are two options for automation on Safari. 

1. The first option is to use **safaridriver** in MacOS to send REST API requests to the iOS device. Basically, since iOS 13, a remote automation feature was introduced in Safari that lets it be operated through safari webdriver from a MacOS. [This process](https://developer.apple.com/documentation/webkit/testing_with_webdriver_in_safari) is another selenium-based automation method for Safari. Currently, I have been testing this method but I have been running into a problem: even when I enable remote automation on Safari, the webdriver sends an error message that the remote automation is switched off. There is [an issue on GitHub](https://github.com/sitespeedio/sitespeed.io/issues/3160) that discusses this.
    
    *I will also highlight an obvious shortfall of this method is that it is detectable by websites and therefore may not be a recommended way.*

2. The second method involves using Appium along with SafariLauncher to automate the safari interactions. The purpose of SafariLauncher is to launch the browser on your app. Thereafter, Appium takes over the interactions between the browser and your client desktop. This method seems clean but I have run into a problem. In order to install SafariLauncher on your iOS device, you need to sign the binary of the app inside XCode. Now this is trivial if you have a developer credential however, it seems that with the developer profile that latest XCode manages, it won't allow the binary to be signed. Therefore, the build of the SafariLauncher fails.











