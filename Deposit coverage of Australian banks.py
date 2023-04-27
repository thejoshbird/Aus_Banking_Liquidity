# Web scraping bank data from Market Watch
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

tickers = ["CBA","NAB","WBC","ANZ","BEN","BOQ","BFL","VUK","JDO","LFG","HGH","HLI","PPM","MYS","AFG","RMC","ABA",
"KSL","BBC","YBR","CCB"]

# Opening each banks URL

base_url1 = 'https://www.marketwatch.com/investing/stock/'
base_url2 = '/financials/balance-sheet?countrycode=au'

urls = []
for i in tickers:
    url =base_url1 + i + base_url2
    urls.append(url)


asset_list = []
liability_list = []
banks = []

# Extracting each balance sheet table as a DataFrame and creating list with dataframes
for url in urls:
    page = requests.get(url)
    soup = BeautifulSoup(page.text, 'html.parser')
    assets = soup.find('table', {'class': 'table table--overflow align--right'})
    liabilities = soup.find('table', {'aria-label': "Financials - Liabilities & Shareholders' Equity data table"})
    
    if assets is not None:
        banks.append(url)
        table_rows = assets.find_all('tr')
        headers = [th.text.strip() for th in table_rows[0].find_all('th')]
        data = [[td.text.strip() for td in tr.find_all('td')] for tr in table_rows[1:]]
        df = pd.DataFrame(data, columns=headers)
        asset_list.append(df)
    else:
        print(f"No asset table found for URL: {url}")
    
    if liabilities is not None:
        table_rows = liabilities.find_all('tr')
        headers = [th.text.strip() for th in table_rows[0].find_all('th')]
        data = [[td.text.strip() for td in tr.find_all('td')] for tr in table_rows[1:]]
        df = pd.DataFrame(data, columns=headers)
        liability_list.append(df)
    else:
        print(f"No liability table found for URL: {url}")
        
        
for i in range(len(asset_list)):
    asset_list[i] = asset_list[i].rename(columns={asset_list[i].columns[0]: banks[i][44:47]})
    first_column_label = asset_list[i].columns[0]
    asset_list[i] = asset_list[i][[first_column_label, '2022']]
    asset_list[i] = asset_list[i].replace(r'\n.*', '', regex=True)
    asset_list[i] = asset_list[i][~asset_list[i]['2022'].str.contains('%')]

for i in range(len(liability_list)):
    liability_list[i] = liability_list[i].rename(columns={liability_list[i].columns[0]: banks[i][44:47]})
    first_column_label = liability_list[i].columns[0]
    liability_list[i] = liability_list[i][[first_column_label, '2022']]
    liability_list[i] = liability_list[i].replace(r'\n.*', '', regex=True)
    liability_list[i] = liability_list[i][~liability_list[i]['2022'].str.contains('%')]


    
    
    
import numpy as np

def convert_string(value):
    if isinstance(value, str):
        value = value.strip()
        if value.endswith('B'):
            return float(value[:-1]) * 10**9
        elif value.endswith('M'):
            return float(value[:-1]) * 10**6
        else:
            return np.nan
        return round(num/100000) * 100000
    else:
        return value

balance_sheets = []

for a, l in zip(asset_list, liability_list):
    combo = pd.concat([a, l], ignore_index=True)
    combo.fillna(0, inplace=True)
    balance_sheets.append(combo)

for i in balance_sheets:
    i.iloc[:, 1] = i.iloc[:, 1].apply(convert_string)
    i.iloc[:, 1] = i.iloc[:, 1].apply(lambda x: round(x, 2))
    
    
    
import pandas as pd

# Create an empty DataFrame for liquidity ratios
liquidity = pd.DataFrame(columns=['Company', 'Liquidity Ratio'])

# Iterate through the balance sheet
for balance_sheet in balance_sheets:
    balance_sheet.fillna(0,inplace =True)
    column_name = balance_sheet.columns[1]
    company_ticker = balance_sheet.columns[0]  # Use the column name as the company ticker
    
    #Retrieving Cash
    cash_mask = balance_sheet.iloc[:, 0] == 'Total Cash & Due from Banks'
    if cash_mask.any():
        total_cash_values = balance_sheet.loc[cash_mask, column_name].iloc[0]
    else:
        total_cash_values = 0
    
    #Retrieving Trading Securities
    trading_mask = balance_sheet.iloc[:, 0] == 'Trading Account Securities'
    if trading_mask.any():
        trading_account_securities_values = balance_sheet.loc[trading_mask, column_name].iloc[0]
    else:
        trading_account_securities_values = 0

    #Retrieving Deposits
    deposit_mask = balance_sheet.iloc[:, 0] == 'Total Deposits'
    if deposit_mask.any():
        total_deposits_values = balance_sheet.loc[deposit_mask, column_name].iloc[0]
    else:
        total_deposits_values = 0
    
    total_cash = total_cash_values
    trading_account_securities = trading_account_securities_values
    total_deposits = total_deposits_values

    try:
        liquidity_ratio = (total_cash + trading_account_securities) / total_deposits
    except ZeroDivisionError:
        liquidity_ratio = "Insufficient Information"
        
    if liquidity_ratio == float('inf') or liquidity_ratio == 0:
        liquidity_ratio = 'Insufficient Information'

    new_row = pd.DataFrame({'Company': [company_ticker], 'Liquidity Ratio': [liquidity_ratio]})

    liquidity = pd.concat([liquidity, new_row], ignore_index=True)


print(liquidity)
