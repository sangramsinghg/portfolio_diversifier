import csv
import sys
import fire
import questionary
from pathlib import Path
import pandas as pd

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
    return allocation_action


"""Function that runs the code related to allocation"""
def run_age_function():

    age_menu()

    question = questionary.confirm("Would you like to modify this diversification?}").ask()

    if question == True:
        allocation_menu()

run_age_function()
