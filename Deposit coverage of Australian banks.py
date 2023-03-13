#!/usr/bin/env python
# coding: utf-8

# In[1]:


# Web scraping bank data from IntelligentInvestor.com.au
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import csv
import pandas as pd
import re
from selenium.webdriver.common.by import By
from lxml import html
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

# Getting the base url
url = 'https://www.intelligentinvestor.com.au/investment-tools/shares?SectorID=40&TimePeriod=1&SecuritiesMovers=0&EqualityId=0&OrderBy=3&OrderByOrientation=Descending&Size=25&ExchangeID=ASX'
reqs = requests.get(url)
soup = BeautifulSoup(reqs.text, 'html.parser')

# Opening each banks URL

urls = []
for link in soup.find_all('a'):
    thelink = link.get('href')
    urls.append(thelink)

urls = urls[87:111]
co_urls = []
for i in urls:
    co_url = i + "/financials"
    co_urls.append(co_url)
    
driver = webdriver.Chrome()

driver.get('https://www.intelligentinvestor.com.au/investment-tools/shares?SectorID=40&TimePeriod=1&SecuritiesMovers=0&EqualityId=0&OrderBy=3&OrderByOrientation=Descending&Size=25&ExchangeID=ASX')
driver.maximize_window()


# In[3]:


balance_sheets = []
banks = []

# Extracting each balance sheet table as a DataFrame and creating list with dataframes
for url in co_urls:
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    balance_sheet = soup.find('table', {'class': 'table table-style-z'})
    
    if balance_sheet is not None:
        banks.append(url)
        table_rows = balance_sheet.find_all('tr')
        headers = [th.text.strip() for th in table_rows[0].find_all('th')]
        data = [[td.text.strip() for td in tr.find_all('td')] for tr in table_rows[1:]]
        df = pd.DataFrame(data, columns=headers)
        balance_sheets.append(df)
    else:
        print(f"No table found for URL: {url}")

# Extracting bank names
for i in range(len(banks)):
    banks[i] = banks[i][54:-11]

# Dropping irrelevant info
for i in range(len(balance_sheets)):
    balance_sheets[i] = balance_sheets[i].drop(['2021', '2020'], axis = 1)
        


# In[4]:


# Converting data to float for use in the ratios
for i in balance_sheets:
    if i['2022'][0] == '':
        i['2022'][0] = 0
    elif isinstance(i['2022'][0], str):
        i['2022'][0] = float(i['2022'][0].replace(',', ''))  
    if i['2022'][1] == '':
        i['2022'][1] = 0
    elif isinstance(i['2022'][1], str):
        i['2022'][1] = float(i['2022'][1].replace(',', ''))
    if i['2022'][12] == '':
        i['2022'][12] = 0
    elif isinstance(i['2022'][12], str):
        i['2022'][12] = float(i['2022'][12].replace(',', ''))  


# In[6]:


# Calculating the ratios where there is sufficient information

liquidity = []

for i in range(len(balance_sheets)):
    if balance_sheets[i].loc[12][1] != 0 and balance_sheets[i].loc[0][1] != 0 and balance_sheets[i].loc[1][1] != 0:
        ratio = (balance_sheets[i].loc[0][1] + balance_sheets[i].loc[1][1]) / balance_sheets[i].loc[12][1]
        liquidity.append(ratio)
    else:
        liquidity.append("Insufficient Information")
        
# Building DataFrame to list banks and their deposit coverage with liquid assets
aus_bank_deposit_coverage = pd.DataFrame({'Bank': banks, 'Deposit Coverage': liquidity})
aus_bank_deposit_coverage


# In[7]:


aus_bank_deposit_coverage.to_csv('aus_banks_deposit_coverage.csv', index=False)


# In[ ]:




