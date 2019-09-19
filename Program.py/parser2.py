import pandas as pd
from bs4 import BeautifulSoup
from requests import get
import os
import urllib.request
from xbrl import XBRLParser, GAAP, GAAPSerializer


#----------------DOWNLOAD REQUISITE FILES--------------------------------------

#
##Step 1: Define funtions to download filings
def get_list(ticker):

    base_url_part1 = "http://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK="
    base_url_part2 = "&type=&dateb=&owner=&start="
    base_url_part3 = "&count=100&output=xml"
    href = []
    
    for page_number in range(0,2000,100):
    
        base_url = base_url_part1 + ticker + base_url_part2 + str(page_number) + base_url_part3
        
        sec_page = urllib.request.urlopen(base_url)
        sec_soup = BeautifulSoup(sec_page)
        
        filings = sec_soup.findAll('filing')
        
        for filing in filings:
            report_year = int(filing.datefiled.get_text()[0:4])
            if (filing.type.get_text() == "10-K") & (report_year > 2012):
                print(filing.filinghref.get_text())
                href.append(filing.filinghref.get_text())
    
    return href
def download_report(url_list,dir_path):
    
    target_base_url = 'http://www.sec.gov'
    
    # type = 'EX-101.INS'
    target_file_type = u'EX-101.INS'
    
    for report_url in url_list:
        report_page = urllib.request.urlopen(report_url)
        report_soup = BeautifulSoup(report_page)
        
        xbrl_file = report_soup.findAll('tr')
        
        for item in xbrl_file:
            try:
                if item.findAll('td')[3].get_text() == target_file_type:
                    if not os.path.exists(dir_path):
                        os.makedirs(dir_path)
                             
                    target_url = target_base_url + item.findAll('td')[2].find('a')['href']
                    print ("Target URL found!")
                    print ("Target URL is:", target_url)
                    
                    file_name = target_url.split('/')[-1]
                    print(file_name)
                   
                    xbrl_report = urllib.request.urlopen(target_url)
                    output = open(os.path.join(dir_path,file_name),'wb')
                    output.write(xbrl_report.read())
                    output.close()
                    
            except:
                pass
## Step 2: Define funtions to download filings
## Import tickers
#TickerFile = pd.read_csv("companylist.csv")
#Tickers = TickerFile['Symbol'].tolist()
#
#
company = input("companyticker: ")
for ticker in company:
    url_list= get_list(ticker)
    base_path = "./Downloaded_Filings"
    dir_path = base_path + "/"+ticker
    download_report(url_list,dir_path)


#--------------------------PARSING XML---------------------------------------------


path = 'C:/Users/Busin/Desktop/Python/Investment Analysis/Downloaded_Filings/' + company + '/'

files = []
# r=root, d=directories, f = files
for r, d, f in os.walk(path):
    for file in f:
        if '.xml' in file:
            files.append(os.path.join(r, file))

print(files)
Years = []
for f in files:
    filename = f[79:83]
    Years.append(filename)
print(Years)    


for file in files:
    #open and read the XML File
    xml = open(file,'r').read()
    #slices the filepath to separate just the year, used for naming the output
    filename = file[79:83]
    #xml parse with beautiful soup
    soup = BeautifulSoup(xml, 'lxml')
    tags = soup.find_all()
    #crate blank dataframe to append data from the XML File
    df = pd.DataFrame(columns=['field','period','value']) 
    
    #For loop that should takes the gaap items and appends to dataframe
    for tag in tags:
        if ('us-gaap:' in tag.name   # only want gaap-related tags 
                and tag.text.isdigit()): # only want values, no commentary
            #a = re.match("^C_"+ re.escape(cik) + "_[0-9]", tag['contextref'])     
                name = tag.name.split('gaap:')[1]
                cref = tag['contextref'][-8:-4]
                value = tag.text
                df = df.append({'field': name, 'period': cref, 'value': value}, ignore_index=True)
    df = df.drop(df[df.period != filename].index)
#    print(df)
    df.to_excel('C:/Users/Busin/Desktop/Python/Investment Analysis/Downloaded_Filings/TSLA/' + filename + ".xlsx")
#                df.to_excel('C:/Users/Busin/Desktop/Python/Investment Analysis/Downloaded_Filings/TSLA/' + filename + ".xlsx")
    #I only want data for the year of the document, so this line calculates the current year of the doc
#                maximum = str(df['period'].max())
#    #This removes any data that isn't from the current year of document
#                df = df.drop(df[df.period != maximum].index)
    #export to excel
     
print("Done")
