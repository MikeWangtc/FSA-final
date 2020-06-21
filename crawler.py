from bs4 import BeautifulSoup
import requests
import pandas as pd
import numpy as np
import os

# market value of equity and long-term liability
if False:
    url = 'https://www.macrotrends.net/stocks/charts/RDS.B/royal-dutch-shell/debt-equity-ratio'
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'html.parser')
    output_file = os.path.join('data', 'debt_equity_market.pickle')

    debt_equity_table = soup.find('table', {'class': 'table'})
    columns = [col.get_text() for col in debt_equity_table.findAll('thead')[1].findAll('th')[1:]] # get rid of date and view it as index
    data_tag = debt_equity_table.findAll('tr')
    data = []
    index = []
    for tag in data_tag:
        row_data = tag.findAll('td')
        tmp = np.array([col.get_text() for col in row_data[1:]])
        if len(tmp) != 0 and len(tmp[0]) != 0  and len(tmp[1]) != 0:
            index.append(row_data[0].get_text())
            tmp[0] = float(tmp[0][1:][:-1]) * 1000
            tmp[1] = float(tmp[1][1:][:-1]) * 1000
            tmp[2] = float(tmp[2])
            data.append(tmp)

    save_df = pd.DataFrame(np.array(data), columns=columns, index=index).iloc[::-1]
    print(f"Save debt/equity ratio to {output_file}")
    save_df.to_pickle(output_file)

# 10y average annual treasury bill
if True:
    url = 'https://www.treasury.gov/resource-center/data-chart-center/interest-rates/pages/TextView.aspx?data=yieldAll'
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'html.parser')
    output_file = os.path.join('data', 'risk_free_rate.pickle')

    risk_free_table = soup.find('table').find('tbody')
    columns = [risk_free_table.find('tr').findAll('th', {'scope': 'col'})[10].get_text()]
    data_tag = risk_free_table.findAll('tr')[1:]
    data = []
    index = []
    for tag in data_tag:
        row_data = tag.findAll('td')[0, 10] # year, 10 year rate
        index.append(row_data[0].get_text())
        data.append(float(row_data[1].get_text()) if row_data[1].get_text() != 'N/A' else np.nan)

    print(data)
    save_df = pd.DataFrame(np.array(data), columns=columns, index=index).iloc[::-1]
    print(f"Save risk-free rate to {output_file}")
    save_df.to_pickle(output_file)

# Brent oil annual price
if False:
    url = 'https://www.macrotrends.net/2480/brent-crude-oil-prices-10-year-daily-chart'
    resp = requests.get(url)
    soup = BeautifulSoup(resp.text, 'html.parser')
    output_file = os.path.join('data', 'oil_price.pickle')

    oil_table = soup.find('table', {'class': 'table'})
    columns = [oil_table.findAll('thead')[1].findAll('th')[1].get_text()]
    data_tag = oil_table.find('tbody').findAll('tr')
    data = []
    index = []
    for tag in data_tag:
        row_data = tag.findAll('td')[:2] # year, Average Closing Price
        index.append(row_data[0].get_text())
        data.append(float(row_data[1].get_text()[1:])) # remove %
    
    save_df = pd.DataFrame(np.array(data), columns=columns, index=index).iloc[::-1]
    print(f"Save risk-free rate to {output_file}")
    save_df.to_pickle(output_file)