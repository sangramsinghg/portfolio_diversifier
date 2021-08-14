import csv
import sys
import fire
import questionary
from pathlib import Path
import pandas as pd

# provisional ticker to test code
tickers = ["shy","gld","tlt","xle"]

""" Function to decide main options"""
def initial_action():
    "Dialog to select action to be performed"

    initial_action = questionary.select(
        "Which of the following would you like to check",
        choices = ["Check financial ratios", "Visualize simulated expected returns", "Add/remove tickers"]
    ).ask()
    return initial_action

""" Functions to pull the ratios from CSV"""

def load_ratios():
    """Writes account information from CSV to list."""
    csvpath = Path('../risk_ret.csv')
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
                "Max_DD" : max_dd
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

    ratios_selected = ratios_df_clean[ratios_action]

    print(
        f"""Please see the ratios selected below:
        {ratios_selected}
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
    all_tickers = ratios_df.index.values.tolist()
    for ticker in tickers:
        all_tickers.remove(ticker)

    add_ticker_action = questionary.checkbox(
        "Which of the following tickers would you like to add?",
        choices = (all_tickers)
    ).ask()

    return add_ticker_action

def run_add_tickers():

    global tickers

    tickers_to_be_added = add_ticker()
    for ticker in tickers_to_be_added:
        tickers.append(ticker)
    print((f"""
    The new list of tickers is:
    {tickers}"""))
    return(tickers)

def remove_ticker():
    
    global tickers

    remove_ticker_action = questionary.checkbox(
        "Which of the following tickers would you like to remove?",
        choices = (tickers)
    ).ask()

    return remove_ticker_action

def run_remove_tickers():

    global tickers

    tickers_to_be_remove = remove_ticker()
    for ticker in tickers_to_be_remove:
        tickers.remove(ticker)
    print(f"""
    The new list of tickers is:
    {tickers}""")
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
    elif first_action == "Visualize simulated expected returns":
        sys.exit("Montecarlo simulation query code to be completed. Thank you for choosing our services")
    elif first_action == "Add/remove tickers":
        run_add_and_remove_function()

def age_menu():
    "Dialog to select age"

    age_action = questionary.select(
        "Please select your age",
        choices = ["18 - 30","30 - 50","50 - 70",">70"]
    ).ask()

    if age_action == "18 - 30":
        recommended_percent = "80% stocks - 20% bonds"
    elif age_action == "30 - 50":
        recommended_percent = "60% stocks - 40% bonds"
    elif age_action == "50 - 70":
        recommended_percent = "40% stocks - 60% bonds"
    elif age_action == ">70":
        recommended_percent = "20% stocks - 80% bonds"

    print(f"Based on your age we recoment a diversification of {recommended_percent}")

    return age_action

def allocation_menu():
    "Dialog to select allocation"

    allocation_action = questionary.select(
        "Please select your age",
        choices = ["100% stocks","80% stocks - 20% bonds","60% stocks - 40% bonds","40% stocks - 60% bonds","20% stocks - 80% bonds","100% bonds"]
    ).ask()
    run_final_function()
    return allocation_action
    

"""Function that runs the code related to allocation"""
def run_age_function():

    age_menu()

    question = questionary.confirm("Would you like to modify this diversification?}").ask()

    if question == True:
        allocation_menu()
    else:
        run_final_function()


if __name__ == "__main__":
    fire.Fire(run_age_function())


    
    




