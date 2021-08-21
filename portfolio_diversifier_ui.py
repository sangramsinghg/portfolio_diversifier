"""
Author: Rodrigo Monge
"""
import csv
import sys
import fire
import questionary
from pathlib import Path
import pandas as pd
from portfolio_diversifier_ratios_and_calculations import diversify_stocks_with_base_portfolio
from portfolio_diversifier_ratios_and_calculations import retrieve_yahoo_data_close
from portfolio_diversifier_forecasting import execute_monte_carlo_simulation

ticker_list = ["qqq", "lqd", "hyg", "tlt", "ief", "shy", "gld", "slv", "efa", "eem", "iyr", "xle", "xlk", "xlf"]
#selected_ticker_list = ['shy', 'gld', 'tlt']
selected_ticker_list = ['shy', 'gld', 'tlt']
tickers = selected_ticker_list
risk_free_rate = 0.00
financing_rate = 0.00
weight_diversifying_asset = 0.20
weight_base_portfolio = 0.80

weight_base_portfolio_stock = 0.60
weight_base_portfolio_bond  = 0.40
ticker_base_portfolio_stock = 'spy'
ticker_base_portfolio_bond  = 'ief'
start_date = '2008-01-01'
end_date = '2020-12-31'

base_portfolio_df = pd.DataFrame()
new_portfolios_df = pd.DataFrame()

""" Function to decide main options"""
def initial_action():
    "Dialog to select action to be performed"

    initial_action = questionary.select(
        "Which of the following would you like to check",
        choices = [ "Check financial ratios",
                    "Forecast using Monte Carlo",
                    "Visualize results",
                    "Add/remove tickers"]
    ).ask()
    return initial_action

""" Functions to pull the ratios from CSV"""

def load_ratios():
    """Writes account information from CSV to list."""
    csvpath = Path('./risk_return.csv')
    ratios = []
    with open(csvpath, newline='') as csvfile:
        rows = csv.reader(csvfile)
        header = next(rows)
        for row in rows:
            ticker = str(row[0])
            warp = float(row[3])
            plus_sortino = float(row[4])
            ret_to_maxdd = float(row[5])
            sharpe = float(row[6])
            sortino = float(row[7])
            max_dd = float(row[8])
            ratio = {
                "ticker" : ticker,
                "WARP" : warp,
                "+Sortino" : plus_sortino,
                "+Ret_To_MaxDD" : ret_to_maxdd,
                "Sharpe" : sharpe,
                "Sortino" : sortino,
                "Max_DD" : max_dd,
            }
            ratios.append(ratio)
        return ratios

""" Functions to make a choice of ratio"""

def ratios_menu():
    "Dialog to select ratios"

    ratios_action = questionary.checkbox(
        "Which of the following ratios would you like to visualize?",
        choices = ["WARP","+Sortino","+Ret_To_MaxDD","Sharpe","Sortino","Max_DD"]
    ).ask()
    return ratios_action


"""The function for running the ratios selected."""
def run_ratios():

    # Cleans the Dataframe
    ratios_df = pd.DataFrame(load_ratios())
    ratios_df = ratios_df.set_index("ticker")
    ratios_df_clean = ratios_df.loc[tickers]

    # Initiates action based on selected ratios
    ratios_action = ratios_menu()

    #Functions to make a choice to sort the values
    if len(ratios_action) > 1:
        sort_action = questionary.select(
            "Which of the following ratios would you like to sort by?",
            choices = ratios_action
        ).ask()
    elif len(ratios_action) == 1:
        sort_action = ratios_action
    else:
        print(f"Nothing selected - len(ratios_action) == {len(ratios_action)}")

    if len(ratios_action) >= 1:
        ratios_selected = ratios_df_clean[ratios_action]
        if sort_action == "Vol":
            ratios_selected = ratios_selected.sort_values(by=sort_action, ascending=True)
        else:
            ratios_selected = ratios_selected.sort_values(by=sort_action, ascending=False)

        print(
            f"""Please see the ratios selected below:\n{ratios_selected}
            """
        )

"""Function that runs the code related to selecting ratios, including looping back in case more actions are needed"""
def run_ratios_function():

    run_ratios()

    question = questionary.confirm("Would you like to perform another action").ask()

    """Conditional to determine if the clients wants to do any additional actions"""
# For now this will loop to a level lower than required, it is a placeholder to check that the code works as intended
    if question == True:
        run_final_function()
    else:
        sys.exit(
        "Thank you for choosing our services"
    )

""" Function to either add ticker or remove"""
def ticker_action():
    "Dialog to select action to be performed"

    ticker_action = questionary.select(
        "Please select one of the following options",
        choices = ["Add tickers", "Remove tickers"]
    ).ask()
    return ticker_action

""" Function to either add ticker or remove"""
def add_ticker():
    
    global tickers

    # Cleans the Dataframe
    ratios_df = pd.DataFrame(load_ratios())
    ratios_df = ratios_df.set_index("ticker")
    all_tickers = ticker_list
    for ticker in tickers:
        all_tickers.remove(ticker)

    add_ticker_action = questionary.checkbox(
        "Which of the following tickers would you like to add?",
        choices = (all_tickers)
    ).ask()

    print(f"""
    Add tickers {add_ticker_action}\n""")
    return add_ticker_action

def run_add_tickers():

    global tickers

    tickers_to_be_added = add_ticker()
    for ticker in tickers_to_be_added:
        tickers.append(ticker)
    print((f"""
    The new list of tickers is:
    {tickers}"""))
    calculate_ratios_and_returns_for_diversified_portfolio()
    return(tickers)

def remove_ticker():
    
    global tickers

    remove_ticker_action = questionary.checkbox(
        "Which of the following tickers would you like to remove?",
        choices = (tickers)
    ).ask()

    print(f"""
    Removed ticker {remove_ticker_action}\n""")
    return remove_ticker_action

def run_remove_tickers():

    global tickers

    tickers_to_be_remove = remove_ticker()
    for ticker in tickers_to_be_remove:
        tickers.remove(ticker)
    print(f"""
    The new list of tickers is:
    {tickers}""")
    calculate_ratios_and_returns_for_diversified_portfolio()
    return(tickers)

def run_add_and_remove_function():

    add_or_remove_action = ticker_action()

    if add_or_remove_action == "Add tickers":
        run_add_tickers()
    elif add_or_remove_action == "Remove tickers":
        run_remove_tickers()

    run_final_function()


# End function to run everything
def run_final_function():

    first_action = initial_action()

    if first_action == "Check financial ratios":
        run_ratios_function()
    elif first_action == "Forecast using Monte Carlo":
        for ticker in tickers:
            ticker_df = retrieve_yahoo_data_close(ticker, start_date, end_date)
            base_stock_df = retrieve_yahoo_data_close(ticker_base_portfolio_stock, start_date, end_date)
            base_bond_df = retrieve_yahoo_data_close(ticker_base_portfolio_bond, start_date, end_date)
            daily_returns_df = pd.concat([ticker_df, base_stock_df, base_bond_df], axis=1)
            daily_returns_df.columns = [ticker, ticker_base_portfolio_stock, ticker_base_portfolio_bond]
            daily_returns_df.columns = pd.MultiIndex.from_product([daily_returns_df.columns, ['close']])
            
            execute_monte_carlo_simulation(	ticker,
                                            daily_returns_df,
                                            weight_diversifying_asset,
                                            weight_base_portfolio * weight_base_portfolio_stock,
                                            weight_base_portfolio * weight_base_portfolio_bond,
                                            number_of_years = 5)

        file = open('selected_tickers.csv', 'w', newline = '\n')
        with file:
            writer = csv.writer(file)
            writer.writerow(tickers)

        question = questionary.confirm("Would you like to perform another action").ask()

        """Conditional to determine if the clients wants to do any additional actions"""
    
        if question == True:
            run_final_function()
        else:
            sys.exit(
            "Thank you for choosing our services"
            )
    elif first_action == 'Visualize results':
        sys.exit("Please type python portfolio_diversifier_ui_dash_db.py on the command line")
    elif first_action == "Add/remove tickers":
        run_add_and_remove_function()

def age_menu():
    "Dialog to select age"
    global weight_base_portfolio_stock
    global weight_base_portfolio_bond

    age_action = questionary.select(
        "Please select your age",
        choices = ["18 - 30", "30 - 50", "50 - 70", "> 70"]
    ).ask()

    if age_action == "18 - 30":
        recommended_percent = "80% stocks - 20% bonds"
        weight_base_portfolio_stock = 0.80
        weight_base_portfolio_bond  = 0.20
    elif age_action == "30 - 50":
        recommended_percent = "60% stocks - 40% bonds"
        weight_base_portfolio_stock = 0.60
        weight_base_portfolio_bond  = 0.40
    elif age_action == "50 - 70":
        recommended_percent = "40% stocks - 60% bonds"
        weight_base_portfolio_stock = 0.40
        weight_base_portfolio_bond  = 0.60
    elif age_action == "> 70":
        recommended_percent = "20% stocks - 80% bonds"
        weight_base_portfolio_stock = 0.20
        weight_base_portfolio_bond  = 0.80

    print(f"Based on your age we recomend a portfolio of {recommended_percent}")

    return age_action

def calculate_ratios_and_returns_for_diversified_portfolio():
    global base_portfolio_df
    global new_portfolios_df
    base_portfolio_name = f'stock_{weight_base_portfolio_stock * 100:.0f}_bond_{weight_base_portfolio_bond * 100:.0f}'
    risk_return_df, new_risk_return_df, base_portfolio_df, new_portfolios_df = diversify_stocks_with_base_portfolio(
                                        base_portfolio_name, selected_ticker_list, selected_ticker_list,
                                        risk_free_rate, financing_rate, weight_diversifying_asset, weight_base_portfolio,
                                        weight_base_portfolio_stock, weight_base_portfolio_bond,
                                        ticker_base_portfolio_stock, ticker_base_portfolio_bond,
                                        start_date, end_date, save_plots = False)

def allocation_menu():
    "Dialog to select allocation"
    global weight_base_portfolio_stock
    global weight_base_portfolio_bond

    allocation_action = questionary.select(
        "Please select your portfolio allocation",
        choices = [ "100% stocks",
                    "80% stocks - 20% bonds",
                    "60% stocks - 40% bonds",
                    "40% stocks - 60% bonds",
                    "20% stocks - 80% bonds",
                    "100% bonds", 
                    "Enter Manually"]
    ).ask()

    if allocation_action == "100% stocks":
        weight_base_portfolio_stock = 1.00
        weight_base_portfolio_bond  = 0.00
    elif allocation_action == "80% stocks - 20% bonds":
        weight_base_portfolio_stock = 0.80
        weight_base_portfolio_bond  = 0.20
    elif allocation_action == "60% stocks - 40% bonds":
        weight_base_portfolio_stock = 0.60
        weight_base_portfolio_bond  = 0.40
    elif allocation_action == "40% stocks - 60% bonds":
        weight_base_portfolio_stock = 0.40
        weight_base_portfolio_bond  = 0.60
    elif allocation_action == "20% stocks - 80% bonds":
        weight_base_portfolio_stock = 0.20
        weight_base_portfolio_bond  = 0.80
    elif allocation_action == "100% bonds":
        weight_base_portfolio_stock = 0.00
        weight_base_portfolio_bond  = 1.00
    elif allocation_action == "Enter Manually":
        try:
            stock_ratio = questionary.text("Please enter the stock ratio (intergers 0 to 100), otherwise default 60/40 will be selected as default").ask()
            stock_ratio = int(stock_ratio)
            if stock_ratio >= 0 & stock_ratio <= 100:
                weight_base_portfolio_stock = stock_ratio/100
                weight_base_portfolio_bond = 1.00 - stock_ratio/100
            else:
                weight_base_portfolio_stock = 0.60
                weight_base_portfolio_bond  = 0.40
        except:
            print("Selecting the default 60/40 portfolio")
            weight_base_portfolio_stock = 0.60
            weight_base_portfolio_bond  = 0.40
    
    calculate_ratios_and_returns_for_diversified_portfolio()
    run_final_function()
    return allocation_action
    

"""Function that runs the code related to allocation"""
def run_age_function():

    age_menu()

    question = questionary.confirm("Would you like to modify this diversification?").ask()

    if question == True:
        allocation_menu()
    else:
        calculate_ratios_and_returns_for_diversified_portfolio()
        run_final_function()

if __name__ == "__main__":
    print(f"Main Function\n")
    fire.Fire(run_age_function())
