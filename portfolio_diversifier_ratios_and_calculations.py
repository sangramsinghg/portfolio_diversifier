'''
Ratios and financial calculations
Author: Sangram Singh
'''

import pandas as pd
import datetime
import numpy as np
import yfinance as yf
from pathlib import Path
from datetime import datetime
import hvplot
import hvplot.pandas


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

def retrieve_yahoo_data_close(ticker = 'spy', start_date = '2007-07-01', end_date = '2020-12-31'):
    try:
        yahoo_data = yf.Ticker(ticker)
        print(f"Ticker is {ticker}")
        price_df = yahoo_data.history(start=start_date, end=end_date).Close
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

def maximum_drawdown(df, return_data = False):
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

def get_maximum_drawdown(df, return_data = False):
    start_net_asset_value = 1.0
    cumprod_return = np.nancumprod(df + start_net_asset_value)
    peak_return = np.maximum.accumulate(cumprod_return)
    drawdown = (cumprod_return - peak_return) / peak_return
    if return_data == True:
        data = drawdown
    else:
        data = np.abs(np.nanmin(drawdown))
    return data

def return_maximum_drawdown_ratio(df, risk_free = 0, periodicity = 252):
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
    maximum_drawdown = get_maximum_drawdown(df, return_data = False)
    return (annual_return - risk_free) / abs(maximum_drawdown)

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

def win_above_base_portfolio(
                    new_asset,
                    base_portfolio,
                    risk_free_rate = 0,
                    financing_rate = 0,
                    weight_asset = 0.20,
                    weight_base_portfolio = 0.80,
                    periodicity = 252):
    """Win Above Base Portolio (WABP): Total score to evaluate whether any new investment improves or hurts the return to risk of your total portfolio.
    new_asset = returns of the asset you are thinking of adding to your portfolio
    base_portfolio = returns of your pre-existing portfolio (e.g. S&P 500 Index, 60/40 Stock-Bond Portfolio)
    risk_free_rate = Tbill rate (annualized)
    financing_rate = portfolio margin/borrowing cost (annualized) to layer new asset on top of prevailing portfolio (e.g. LIBOR + 60bps). No financing rate is reasonable for derivate overlay products.
    weight_asset = % weight you wish to overlay for the new asset on top of the previous portfolio, 25% overlay allocation is standard
    weight_base_portfolio = % weight of the base portfolio, 100% pre-existing portfolio value is standard
    periodicity = the frequency of the data you are sampling, typically 12 for monthly or 252 for trading day count"""
    # convert annualized financing rate into appropriate value for provided periodicity
    # risk_free_rate will be converted appropriately in respective Sortino and RMDD calcs
    financing_rate = (1 + financing_rate)**(1 / periodicity) - 1

    #Calculate Base Portfolio Sortino Ratio
    base_portfolio_sortino = sortino_ratio(base_portfolio, risk_free = risk_free_rate, periodicity = periodicity)

    #Calculate Base Portfolio Return to Max Drawdown
    base_portfolio_return_maximum_drawdown = return_maximum_drawdown_ratio(
                                                    base_portfolio,
                                                    risk_free = risk_free_rate,
                                                    periodicity = periodicity)

    #Calculate New Portfolio Sortino Ratio
    new_portfolio = (new_asset - financing_rate) * (weight_asset) + base_portfolio * (weight_base_portfolio)
    new_portfolio_sortino = sortino_ratio(new_portfolio, risk_free = risk_free_rate, periodicity = periodicity)

    #Calculate New Portfolio Return to Max Drawdown
    new_portfolio_return_maximum_drawdown = return_maximum_drawdown_ratio(new_portfolio, risk_free = risk_free_rate, periodicity = periodicity)

    #Final WABP calculation
    wabp = (((new_portfolio_return_maximum_drawdown / base_portfolio_return_maximum_drawdown) * 
              (new_portfolio_sortino / base_portfolio_sortino)) ** (1/2) - 1) * 100
    
    return wabp

def wabp_additive_sortino(new_asset,
                          base_portfolio,
                          risk_free_rate = 0,
                          financing_rate = 0,
                          weight_asset = 0.20,
                          weight_base_portfolio = 0.80,
                          periodicity = 252):
    """Win Above Base Portolio (WABP) Sortino +: Isolates new investment effect on total portfolio Sortino Ratio, which is a portion of the holistic WABP score.
    new_asset = returns of the asset you are thinking of adding to your portfolio
    base_portfolio = returns of your pre-existing portfolio (e.g. S&P 500 Index, 60/40 Stock-Bond Portfolio)
    risk_free_rate = Tbill rate (annualized)
    financing_rate = portfolio margin/borrowing cost (annualized) to layer new asset on top of prevailing portfolio (e.g. LIBOR + 60bps). No financing rate is reasonable for derivate overlay products.
    weight_asset = % weight you wish to overlay for the new asset on top of the previous portfolio, 25% overlay allocation is standard (translates to 20% in new portfolio)
    weight_base_portfolio = % weight of the base portfolio, 100% pre-existing portfolio value is standard (translates to 80% mixed with the 20% of asset)
    periodicity = the frequency of the data you are sampling, typically 12 for monthly or 252 for trading day count"""
    # convert annualized financing rate into appropriate value for provided periodicity
    # risk_free_rate will be converted appropriately in respective Sortino and RMDD calcs
    financing_rate = (1+financing_rate)**(1/periodicity)-1

    #Calculate Replacement Portfolio Sortino Ratio
    base_portfolio_sortino = sortino_ratio(base_portfolio, risk_free = risk_free_rate, periodicity = periodicity)

    #Calculate New Portfolio Sortino Ratio
    new_portfolio = (new_asset - financing_rate)*(weight_asset) + base_portfolio * (weight_base_portfolio)
    new_portfolio_sortino = sortino_ratio(new_portfolio, risk_free = risk_free_rate, periodicity = periodicity)

    #Final calculation
    wabp_additive_sortino_number = ((new_portfolio_sortino/base_portfolio_sortino) - 1) * 100

    return wabp_additive_sortino_number

def wabp_additive_return_maximum_drawdown(
                            new_asset,
                            base_portfolio,
                            risk_free_rate = 0,
                            financing_rate = 0,
                            weight_asset = 0.20,
                            weight_base_portfolio = 0.80,
                            periodicity = 252):
    """Win Above Base Portolio (WABP) Ret to Max DD +: Isolates new investment effect on total portfolio Return to MAXDD, which is a portion of the holistic WABP score.
    new_asset = returns of the asset you are thinking of adding to your portfolio
    base_portfolio = returns of your pre-existing portfolio (e.g. S&P 500 Index, 60/40 Stock-Bond Portfolio)
    risk_free_rate = Tbill rate (annualized)
    financing_rate = portfolio margin/borrowing cost (annualized) to layer new asset on top of prevailing portfolio (e.g. LIBOR + 60bps). No financing rate is reasonable for derivate overlay products.
    weight_asset = % weight you wish to overlay for the new asset on top of the previous portfolio, 25% overlay allocation is standard
    weight_base_portfolio = % weight of the replacement portfolio, 100% pre-existing portfolio value is standard
    periodicity = the frequency of the data you are sampling, typically 12 for monthly or 252 for trading day count"""
    # convert annualized financing rate into appropriate value for provided periodicity
    # risk_free_rate will be converted appropriately in respective Sortino and RMDD calcs
    financing_rate = (1 + financing_rate)**(1/periodicity)-1

    #Calculate Replacement Portfolio Return to Max Drawdown
    base_portfolio_return_maximum_drawdown = return_maximum_drawdown_ratio(
                                                                base_portfolio,
                                                                risk_free = risk_free_rate,
                                                                periodicity = periodicity)

    #Calculate New Portfolio Return to Max Drawdown
    new_portfolio = (new_asset-financing_rate)*(weight_asset) + base_portfolio * (weight_base_portfolio)
    new_portfolio_return_maximum_drawdown = return_maximum_drawdown_ratio(new_portfolio, risk_free=risk_free_rate, periodicity=periodicity)

    #Final calculation
    wabp_additive_return_maximum_drawdown_number = ((new_portfolio_return_maximum_drawdown/base_portfolio_return_maximum_drawdown)-1)*100

    return wabp_additive_return_maximum_drawdown_number

def wabp_portfolio_return(new_asset, 
                     base_portfolio,
                     risk_free_rate = 0,
                     financing_rate = 0,
                     weight_asset = 0.20,
                     weight_base_portfolio = 0.80,
                     periodicity = 252):
    """Win Above Base Portolio (WABP) Portfolio Return: Returns of the aggregate portfolio after a new asset is financed and layered on top of the replacement portfolio.
    new_asset = returns of the asset you are thinking of adding to your portfolio
    base_portfolio = returns of your pre-existing portfolio (e.g. S&P 500 Index, 60/40 Stock-Bond Portfolio)
    risk_free_rate = Tbill rate (annualized)
    financing_rate = portfolio margin/borrowing cost (annualized) to layer new asset on top of prevailing portfolio (e.g. LIBOR + 60bps). No financing rate is reasonable for derivate overlay products.
    weight_asset = % weight you wish to overlay for the new asset on top of the previous portfolio, 25% overlay allocation is standard
    weight_base_portfolio = % weight of the replacement portfolio, 100% pre-existing portfolio value is standard
    periodicity = the frequency of the data you are sampling, typically 12 for monthly or 252 for trading day count"""
    # convert annual financing based on periodicity
    financing_rate=((financing_rate+1)**(1/periodicity)-1)

    # compose new portfolio
    new_port=(new_asset-financing_rate)*(weight_asset) + base_portfolio*(weight_base_portfolio)

    # calculate annualized return of new portfolio and subtract risk-free rate
    annualized_return_number = annualized_return(new_port, periodicity=periodicity) - risk_free_rate
    return annualized_return_number

def wabp_portfolio_risk(new_asset,
                   base_portfolio,
                   risk_free_rate = 0,
                   financing_rate = 0,
                   weight_asset = 0.20,
                   weight_base_portfolio = 0.80,
                   periodicity = 252):
    """Win Above Base Portolio (WABP) Portfolio Risk: Volatility of the aggregate portfolio after a new asset is financed and layered on top of the replacement portfolio.
    new_asset = returns of the asset you are thinking of adding to your portfolio
    base_portfolio = returns of your pre-existing portfolio (e.g. S&P 500 Index, 60/40 Stock-Bond Portfolio)
    risk_free_rate = Tbill rate (annualized)
    financing_rate = portfolio margin/borrowing cost (annualized) to layer new asset on top of prevailing portfolio (e.g. LIBOR + 60bps). No financing rate is reasonable for derivate overlay products.
    weight_asset = % weight you wish to overlay for the new asset on top of the previous portfolio, 25% overlay allocation is standard
    weight_base_portfolio = % weight of the replacement portfolio, 100% pre-existing portfolio value is standard
    periodicity = the frequency of the data you are sampling, typically 12 for monthly or 252 for trading day count"""
    # convert annual financing and risk free rates based on periodicity
    financing_rate = ((financing_rate+1)**(1/periodicity)-1)
    risk_free_rate = ((risk_free_rate+1)**(1/periodicity)-1)
    # compose new portfolio
    new_portfolio = (new_asset - financing_rate)*(weight_asset) + base_portfolio*(weight_base_portfolio)
    # calculated target downside deviation (TDD)
    target_downside_deviation_number = target_downside_deviation(new_portfolio, minimum_acceptable_return = 0)*np.sqrt(periodicity)
    return target_downside_deviation_number

def wabp_new_portfolio_data(new_asset,
                       base_portfolio,
                       risk_free_rate = 0,
                       financing_rate = 0,
                       weight_asset = 0.20,
                       weight_base_portfolio = 0.80,
                       periodicity = 252):
    """Win Above Base Portolio (WABP) return stream: Return series after a new asset is financed and layered on top of the replacement portfolio.
    new_asset = returns of the asset you are thinking of adding to your portfolio
    base_portfolio = returns of your pre-existing portfolio (e.g. S&P 500 Index, 60/40 Stock-Bond Portfolio)
    risk_free_rate = Tbill rate
    financing_rate = portfolio margin/borrowing cost to layer new asset on top of prevailing portfolio (e.g. LIBOR + 60bps). No financing rate is reasonable for derivate overlay products.
    weight_asset = % weight you wish to overlay for the new asset on top of the previous portfolio, 25% overlay allocation is standard
    weight_base_portfolio = % weight of the replacement portfolio, 100% pre-existing portfolio value is standard
    periodicity = the frequency of the data you are sampling, typically 12 for monthly or 252 for trading day count"""
    # convert annual financing based on periodicity
    financing_rate = ((financing_rate + 1)**(1/periodicity) - 1)
    new_portfolio = (new_asset - financing_rate) * (weight_asset) + base_portfolio * (weight_base_portfolio)
    return new_portfolio

def calculate_risk_return(ticker, ticker_data, base_portfolio, risk_free_rate, financing_rate, weight_asset,
                          weight_base_portfolio, data_periodicity, risk_return_df):
    risk_return_df.loc[ticker, 'WABP'] = win_above_base_portfolio(
                                                new_asset = ticker_data, 
                                                base_portfolio = base_portfolio,
                                                risk_free_rate = risk_free_rate,
                                                financing_rate = financing_rate,
                                                weight_asset = weight_asset,
                                                weight_base_portfolio = weight_base_portfolio,
                                                periodicity = data_periodicity)
    risk_return_df.loc[ticker, '+Sortino'] = wabp_additive_sortino(new_asset = ticker_data, 
                                                                base_portfolio = base_portfolio,
                                                                        risk_free_rate = risk_free_rate,
                                                                        financing_rate = financing_rate,
                                                                        weight_asset = weight_asset,
                                                                        weight_base_portfolio = weight_base_portfolio,
                                                                        periodicity = data_periodicity)
    risk_return_df.loc[ticker, '+Ret_To_MaxDD'] = wabp_additive_return_maximum_drawdown(
                                                            new_asset = ticker_data, 
                                                            base_portfolio = base_portfolio,
                                                            risk_free_rate = risk_free_rate,
                                                            financing_rate = financing_rate,
                                                            weight_asset = weight_asset,
                                                            weight_base_portfolio = weight_base_portfolio,
                                                            periodicity = data_periodicity)
    risk_return_df.loc[ticker, 'Sharpe'] = sharpe_ratio(
                                                    ticker_data,
                                                    risk_free = risk_free_rate,
                                                    periodicity = data_periodicity)
    risk_return_df.loc[ticker, 'Sortino'] = sortino_ratio(
                                                        ticker_data,
                                                        risk_free = risk_free_rate,
                                                        periodicity = data_periodicity)
    risk_return_df.loc[ticker, 'Max_DD'] = maximum_drawdown(ticker_data)

def calculate_new_risk_return(ticker, ticker_data, base_portfolio, risk_free_rate, financing_rate, weight_asset,
                           weight_base_portfolio, data_periodicity, risk_return_df, new_risk_return_df, new_portfolios):
    new_risk_return_df.loc[ticker, 'Return'] = wabp_portfolio_return(
                                                        new_asset = ticker_data,
                                                        base_portfolio = base_portfolio,
                                                        risk_free_rate = risk_free_rate,
                                                        financing_rate = financing_rate,
                                                        weight_asset = weight_asset,
                                                        weight_base_portfolio = weight_base_portfolio,
                                                        periodicity = data_periodicity)
    new_risk_return_df.loc[ticker, 'Vol'] = wabp_portfolio_risk(
                                                    new_asset = ticker_data,
                                                    base_portfolio = base_portfolio,
                                                    risk_free_rate = risk_free_rate,
                                                    financing_rate = financing_rate,
                                                    weight_asset = weight_asset,
                                                    weight_base_portfolio = weight_base_portfolio,
                                                    periodicity = data_periodicity)
    wnpd = wabp_new_portfolio_data(new_asset = ticker_data,
                              base_portfolio = base_portfolio,
                              risk_free_rate = risk_free_rate,
                              financing_rate = financing_rate,
                              weight_asset = weight_asset,
                              weight_base_portfolio = weight_base_portfolio,
                              periodicity = data_periodicity)
    new_portfolios[ticker] = wnpd
    new_risk_return_df.loc[ticker, 'Sharpe'] = sharpe_ratio(wnpd.copy(),
                                                         risk_free = risk_free_rate,
                                                         periodicity = data_periodicity)
    new_risk_return_df.loc[ticker, 'Sortino'] = sortino_ratio(
                                                        wnpd.copy(),
                                                        risk_free = risk_free_rate,
                                                        periodicity = data_periodicity)
    new_risk_return_df.loc[ticker, 'Max_DD'] = maximum_drawdown(wnpd.copy())
    new_risk_return_df.loc[ticker, 'Ret_To_MaxDD'] = return_maximum_drawdown_ratio(
                                                                            wnpd.copy(),
                                                                            risk_free = risk_free_rate,
                                                                            periodicity = data_periodicity)
    new_risk_return_df.loc[ticker, f'WABP_{round(100*weight_asset)}%_asset'] = risk_return_df.loc[ticker, 'WABP']


def retrieve_ticker_data_and_update_risk_return_data_frame(ticker, yahoo,
                                                           csv_file, risk_return_df,
                                                           base_portfolio,
                                                           risk_free_rate, financing_rate, weight_asset, weight_base_portfolio,
                                                           start_date, end_date,
                                                           data_periodicity = 252):
    if yahoo == True:
        ticker_data = retrieve_yahoo_data(ticker, start_date, end_date)
        risk_return_df.loc[ticker, 'Start Date'] = min(ticker_data.index).date()
        risk_return_df.loc[ticker, 'End Date'] = max(ticker_data.index).date()
    else:
        ticker_data = pd.read_csv(Path(csv_file), index_col='ReturnDate', skiprows=2)
        ticker_data = ticker_data[['PercentReturn']]
        risk_return_df.loc[ticker, 'Start Date'] = datetime.strptime(min(ticker_data.index), '%b %Y').date()
        risk_return_df.loc[ticker, 'End Date'] = datetime.strptime(max(ticker_data.index), '%b %Y').date()
        ticker_data = ticker_data[['PercentReturn']]
        ticker_data.reset_index(drop=True, inplace=True)
        ticker_data = ticker_data[:].values
        
    calculate_risk_return(ticker, ticker_data, base_portfolio, risk_free_rate, financing_rate, weight_asset,
                          weight_base_portfolio, data_periodicity, risk_return_df)

def retrieve_ticker_data_and_update_data_frames(ticker, yahoo,
                                               csv_file, risk_return_df, ticker_data_dict, new_risk_return_df, new_portfolios,
                                               base_portfolio,
                                               risk_free_rate, financing_rate, weight_asset, weight_base_portfolio,
                                               start_date, end_date,
                                               data_periodicity = 252):
    if yahoo == True:
        ticker_data = retrieve_yahoo_data(ticker, start_date, end_date)
        ticker_data_dict[ticker] = ticker_data
        risk_return_df.loc[ticker, 'Start Date'] = min(ticker_data.index).date()
        risk_return_df.loc[ticker, 'End Date'] = max(ticker_data.index).date()
    else:
        ticker_data = pd.read_csv(Path(csv_file), index_col='ReturnDate', skiprows=2)
        ticker_data = ticker_data[['PercentReturn']]
        ticker_data_dict[ticker] = ticker_data
        risk_return_df.loc[ticker, 'Start Date'] = datetime.strptime(min(ticker_data.index), '%b %Y').date()
        risk_return_df.loc[ticker, 'End Date'] = datetime.strptime(max(ticker_data.index), '%b %Y').date()
        ticker_data = ticker_data[['PercentReturn']]
        ticker_data.reset_index(drop=True, inplace=True)
        ticker_data = ticker_data[:].values
        
    calculate_risk_return(ticker, ticker_data, base_portfolio, risk_free_rate, financing_rate, weight_asset,
                          weight_base_portfolio, data_periodicity, risk_return_df)
    calculate_new_risk_return(ticker, ticker_data, base_portfolio, risk_free_rate, financing_rate, weight_asset,
                           weight_base_portfolio, data_periodicity, risk_return_df, new_risk_return_df, new_portfolios)

def diversify_stocks_with_base_portfolio(
                                    base_portfolio_name, ticker_list, selected_ticker_list, risk_free_rate, 
                                    financing_rate, weight_asset, weight_base_portfolio,
                                    weight_base_portfolio_stock, weight_base_portfolio_bond,
                                    ticker_base_portfolio_stock, ticker_base_portfolio_bond,
                                    start_date, end_date, save_plots):
    
    new_portfolios = {}
    stock_df = retrieve_yahoo_data(ticker_base_portfolio_stock, start_date, end_date)
    bond_df = retrieve_yahoo_data(ticker_base_portfolio_bond, start_date, end_date)
    base_portfolio_df = ((weight_base_portfolio_stock * stock_df) + 
                        (weight_base_portfolio_bond * bond_df))

    risk_return_df = pd.DataFrame(
                index = ticker_list,
                columns = ['Start Date','End Date','WABP','+Sortino','+Ret_To_MaxDD','Sharpe','Sortino','Max_DD'])
    new_risk_return_df = pd.DataFrame(
                    index = ticker_list,
                    columns = ['Return','Vol','Sharpe','Sortino','Max_DD','Ret_To_MaxDD',f'WABP_{round(100*weight_asset)}%_asset'])
    ticker_data_dict = {}
    csv_file = ""

    for ticker in ticker_list:
        retrieve_ticker_data_and_update_data_frames(
                                            ticker, True, csv_file, risk_return_df, ticker_data_dict, new_risk_return_df,
                                            new_portfolios, base_portfolio_df,
                                            risk_free_rate, financing_rate, weight_asset, weight_base_portfolio,
                                            start_date, end_date,
                                            252)
    risk_return_df.to_csv(f"risk_return_{base_portfolio_name}.csv")
    risk_return_df.to_csv(f'risk_return.csv')
    new_risk_return_df.to_csv(f"new_risk_return_{base_portfolio_name}.csv")
    new_risk_return_df.to_csv(f"new_risk_return.csv")
    new_portfolios_df = pd.DataFrame(new_portfolios)
    new_portfolios_df.to_csv(f"new_portfolios_{base_portfolio_name}.csv")
    new_portfolios_df.to_csv(f"new_portfolios.csv")
    ticker_data_df = pd.DataFrame(ticker_data_dict)
    ticker_data_df.to_csv(f"ticker_data_{base_portfolio_name}.csv")
    ticker_data_df.to_csv(f"ticker_data.csv")

    save_portfolio_cumulative_data_plots(
                                    base_portfolio_name,
                                    ticker_list,
                                    selected_ticker_list,
                                    risk_return_df,
                                    new_risk_return_df,
                                    base_portfolio_df,
                                    new_portfolios,
                                    save_plots)

    return risk_return_df, new_risk_return_df, base_portfolio_df, new_portfolios_df

def calculate_cumulative_product(ticker_list, new_ports, replacement_portfolio, replacement_portfolio_name):
    cumulative_returns = {}
    for ticker in ticker_list:
        cumulative_returns[ticker] = (1 + new_ports[ticker]).cumprod()
    cumulative_returns[replacement_portfolio_name] = (1 + replacement_portfolio).cumprod()
    
    cumulative_returns_df = pd.DataFrame(cumulative_returns)
    cumulative_returns_df.to_csv(f"cumulative_returns_{replacement_portfolio_name}.csv")
    return cumulative_returns_df

def save_portfolio_cumulative_data_plots(
                            base_portfolio_name, ticker_list, selected_ticker_list, risk_return_df,
                            new_risk_return_df, base_portfolio_df, new_portfolios, save_plot):
    sorted_values = risk_return_df.sort_values('Sharpe', ascending=False).head()
    print(f"Sorted by Sharpe:\n{sorted_values}")
    sorted_values = new_risk_return_df.sort_values('Vol', ascending=True).head()
    print(f"Sorted by Vol:\n{sorted_values}")
    sorted_values = risk_return_df.sort_values('WABP', ascending=False).head()
    print(f"Sorted by WABP:\n{sorted_values}")
    cumulative_returns = {}
    for ticker in ticker_list:
        cumulative_returns[ticker] = (1 + new_portfolios[ticker]).cumprod()
    cumulative_returns[base_portfolio_name] = (1 + base_portfolio_df).cumprod()
    #print(f"{cumulative_returns}")
    cumulative_returns_df = pd.DataFrame(cumulative_returns)
    cumulative_returns_df.to_csv(f"cumulative_returns.csv")
    cumulative_returns_df.to_csv(f"cumulative_returns_{base_portfolio_name}.csv")
    
    if save_plot == True:
        plot = cumulative_returns_df.hvplot.line(
            title="Cumulative Returns - Growth of initial investment of $1",
            xlabel = "Year",
            ylabel = "Cumulative Return",
            height = 500,
            width = 1000)
        hvplot.save(plot, "cumulative_returns.png")

    cumulative_returns_selected_df = cumulative_returns_df[selected_ticker_list + [base_portfolio_name]]
    cumulative_returns_selected_df.to_csv(f"cumulative_returns_selected.csv")
    cumulative_returns_selected_df.to_csv(f"cumulative_returns_selected_{base_portfolio_name}.csv")

    if save_plot == True:
        plot = cumulative_returns_selected_df.hvplot.line(
            title="Cumulative Returns Selected - Growth of initial investment of $1",
            xlabel = "Year",
            ylabel = "Cumulative Return",
            height = 500,
            width = 1000)
        hvplot.save(plot, "cumulative_returns_selected.png")

    cumulative_returns_selected_2008_2009_df = cumulative_returns_selected_df.loc['01-01-2008':'12-31-2009']
    cumulative_returns_selected_2008_2009_df.to_csv(f"cumulative_returns_selected_2008_2009.csv")
    cumulative_returns_selected_2008_2009_df.to_csv(f"cumulative_returns_selected_2008_2009_{base_portfolio_name}.csv")
    
    if save_plot == True:
        plot = cumulative_returns_selected_2008_2009_df.hvplot.line(
            title="Cumulative Returns Selected - 2008 to 2009 - Growth of initial investment of $1",
            xlabel = "Year",
            ylabel = "Cumulative Return",
            height = 450,
            width = 900)
        hvplot.save(plot, "cumulative_returns_selected_2008_2009.png")

    cumulative_returns_2020 = {}
    for ticker in ticker_list:
        cumulative_returns_2020[ticker] = (1 + new_portfolios[ticker].loc['01-01-2020':'12-31-2020']).cumprod()
    cumulative_returns_2020[base_portfolio_name] = (1 + base_portfolio_df).loc['01-01-2020':'12-31-2020'].cumprod()    
    cumulative_returns_2020_df = pd.DataFrame(cumulative_returns_2020)
    cumulative_returns_selected_2020_df = cumulative_returns_2020_df[selected_ticker_list + [base_portfolio_name]]
    cumulative_returns_selected_2020_df.to_csv(f"cumulative_returns_selected_2020.csv")
    cumulative_returns_selected_2020_df.to_csv(f"cumulative_returns_selected_2020_{base_portfolio_name}.csv")
    
    if save_plot == True:
        plot = cumulative_returns_selected_2020_df.hvplot.line(
            title="Cumulative Returns Selected - 2020 - Growth of initial investment of $1",
            xlabel = "Year",
            ylabel = "Cumulative Return",
            height = 450,
            width = 900)
        hvplot.save(plot, "cumulative_returns_seleted_2008_2010.csv")

def run_calculations():
    ticker_list = ["qqq", "lqd", "hyg", "tlt", "ief", "shy", "gld", "slv", "efa", "eem", "iyr", "xle", "xlk", "xlf", 'GC=F']
    selected_ticker_list = ['tlt', 'shy', 'GC=F', 'gld']
    risk_free_rate = 0.00
    financing_rate = 0.00
    weight_asset = 0.20
    weight_base_portfolio = 0.80

    weight_base_portfolio_stock = 1.0
    weight_base_portfolio_bond  = 0.0
    ticker_base_portfolio_stock = 'spy'
    ticker_base_portfolio_bond  = 'ief'
    start_date = '2008-01-01'
    end_date = '2020-12-31'
    new_portfolios = {}
    base_portfolio_name = f'stock_{weight_base_portfolio_stock * 100:.0f}_bond_{weight_base_portfolio_bond * 100:.0f}'

    risk_return_df, new_risk_return_df, base_portfolio_df, new_portfolios = diversify_stocks_with_base_portfolio(
                                        base_portfolio_name, ticker_list, selected_ticker_list, risk_free_rate, financing_rate, weight_asset, 
                                        weight_base_portfolio,
                                        weight_base_portfolio_stock, weight_base_portfolio_bond,
                                        ticker_base_portfolio_stock, ticker_base_portfolio_bond,
                                        start_date, end_date, save_plots = True)

    weight_base_portfolio_stock = 0.60
    weight_base_portfolio_bond  = 0.40
    new_portfolios = {}
    base_portfolio_name = f'stock_{weight_base_portfolio_stock * 100:.0f}_bond_{weight_base_portfolio_bond * 100:.0f}'
 
    risk_return_df, new_risk_return_df, base_portfolio_df, new_portfolios = diversify_stocks_with_base_portfolio(
                                        base_portfolio_name, ticker_list, selected_ticker_list, risk_free_rate, financing_rate, weight_asset, 
                                        weight_base_portfolio,
                                        weight_base_portfolio_stock, weight_base_portfolio_bond,
                                        ticker_base_portfolio_stock, ticker_base_portfolio_bond,
                                        start_date, end_date, save_plots = True)