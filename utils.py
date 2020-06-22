import pandas as pd
import pyexcel as px
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.ticker import PercentFormatter
from matplotlib import dates
from scipy import stats

def preprocess(df):
    """
    Transpose dataframe, rename both index and columns, remove NAN and convert from string to float

    - original:
                     1990 1991 ...
        account1
        account2
        ...
    - preprocessed
                account1 account2 ...
        1990
        1991
        ...
    
    Argument: 
        df: dataframe of statments
    Return:
        rtn: preprocessed dataframe
    """
    rtn = df.dropna(axis='columns', how='all')
    rtn = rtn.T
    new_col = rtn.iloc[0 ,1:]
    new_idx = rtn.iloc[1:, 0].rename('Year')
    rtn = rtn.iloc[1:, 1:]

    rtn.columns = new_col
    rtn.index = new_idx

    rtn.drop(columns=['(FYR Ending):'], inplace=True)
    rtn = rtn.astype(np.float64).loc['1983':, :]
    return rtn

def load_statement(s_dir):
    statement_dic = {}

    for i, xls in enumerate(os.listdir(s_dir)):
        print(f"Load financial statement of {xls} ...")

        company_data = {}
        df = pd.read_html(os.path.join(s_dir, xls))[0]
        company_data['firm_name'] = df.iloc[0, 2]
        company_data['ticker'] = df.iloc[1, 2]
        company_data['financial_position'] = preprocess(df.iloc[8:62, :])
        company_data['income_statement'] = preprocess(df.iloc[65:105, :])
        company_data['cashflow_statement'] = preprocess(df.iloc[128:174, :])
        company_data['addition_schedule'] = preprocess(df.iloc[178:238, :])
        company_data['addition_data'] = preprocess(df.iloc[241:295, :])

        statement_dic[company_data['ticker']] = company_data
    
    return statement_dic

def load_price(p_dir):
    price_dic = {}

    for ticker in os.listdir(p_dir):
        df = pd.read_csv(os.path.join(p_dir, ticker))
        df.astype(np.float64)
        price_dic[ticker] = df
    
    return price_dic

def print_stat_account(statement):
    """
    Print account in the statement
    """
    for account in statement.columns:
        print(account) if not account is np.nan else print('')

def plot_time_series(series, title, unit='unit', img_save=None, marker='o'):
    """
    Plot time series data
    """
    series = [series] if not type(series) is list else series
    
    fig, ax = plt.subplots(figsize=(series[0].shape[0]*0.4, 5))
    ax.set_title(title)
    ax.set_xlabel('Year')

    # set axis formatter
    if unit == 'unit':
        ax.set_ylabel('Million Dollar')
        ax.get_yaxis().set_major_formatter(FuncFormatter(lambda x, p: format(int(x), ',')))
    elif unit == '%':
        ax.set_ylabel('Percentage (%)')
        ax.get_yaxis().set_major_formatter(FuncFormatter(lambda x, p: f"{x*100:.0f}%"))
    ax.get_xaxis().set_major_formatter(dates.DateFormatter('%Y'))

    # plot time series data
    for s in series:
        s.plot() if is_reference(s) else s.plot(marker=marker)
        
        if len(series) == 1:
            plt.figtext(0.95, 0.4, s.describe().to_string()) 


    print(f"Save image to {img_save} ...")
    plt.show() if img_save is None else plt.savefig(img_save, bbox_inches='tight')
    plt.close('all')

def price_to_pickle(price_dir):
    files = os.listdir(price_dir)

    for file in files:
        path = os.path.join(price_dir, file)
        outfile = os.path.join(price_dir, f"{file[:-4]}.pickle")

        if file[-3:] != 'csv':
            continue

        raw_df = pd.read_csv(path)

        if file == 'dow-jones-industrial-average-last-10-years.csv':
            df = pd.DataFrame(raw_df.loc[:, 'value'].tolist(), columns=['Price'], index=raw_df.loc[:, 'date'].tolist())
        else:
            df = pd.DataFrame(raw_df.loc[:, 'Close'].tolist(), columns=['Price'], index=raw_df.loc[:, 'Date'].tolist())
        
        print(f"Save to {outfile} ...")
        df.to_pickle(outfile)

def get_beta(benchmark, stock):
    """
    Apply regression on benchmark and stock
    """
    benchmark_rtn = np.array(benchmark.pct_change()[1:].values).squeeze()
    stock_rtn = np.array(stock.pct_change()[1:].values).squeeze()
    
    beta, alpha = stats.linregress(benchmark_rtn, stock_rtn)[0:2]

    print(f"The stock has beta {beta:.4f}")

def get_ones(series):
    """
    Served as the reference (100 percent) for ratio data 
    """
    return pd.Series(np.ones(len(series)), index=series.index)

def get_mean(series):
    """
    Served as comparison to the whole data
    """
    # print(series.mean(), type(series.mean()))
    mean = np.empty(series.shape)
    mean.fill(series.mean())

    return pd.Series(mean, index=series.index)

def is_reference(series):
    ref = series.iloc[0]
    cnt = 0
    for num in series:
        if num == ref:
            cnt += 1
    return cnt == len(series)

if __name__ == "__main__":

    data_dir = 'data'
    image_dir = 'image'
    price_dir = os.path.join(data_dir, 'price')
    statement_dir = os.path.join(data_dir, 'statement')
    tax_dir = os.path.join(data_dir, 'tax')

    os.makedirs(image_dir, exist_ok=True)
    price_to_pickle(price_dir)

