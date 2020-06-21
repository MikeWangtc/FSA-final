import pandas as pd
import pyexcel as px
import os
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from matplotlib.ticker import PercentFormatter
from matplotlib import dates

from utils import load_statement, load_price, \
                  print_stat_account, plot_time_series, \
                  get_beta, get_ones


def cal_financial_data(statement, data_type):
    predefine_type = ['working_capital', 'tax_rate', 'ebit', 'capital_employed', \
                      'capital_expenditure', 'depreciation', 'debt_ratio', 'gross_margin', \
                      'gross_profit', 'revenue', 'operating_margin', 'long_term_debt', \
                      'pretax_income', 'interest', 'eps', \
                      'operating_cashflow', 'investing_cashflow', 'financing_cashflow'
                    ]

    if not data_type in predefine_type:
        print(f"Input type should be in {predefine_type}")
        return None
    

    # I/S
    if data_type == 'revenue': return statement.loc[:, 'Sales (Net)']
    if data_type == 'gross_profit': return statement.loc[:, 'Gross Profit']
    if data_type == 'depreciation': return statement.loc[:, 'Depreciation, Depletion, & Amortiz']
    if data_type == 'interest': return statement.loc[:, 'Interest Expense']
    if data_type == 'pretax_income': return statement.loc[:, 'Pretax Income']
    if data_type == 'eps': return statement.loc[:, 'EPS - Primary, Excluding EI&DO']

    if data_type == 'ebit': return statement.loc[:, 'Net Income (Loss)'] + statement.loc[:, 'Income Taxes - Total'] + statement.loc[:, 'Interest Expense']

    # B/S
    if data_type == 'capital_employed': return statement.loc[:, 'TOTAL ASSETS'] # - statement.loc[:, 'Total Current Liabilities']
    if data_type == 'long_term_debt': return statement.loc[:, 'Long Term Debt']

    # ratio
    if data_type == 'gross_margin': return cal_financial_data(statement, 'gross_profit') / cal_financial_data(statement, 'revenue')
    if data_type == 'operating_margin': return cal_financial_data(statement, 'ebit') / statement.loc[:, 'Sales (Net)']
    if data_type == 'debt_ratio': return cal_financial_data(statement, 'long_term_debt') / (cal_financial_data(statement, 'long_term_debt') + statement.loc[: ,"Shareholder's Equity"])

    # Cashflow
    if data_type == 'operating_cashflow': return statement.loc[:, 'Operating Actiities - Net Cash Flow']
    if data_type == 'investing_cashflow': return statement.loc[:, 'Investing Activites - Net Cash Flow']
    if data_type == 'financing_cashflow': return statement.loc[:, 'Financing Activities - Net Cash Flow']
    if data_type == 'capital_expenditure': return statement.loc[:, 'Capital Expenditures']

    # other
    if data_type == 'tax_rate': return statement.loc[:, 'Income Taxes - Total'] / cal_financial_data(statement, 'pretax_income')
    if data_type == 'working_capital': return statement.loc[:, 'Current Assets - Total'] - statement.loc[:, 'Total Current Liabilities']


def estimate_fcff():
    columns = ['Revenue', 'Expected Growth', 'Operating Margin', 'EBIT', 'Tax Rate', 'EBIT(1-t)', 'Reinvestment Rate', 'Expected Growth in EBIT', 'ROC']
    df = pd.DataFrame(np.full((7, len(columns)), np.nan), columns=columns) # 6 = 1 (base) + 2 (virus affected)+ 3 (recovery) + 1 (steady growth)
    
    # expected_growth_revenue = []
    # revenue = [344877, ]

    return estimated_fcff


# directory
data_dir = 'data'
price_dir = os.path.join(data_dir, 'price')
statement_dir = os.path.join(data_dir, 'statement')
tax_dir = os.path.join(data_dir, 'tax')

# pickle data
debt_equity_market_path = os.path.join('data', 'debt_equity_market.pickle')
risk_free_rate_path = os.path.join('data', 'risk_free_rate.pickle')
price_market_path = os.path.join(price_dir,'dow-jones-industrial-average-last-10-years.pickle')
price_rdsb_path = os.path.join(price_dir, 'RDS-B.pickle')
price_oil_path = os.path.join('data', 'oil_price.pickle')

# readin data
statement_dic = load_statement(statement_dir)
debt_equity_market = pd.read_pickle(debt_equity_market_path).astype(np.float64)
risk_free_rate = pd.read_pickle(risk_free_rate_path).astype(np.float64)
price_market = pd.read_pickle(price_market_path).astype(np.float64)[-1800:]
price_rdsb = pd.read_pickle(price_rdsb_path).astype(np.float64)[-1800:]
price_oil = pd.read_pickle(price_oil_path).astype(np.float64)

# not related to individual company
return_market = price_market.pct_change()
plot_time_series(price_oil, 'Brent oil price', img_save=os.path.join('image', 'oil_price'))
plot_time_series(return_market, 'Market Return', img_save=os.path.join('image', 'market_return'))
plot_time_series(price_market, 'Dow Jone Index price', marker=None, img_save=os.path.join(image_dir, 'dow_jone_index'))
plot_time_series(price_rdsb, 'RDS-B', marker=None, img_save=os.path.join(image_dir, 'RDS-B'))
get_beta(benchmark=price_market, stock=price_rdsb)


for ticker, statement in statement_dic.items():
    image_dir = os.path.join('image', ticker)
    os.makedirs(image_dir, exist_ok=True)

    # Show accounts in statement
    # print_stat_account(statement['income_statement'])
    # print_stat_account(statement['financial_position'])
    # print_stat_account(statement['cashflow_statement'])


    # B/S
    long_term_debt = cal_financial_data(statement['financial_position'], 'long_term_debt')

    # I/S
    revenue = cal_financial_data(statement['income_statement'], 'revenue')
    gross_profit = cal_financial_data(statement['income_statement'], 'gross_profit')
    depreciation = cal_financial_data(statement['income_statement'], 'depreciation')
    interest = cal_financial_data(statement['income_statement'], 'interest')
    pretax_income = cal_financial_data(statement['income_statement'], 'pretax_income')
    eps = cal_financial_data(statement['income_statement'], 'eps')

    # calculate fcff
    ebit = cal_financial_data(statement['income_statement'], 'ebit')
    tax_rate = cal_financial_data(statement['income_statement'], 'tax_rate')
    nopat = ebit * (1-tax_rate)
    capital_expenditure = cal_financial_data(statement['cashflow_statement'], 'capital_expenditure')
    working_capital = cal_financial_data(statement['financial_position'], 'working_capital')
    working_capital_diff = working_capital.diff()

    # equation
    return_on_capital = nopat / cal_financial_data(statement['financial_position'], 'capital_employed').shift(periods=1)
    reinvestment_rate = (capital_expenditure + working_capital_diff) / nopat
    ebit_growth = ebit.pct_change()

    # fcff
    fcff = nopat * (1 - reinvestment_rate)

    # WACC
    debt_ratio = cal_financial_data(debt_equity_market, 'debt_ratio')
    cost_debt_post_tax = interest / long_term_debt.shift(periods=1) * (1 - tax_rate)

    # cashflow
    operating_cashflow = cal_financial_data(statement['cashflow_statement'], 'operating_cashflow')
    investing_cashflow = cal_financial_data(statement['cashflow_statement'], 'investing_cashflow')
    financing_cashflow = cal_financial_data(statement['cashflow_statement'], 'financing_cashflow')
    
    # ratio
    gross_margin = cal_financial_data(statement['income_statement'], 'gross_margin')
    operating_margin = cal_financial_data(statement['income_statement'], 'operating_margin')
    working_capital_rate = working_capital / revenue


    plot_time_series(working_capital, 'working_capital', img_save=os.path.join(image_dir, 'working_capital'))
    plot_time_series(working_capital_rate, 'Working Capital to Revenue', unit='%', img_save=os.path.join(image_dir, 'working_capital_revenue'))
    plot_time_series(return_on_capital, 'ROC', unit='%', img_save=os.path.join(image_dir, 'roc'))
    plot_time_series([reinvestment_rate.clip(0, 10), get_ones(reinvestment_rate.clip(0, 10))], 'reinvestment Rate', unit='%', img_save=os.path.join(image_dir, 'reinvestment_rate'))
    plot_time_series(working_capital_diff, 'Delta Working Capital', img_save=os.path.join(image_dir, 'working_capital_diff'))
    plot_time_series(nopat, 'EBIT(1-t)', img_save=os.path.join(image_dir, 'nopat'))
    plot_time_series(ebit_growth, 'EBIT growth rate', unit='%', img_save=os.path.join(image_dir, 'ebit_growth'))
    plot_time_series(ebit, 'EBIT', img_save=os.path.join(image_dir, 'EBIT'))
    plot_time_series(operating_margin, 'Operating Margin',unit='%', img_save=os.path.join(image_dir, 'operating_margin'))
    plot_time_series(tax_rate, 'Tax Rate', unit='%', img_save=os.path.join(image_dir, 'tax_rate'))
    plot_time_series(pretax_income, 'Pretax Income', img_save=os.path.join(image_dir, 'pretax_income'))
    plot_time_series(reinvestment_rate * return_on_capital, 'RR * ROC', unit='%', img_save=os.path.join(image_dir, 'rr_roc'))
    plot_time_series(debt_ratio, 'debt_ratio', unit='%', img_save=os.path.join(image_dir, 'debt_ratio'))
    plot_time_series(risk_free_rate, 'Average annual rate of 10y teasury bill', unit='%', img_save=os.path.join(image_dir, 'risk_free_rate'))
    
    plot_time_series(capital_expenditure, 'capital_expenditure', img_save=os.path.join(image_dir, 'capital_expenditure'))
    plot_time_series(gross_margin, 'Gross Margin', unit='%', img_save=os.path.join(image_dir, 'gross_margin'))
    plot_time_series(gross_profit, 'Gross profit', img_save=os.path.join(image_dir, 'gross_profit'))
    plot_time_series(revenue, 'Revenue', img_save=os.path.join(image_dir, 'revenue'))
    plot_time_series(long_term_debt, 'Long Term Debt', img_save = os.path.join(image_dir, 'long_term_debt'))
    plot_time_series(interest, 'Interest Expense', img_save = os.path.join(image_dir, 'interest_expense'))
    plot_time_series(cost_debt_post_tax, 'Cost of Debt (post-tax)', unit='%', img_save=os.path.join(image_dir, 'cost_of_debt_post_tax'))
    get_beta(benchmark=price_oil.loc['1998':'2019'], stock=operating_margin['1998':'2019'])

    plot_time_series(fcff, 'FCFF', img_save=os.path.join(image_dir, 'fcff'))
    plot_time_series(eps, 'EPS', img_save=os.path.join(image_dir, 'eps'))
    plot_time_series(working_capital_diff + capital_expenditure, 'W + C', img_save=os.path.join(image_dir, 'working_cap_exp'))
    plot_time_series(depreciation, 'Depreciation', img_save=os.path.join(image_dir, 'depreciation'))

    plot_time_series([nopat, depreciation], 'Depreciation compares to Nopat', img_save=os.path.join(image_dir, 'nopat_2_depreciation'))
    plot_time_series([(depreciation / nopat).clip(0, 10), get_ones(depreciation)], 'Ratio of depreciation to nopat', unit='%', img_save=os.path.join(image_dir, 'nopat_2_depreciation_ratio'))