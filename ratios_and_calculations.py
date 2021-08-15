'''
Ratios and financial calculation
Author: Sangram Singh
'''

import pandas as pd
import datetime
import numpy as np
import yfinance as yf
from pathlib import Path
from datetime import datetime


def sharpe_ratio(df, risk_free=0, periodicity=252):
    # convert anuualized risk free rate into appropriate value
    risk_free = (1+risk_free)**(1/periodicity)-1
    excess_return = df.mean() - risk_free
    calculated_sharpe = (excess_return/df.std())*np.sqrt(periodicity)
    return calculated_sharpe

def retrieve_yahoo_data(ticker = 'spy', start_date = '2007-07-01', end_date = '2020-12-31'):
    try:
        yahoo_data = yf.Ticker(ticker)
        print(f"Ticker is {ticker}")
        price_df = yahoo_data.history(start=start_date, end=end_date).Close.pct_change()
        price_df.name = ticker
        if price_df.shape[0] == 0:
            raise Exception("No Prices.")
        return price_df
    except Exception as ex:
        print(f"Sorry, Data not available for '{ticker}': Exception is {ex}")

def target_downside_deviation(df, minimum_acceptable_return = 0, periodicity=252):
    df_diff = df - minimum_acceptable_return
    df_positive_excess_return = np.where(df_diff < 0, df_diff, 0)
    calculated_target_downside_deviation = np.sqrt(np.nanmean(df_positive_excess_return ** 2))
    return calculated_target_downside_deviation

def sortino_ratio(df, risk_free = 0, periodicity = 252, include_risk_free_in_volatility = False):
    risk_free = (1 + risk_free) ** (1/periodicity) - 1
    df_mean = np.nanmean(df) - risk_free
    if include_risk_free_in_volatility == True:
        minimum_acceptable_return = risk_free
    else:
        minimum_acceptable_return = 0
    calculated_target_downside_deviation = target_downside_deviation(df,
                                                                     minimum_acceptable_return = minimum_acceptable_return)
    df_sortino = (df_mean/calculated_target_downside_deviation) * np.sqrt(periodicity)
    return df_sortino

def annualized_return(df, periodicity = 252):
    difference_in_years = len(df)/periodicity
    start_net_asset_value = 1.0
    cumprod_return = np.nancumprod(df + start_net_asset_value)
    end_net_asset_value = cumprod_return[-1]
    annual_return = end_net_asset_value ** (1 / difference_in_years) - 1
    return annual_return

def max_drawdown(df, return_data = False):
    """df - asset return series, e.g. returns based on daily close prices of asset
    return_data - boolean value to determine if drawdown values over the return data time period should be return, instead of max DD"""
    # convert return series to numpy array (in case Pandas series is provided)
    df = np.asarray(df)
    # calculate cumulative returns
    start_NAV = 1
    r = np.nancumprod(df+start_NAV)
    # calculate cumulative max returns (i.e. keep track of peak cumulative return up to that point in time, despite actual cumulative return at that point in time)
    peak_r = np.maximum.accumulate(r)
    # determine drawdowns relative to peak cumulative return achieved up to each point in time
    drawdown = (r - peak_r) / peak_r
    # return drawdown values over time period if return_data is set to True, otherwise return max drawdown which will be a positive number
    if return_data == True:
        out = drawdown
    else:
        out = np.abs(np.nanmin(drawdown))
    return out

def get_max_drawdown(df, return_data = False):
    start_net_asset_value = 1.0
    cumprod_return = np.nancumprod(df + start_net_asset_value)
    peak_return = np.maximum.accumulate(cumprod_return)
    drawdown = (cumprod_return - peak_return) / peak_return
    if return_data == True:
        data = drawdown
    else:
        data = np.abs(np.nanmin(drawdown))
    return data

def return_max_drawdown_ratio(df, risk_free = 0, periodicity = 252):
    """df - asset return series, e.g. returns based on daily close prices of asset
   risk_free - annualized risk free rate (default is assumed to be 0)
   periodicity - number of periods at desired frequency in one year
                e.g. 252 business days in 1 year (default),
                12 months in 1 year,
                52 weeks in 1 year etc."""
    # convert annualized risk free rate into appropriate value for provided frequency of asset return series (df)
    risk_free= (1 + risk_free)**(1 / periodicity) - 1
    # determine annualized return to be used in numerator of return to max drawdown (RMDD) calculation
    annual_return = annualized_return(df, periodicity = periodicity)
    # determine max drawdown to be used in the denominator of RMDD calculation
    max_drawdown = get_max_drawdown(df, return_data = False)
    return (annual_return - risk_free) / abs(max_drawdown)

def average_positive(ret, drop_zero = 1):
    if drop_zero > 0:
        positives = ret > 0
    else:
        positives = ret >= 0
    if positives.any():
        return np.mean(ret[positives])
    else:
        return 0.000000000000000000000000000001

def average_negative(ret):
    negatives = ret < 0
    if negatives.any():
        return np.mean(ret[negatives])
    else:
        return -1*0.000000000000000000000000000001

def win_above_replacement_portfolio(
                    new_asset,
                    replace_port,
                    risk_free_rate = 0,
                    financing_rate = 0,
                    weight_asset = 0.25,
                    weight_replace_port = 1,
                    periodicity = 252):
    """Win Above Replacement Portolio (WARP): Total score to evaluate whether any new investment improves or hurts the return to risk of your total portfolio.
    new_asset = returns of the asset you are thinking of adding to your portfolio
    replace_port = returns of your pre-existing portfolio (e.g. S&P 500 Index, 60/40 Stock-Bond Portfolio)
    risk_free_rate = Tbill rate (annualized)
    financing_rate = portfolio margin/borrowing cost (annualized) to layer new asset on top of prevailing portfolio (e.g. LIBOR + 60bps). No financing rate is reasonable for derivate overlay products.
    weight_asset = % weight you wish to overlay for the new asset on top of the previous portfolio, 25% overlay allocation is standard
    weight_replace_port = % weight of the replacement portfolio, 100% pre-existing portfolio value is standard
    periodicity = the frequency of the data you are sampling, typically 12 for monthly or 252 for trading day count"""
    # convert annualized financing rate into appropriate value for provided periodicity
    # risk_free_rate will be converted appropriately in respective Sortino and RMDD calcs
    financing_rate = (1 + financing_rate)**(1 / periodicity) - 1

    #Calculate Replacement Portfolio Sortino Ratio
    replace_port_sortino = sortino_ratio(replace_port, risk_free = risk_free_rate, periodicity = periodicity)

    #Calculate Replacement Portfolio Return to Max Drawdown
    replace_port_return_max_drawdown = return_max_drawdown_ratio(
                                                    replace_port,
                                                    risk_free = risk_free_rate,
                                                    periodicity = periodicity)

    #Calculate New Portfolio Sortino Ratio
    total_weight = weight_asset + weight_replace_port
    new_port = (new_asset - financing_rate) * (weight_asset/total_weight) + replace_port * (weight_replace_port/total_weight)
    new_port_sortino = sortino_ratio(new_port, risk_free = risk_free_rate, periodicity = periodicity)

    #Calculate New Portfolio Return to Max Drawdown
    new_port_return_max_drawdown = return_max_drawdown_ratio(new_port, risk_free = risk_free_rate, periodicity = periodicity)

    #Final WARP calculation
    WARP = (((new_port_return_max_drawdown / replace_port_return_max_drawdown) * 
              (new_port_sortino / replace_port_sortino)) ** (1/2) - 1) * 100
    
    return WARP

def warp_additive_sortino(new_asset,
                          replace_port,
                          risk_free_rate = 0,
                          financing_rate = 0,
                          weight_asset = 0.25,
                          weight_replace_port = 1,
                          periodicity = 252):
    """Win Above Replacement Portolio (WARP) Sortino +: Isolates new investment effect on total portfolio Sortino Ratio, which is a portion of the holistic CWARP score.
    new_asset = returns of the asset you are thinking of adding to your portfolio
    replace_port = returns of your pre-existing portfolio (e.g. S&P 500 Index, 60/40 Stock-Bond Portfolio)
    risk_free_rate = Tbill rate (annualized)
    financing_rate = portfolio margin/borrowing cost (annualized) to layer new asset on top of prevailing portfolio (e.g. LIBOR + 60bps). No financing rate is reasonable for derivate overlay products.
    weight_asset = % weight you wish to overlay for the new asset on top of the previous portfolio, 25% overlay allocation is standard
    weight_replace_port = % weight of the replacement portfolio, 100% pre-existing portfolio value is standard
    periodicity = the frequency of the data you are sampling, typically 12 for monthly or 252 for trading day count"""
    # convert annualized financing rate into appropriate value for provided periodicity
    # risk_free_rate will be converted appropriately in respective Sortino and RMDD calcs
    financing_rate = (1+financing_rate)**(1/periodicity)-1

    #Calculate Replacement Portfolio Sortino Ratio
    replace_port_sortino = sortino_ratio(replace_port, risk_free = risk_free_rate, periodicity = periodicity)

    #Calculate New Portfolio Sortino Ratio
    total_weight = weight_asset + weight_replace_port
    new_port = (new_asset - financing_rate)*(weight_asset/total_weight) + replace_port * (weight_replace_port/total_weight)
    new_port_sortino = sortino_ratio(new_port, risk_free = risk_free_rate, periodicity = periodicity)

    #Final calculation
    WARP_add_sortino = ((new_port_sortino/replace_port_sortino) - 1)*100

    return WARP_add_sortino

def warp_additive_ret_maxdd(new_asset,
                            replace_port,
                            risk_free_rate = 0,
                            financing_rate = 0,
                            weight_asset = 0.25,
                            weight_replace_port = 1,
                            periodicity = 252):
    """Win Above Replacement Portolio (WARP) Ret to Max DD +: Isolates new investment effect on total portfolio Return to MAXDD, which is a portion of the holistic CWARP score.
    new_asset = returns of the asset you are thinking of adding to your portfolio
    replace_port = returns of your pre-existing portfolio (e.g. S&P 500 Index, 60/40 Stock-Bond Portfolio)
    risk_free_rate = Tbill rate (annualized)
    financing_rate = portfolio margin/borrowing cost (annualized) to layer new asset on top of prevailing portfolio (e.g. LIBOR + 60bps). No financing rate is reasonable for derivate overlay products.
    weight_asset = % weight you wish to overlay for the new asset on top of the previous portfolio, 25% overlay allocation is standard
    weight_replace_port = % weight of the replacement portfolio, 100% pre-existing portfolio value is standard
    periodicity = the frequency of the data you are sampling, typically 12 for monthly or 252 for trading day count"""
    # convert annualized financing rate into appropriate value for provided periodicity
    # risk_free_rate will be converted appropriately in respective Sortino and RMDD calcs
    financing_rate=(1+financing_rate)**(1/periodicity)-1

    #Calculate Replacement Portfolio Return to Max Drawdown
    replace_port_return_max_drawdown = return_max_drawdown_ratio(replace_port,
                                                          risk_free = risk_free_rate,
                                                          periodicity = periodicity)

    #Calculate New Portfolio Return to Max Drawdown
    total_weight = weight_asset + weight_replace_port
    new_port = (new_asset-financing_rate)*(weight_asset/total_weight)+replace_port*(weight_replace_port/total_weight)
    new_port_return_max_drawdown = return_max_drawdown_ratio(new_port, risk_free=risk_free_rate, periodicity=periodicity)

    #Final calculation
    WARP_add_ret_max_drawdown = ((new_port_return_max_drawdown/replace_port_return_max_drawdown)-1)*100

    return WARP_add_ret_max_drawdown

def warp_port_return(new_asset,
                     replace_port,
                     risk_free_rate = 0,
                     financing_rate = 0,
                     weight_asset = 0.25,
                     weight_replace_port = 1,
                     periodicity = 252):
    """Win Above Replacement Portolio CWARP) Portfolio Return: Returns of the aggregate portfolio after a new asset is financed and layered on top of the replacement portfolio.
    new_asset = returns of the asset you are thinking of adding to your portfolio
    replace_port = returns of your pre-existing portfolio (e.g. S&P 500 Index, 60/40 Stock-Bond Portfolio)
    risk_free_rate = Tbill rate (annualized)
    financing_rate = portfolio margin/borrowing cost (annualized) to layer new asset on top of prevailing portfolio (e.g. LIBOR + 60bps). No financing rate is reasonable for derivate overlay products.
    weight_asset = % weight you wish to overlay for the new asset on top of the previous portfolio, 25% overlay allocation is standard
    weight_replace_port = % weight of the replacement portfolio, 100% pre-existing portfolio value is standard
    periodicity = the frequency of the data you are sampling, typically 12 for monthly or 252 for trading day count"""
    # convert annual financing based on periodicity
    financing_rate=((financing_rate+1)**(1/periodicity)-1)

    # compose new portfolio
    total_weight = weight_asset + weight_replace_port
    new_port=(new_asset-financing_rate)*(weight_asset/total_weight)+replace_port*(weight_replace_port/total_weight)

    # calculate annualized return of new portfolio and subtract risk-free rate
    out = annualized_return(new_port, periodicity=periodicity) - risk_free_rate
    return out

def warp_port_risk(new_asset,
                   replace_port,
                   risk_free_rate = 0,
                   financing_rate = 0,
                   weight_asset = 0.25,
                   weight_replace_port = 1,
                   periodicity = 252):
    """Win Above Replacement Portolio (WARP) Portfolio Risk: Volatility of the aggregate portfolio after a new asset is financed and layered on top of the replacement portfolio.
    new_asset = returns of the asset you are thinking of adding to your portfolio
    replace_port = returns of your pre-existing portfolio (e.g. S&P 500 Index, 60/40 Stock-Bond Portfolio)
    risk_free_rate = Tbill rate (annualized)
    financing_rate = portfolio margin/borrowing cost (annualized) to layer new asset on top of prevailing portfolio (e.g. LIBOR + 60bps). No financing rate is reasonable for derivate overlay products.
    weight_asset = % weight you wish to overlay for the new asset on top of the previous portfolio, 25% overlay allocation is standard
    weight_replace_port = % weight of the replacement portfolio, 100% pre-existing portfolio value is standard
    periodicity = the frequency of the data you are sampling, typically 12 for monthly or 252 for trading day count"""
    # convert annual financing and risk free rates based on periodicity
    financing_rate = ((financing_rate+1)**(1/periodicity)-1)
    risk_free_rate = ((risk_free_rate+1)**(1/periodicity)-1)
    # compose new portfolio
    total_weight = weight_asset + weight_replace_port
    new_port = (new_asset - financing_rate)*(weight_asset/total_weight) + replace_port*(weight_replace_port/total_weight)
    # calculated target downside deviation (TDD)
    tdd = target_downside_deviation(new_port, minimum_acceptable_return = 0)*np.sqrt(periodicity)
    return tdd

def warp_new_port_data(new_asset,
                       replace_port,
                       risk_free_rate = 0,
                       financing_rate = 0,
                       weight_asset = 0.25,
                       weight_replace_port = 1,
                       periodicity = 252):
    """Win Above Replacement Portolio (WARP) return stream: Return series after a new asset is financed and layered on top of the replacement portfolio.
    new_asset = returns of the asset you are thinking of adding to your portfolio
    replace_port = returns of your pre-existing portfolio (e.g. S&P 500 Index, 60/40 Stock-Bond Portfolio)
    risk_free_rate = Tbill rate
    financing_rate = portfolio margin/borrowing cost to layer new asset on top of prevailing portfolio (e.g. LIBOR + 60bps). No financing rate is reasonable for derivate overlay products.
    weight_asset = % weight you wish to overlay for the new asset on top of the previous portfolio, 25% overlay allocation is standard
    weight_replace_port = % weight of the replacement portfolio, 100% pre-existing portfolio value is standard
    periodicity = the frequency of the data you are sampling, typically 12 for monthly or 252 for trading day count"""
    # convert annual financing based on periodicity
    financing_rate=((financing_rate + 1)**(1/periodicity) - 1)
    total_weight = weight_asset + weight_replace_port
    new_port = (new_asset - financing_rate) * (weight_asset/total_weight) + replace_port * (weight_replace_port/total_weight)
    return new_port

def calculate_risk_return(ticker, ticker_data, replacement_portfolio, risk_free_rate, financing_rate, weight_asset,
                          weight_replacement_port, data_periodicity):
    risk_ret_df.loc[ticker, 'WARP'] = win_above_replacement_portfolio(
                                                new_asset = ticker_data, 
                                                replace_port = replacement_portfolio,
                                                risk_free_rate = risk_free_rate,
                                                financing_rate = financing_rate,
                                                weight_asset = weight_asset,
                                                weight_replace_port = weight_replacement_port,
                                                periodicity = data_periodicity)
    risk_ret_df.loc[ticker, '+Sortino'] = warp_additive_sortino(new_asset = ticker_data, 
                                                                        replace_port = replacement_portfolio,
                                                                        risk_free_rate = risk_free_rate,
                                                                        financing_rate = financing_rate,
                                                                        weight_asset = weight_asset,
                                                                        weight_replace_port = weight_replacement_port,
                                                                        periodicity = data_periodicity)
    risk_ret_df.loc[ticker, '+Ret_To_MaxDD'] = warp_additive_ret_maxdd(
                                                            new_asset = ticker_data, 
                                                            replace_port = replacement_portfolio,
                                                            risk_free_rate = risk_free_rate,
                                                            financing_rate = financing_rate,
                                                            weight_asset = weight_asset,
                                                            weight_replace_port = weight_replacement_port,
                                                            periodicity = data_periodicity)
    risk_ret_df.loc[ticker, 'Sharpe'] = sharpe_ratio(
                                                    ticker_data,
                                                    risk_free = risk_free_rate,
                                                    periodicity = data_periodicity)
    risk_ret_df.loc[ticker, 'Sortino'] = sortino_ratio(
                                                        ticker_data,
                                                        risk_free = risk_free_rate,
                                                        periodicity = data_periodicity)
    risk_ret_df.loc[ticker, 'Max_DD'] = max_drowdown(ticker_data)

def calculate_new_risk_ret(ticker, ticker_data, replacement_portfolio, risk_free_rate, financing_rate, weight_asset,
                           weight_replacement_port, data_periodicity, new_ports):
    new_risk_ret_df.loc[ticker, 'Return'] = warp_port_return(
                                                        new_asset = ticker_data,
                                                        replace_port = replacement_portfolio,
                                                        risk_free_rate = risk_free_rate,
                                                        financing_rate = financing_rate,
                                                        weight_asset = weight_asset,
                                                        weight_replace_port = weight_replacement_port,
                                                        periodicity = data_periodicity)
    new_risk_ret_df.loc[ticker, 'Vol'] = warp_port_risk(
                                                    new_asset = ticker_data,
                                                    replace_port = replacement_portfolio,
                                                    risk_free_rate = risk_free_rate,
                                                    financing_rate = financing_rate,
                                                    weight_asset = weight_asset,
                                                    weight_replace_port = weight_replacement_port,
                                                    periodicity = data_periodicity)
    cnpd = warp_new_port_data(new_asset = ticker_data,
                              replace_port = replacement_portfolio,
                              risk_free_rate = risk_free_rate,
                              financing_rate = financing_rate,
                              weight_asset = weight_asset,
                              weight_replace_port = weight_replacement_port,
                              periodicity = data_periodicity)
    new_ports[ticker] = cnpd
    new_risk_ret_df.loc[ticker, 'Sharpe'] = sharpe_ratio(cnpd.copy(),
                                                         risk_free = risk_free_rate,
                                                         periodicity = data_periodicity)
    new_risk_ret_df.loc[ticker, 'Sortino'] = sortino_ratio(
                                                        cnpd.copy(),
                                                        risk_free = risk_free_rate,
                                                        periodicity = data_periodicity)
    new_risk_ret_df.loc[ticker, 'Max_DD'] = max_dd(cnpd.copy())
    new_risk_ret_df.loc[ticker, 'Ret_To_MaxDD'] = return_max_drawdown_ratio(
                                                                            cnpd.copy(),
                                                                            risk_free = risk_free_rate,
                                                                            periodicity = data_periodicity)
    new_risk_ret_df.loc[ticker, f'WARP_{round(100*weight_asset)}%_asset'] = risk_ret_df.loc[ticker, 'WARP']


def retrieve_ticker_data_and_update_risk_return_data_frame(ticker, yahoo,
                                                           csv_file, risk_ret_df,
                                                           replacement_portfolio,
                                                           risk_free_rate, financing_rate, weight_asset, weight_replacement_port,
                                                           data_periodicity = 252):
    if yahoo == True:
        ticker_data = retrieve_yahoo_data(ticker)
        risk_ret_df.loc[ticker, 'Start Date'] = min(ticker_data.index).date()
        risk_ret_df.loc[ticker, 'End Date'] = max(ticker_data.index).date()
    else:
        ticker_data = pd.read_csv(Path(csv_file), index_col='ReturnDate', skiprows=2)
        ticker_data = ticker_data[['PercentReturn']]
        risk_ret_df.loc[ticker, 'Start Date'] = datetime.strptime(min(ticker_data.index), '%b %Y').date()
        risk_ret_df.loc[ticker, 'End Date'] = datetime.strptime(max(ticker_data.index), '%b %Y').date()
        ticker_data = ticker_data[['PercentReturn']]
        ticker_data.reset_index(drop=True, inplace=True)
        ticker_data = ticker_data[:].values
        
    calculate_risk_return(ticker, ticker_data, replacement_portfolio, risk_free_rate, financing_rate, weight_asset,
                          weight_replacement_port, data_periodicity)

def retrieve_ticker_data_and_update_data_frames(ticker, yahoo,
                                               csv_file, risk_ret_df, ticker_data_dict, new_risk_ret_df, new_ports,
                                               replacement_portfolio,
                                               risk_free_rate, financing_rate, weight_asset, weight_replacement_port,
                                               data_periodicity = 252):
    if yahoo == True:
        ticker_data = retrieve_yahoo_data(ticker)
        ticker_data_dict[ticker] = ticker_data
        risk_ret_df.loc[ticker, 'Start Date'] = min(ticker_data.index).date()
        risk_ret_df.loc[ticker, 'End Date'] = max(ticker_data.index).date()
    else:
        ticker_data = pd.read_csv(Path(csv_file), index_col='ReturnDate', skiprows=2)
        ticker_data = ticker_data[['PercentReturn']]
        ticker_data_dict[ticker] = ticker_data
        risk_ret_df.loc[ticker, 'Start Date'] = datetime.strptime(min(ticker_data.index), '%b %Y').date()
        risk_ret_df.loc[ticker, 'End Date'] = datetime.strptime(max(ticker_data.index), '%b %Y').date()
        ticker_data = ticker_data[['PercentReturn']]
        ticker_data.reset_index(drop=True, inplace=True)
        ticker_data = ticker_data[:].values
        
    calculate_risk_return(ticker, ticker_data, replacement_portfolio, risk_free_rate, financing_rate, weight_asset,
                          weight_replacement_port, data_periodicity)
    calculate_new_risk_ret(ticker, ticker_data, replacement_portfolio, risk_free_rate, financing_rate, weight_asset,
                           weight_replacement_port, data_periodicity, new_ports)

def compare_stocks_with_60_40_portfolio():
    ticker_list = ["qqq", "lqd", "hyg", "tlt", "ief", "shy", "gld", "slv", "efa", "eem", "iyr", "xle", "xlk", "xlf", 'GC=F', 'RPAR']
    risk_free_rate = 0.0
    weight_asset = 0.25
    financing_rate = 0.00
    weight_replacement_port = 1.00

    weight_replacement_portfolio_stock = 0.6
    weight_replacement_portfolio_bond  = 0.4
    ticker_replacement_portfolio_stock = 'spy'
    ticker_replacement_portfolio_bond  = 'ief'
    start_date = '2008-01-01'
    end_date = '2020-12-31'
    new_ports = {}

    df_stock = retrieve_yahoo_data(ticker_replacement_portfolio_stock, start_date, end_date)
    df_bond = retrieve_yahoo_data(ticker_replacement_portfolio_bond, start_date, end_date)
    replacement_portfolio = ((weight_replacement_portfolio_stock * df_stock) + 
                        (weight_replacement_portfolio_bond * df_bond))

    risk_ret_df = pd.DataFrame(
                index = ticker_list,
                columns = ['Start Date','End Date','WARP','+Sortino','+Ret_To_MaxDD','Sharpe','Sortino','Max_DD'])
    new_risk_ret_df = pd.DataFrame(
                    index = ticker_list,
                    columns = ['Return','Vol','Sharpe','Sortino','Max_DD','Ret_To_MaxDD',f'WARP_{round(100*weight_asset)}%_asset'])
    ticker_data_dict = {}
    csv_file = ""

    for ticker in ticker_list:
        retrieve_ticker_data_and_update_data_frames(ticker, True, csv_file, risk_ret_df, ticker_data_dict, new_risk_ret_df, new_ports,
                                               replacement_portfolio,
                                               risk_free_rate, financing_rate, weight_asset, weight_replacement_port,
                                               252)
    risk_ret_df.to_csv("risk_ret.csv")
    new_risk_ret_df.to_csv("new_risk_ret.csv")
    new_ports_df = pd.DataFrame(new_ports)
    new_ports_df.to_csv("new_ports.csv")
    ticker_data_df = pd.DataFrame(ticker_data_dict)
    ticker_data_df.to_csv("ticker_data.csv")

def calculate_cumulative_product(ticker_list, new_ports, replacement_portfolio, replacement_portfolio_name):
    cumulative_returns = {}
    for ticker in ticker_list:
        cumulative_returns[ticker] = (1 + new_ports[ticker]).cumprod()
    cumulative_returns[replacement_portfolio_name] = (1 + replacement_portfolio).cumprod()
    
    cumulative_returns_df = pd.DataFrame(cumulative_returns)
    cumulative_returns_df.to_csv(f"cumulative_returns_{replacement_portfolio_name}.csv")
    return cumulative_returns_df