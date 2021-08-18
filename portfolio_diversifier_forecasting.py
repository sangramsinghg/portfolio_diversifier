"""
Author: George Kraft
"""
import pandas as pd
from MCForecastTools import MCSimulation

# Configure a Monte Carlo simulation to forecast five years cumulative returns
# from daily_returns_df
number_of_trading_days_in_a_year = 252

def execute_monte_carlo_simulation(ticker,
                                    daily_returns_df,
                                    weight_diversifying_asset,
                                    weight_base_portfolio_stock,
                                    weight_base_portfolio_bond,
                                    number_of_years = 5):
    print("executing monte carlo simulations - weight asset {weight_diverisfying_asset} weight base {weight_base_portfolio}")
    monte_carlo_diversified_portfolio = MCSimulation(
                    portfolio_data = daily_returns_df,
                    weights = [weight_diversifying_asset, weight_base_portfolio_stock, weight_base_portfolio_bond],
                    num_simulation = 500,
                    num_trading_days = number_of_trading_days_in_a_year * number_of_years)

    # Printing the first five rows of the simulation input data
    print(f'{monte_carlo_diversified_portfolio.portfolio_data.head()}')

    # Run a Monte Carlo simulation to forecast five years cumulative returns
    results = monte_carlo_diversified_portfolio.calc_cumulative_return()
    print(f'{results}')
    # Visualize the Monte Carlo simulation by creating an overlay line plot
    #diversified_portfolio_line_plot = monte_carlo_diversified_portfolio.plot_simulation()

    # Visualize the Monte Carlo simulation by creating a histogram
    diversified_portfolio_distribution_plot = monte_carlo_diversified_portfolio.plot_distribution()

    # Generate the summary statistics for the Monte Carlo simulation
    diversified_portfolio_table = monte_carlo_diversified_portfolio.summarize_cumulative_return()

    # Print the table of summary statistics
    print(diversified_portfolio_table)
    diversified_portfolio_table.to_csv(f'monte_carlo_simulation_table_{ticker}.csv')

    # Using the lower and upper `95%` confidence interval values 
    # (index positions 8 & 9 from the diversified_portfolio_table)
    # calculate  the range of the possible outcomes for a $10,000 investment 
    diversified_portfolio_ci_lower = round(diversified_portfolio_table[8]*10000,2)
    diversified_portfolio_ci_upper = round(diversified_portfolio_table[9]*10000,2)

    # Print results
    print(f"There is a 95% chance that an initial investment of $10,000 in the portfolio"
         f" ${diversified_portfolio_ci_lower} and ${diversified_portfolio_ci_upper}.")



