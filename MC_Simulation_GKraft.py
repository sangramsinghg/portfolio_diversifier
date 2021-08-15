import pandas as pd
from MCForecastTools import MCSimulation

# Configure a Monte Carlo simulation to forecast five years cumulative returns
# for current_closing_prices_df
# Use an even weight of .33 across all 3 stocks

equity_weighting = .45
bonds_weighting = .30
diversifier_weighting = .25


MC_diversified_portfolio = MCSimulation(
    portfolio_data = asset_classes_closing_prices_df,
    weights = [equity_weighting,bonds_weighting,diversifier_weighting],
    num_simulation = 1000,
    num_trading_days = 252*5
)

# Printing the first five rows of the simulation input data
MC_diversified_portfolio.portfolio_data.head()

# Run a Monte Carlo simulation to forecast five years cumulative returns
MC_diversified_portfolio.calc_cumulative_return()

# Visualize the Monte Carlo simulation by creating an overlay line plot
diversified_portfolio_line_plot = MC_diversified_portfolio.plot_simulation()

# Visualize the Monte Carlo simulation by creating a histogram
diversified_portfolio_distribution_plot = MC_diversified_portfolio.plot_distribution()

# Generate the summary statistics for the Monte Carlo simulation
diversified_portfolio_table = MC_diversified_portfolio.summarize_cumulative_return()

# Print the table of summary statistics
print(diversified_portfolio_table)

# Using the lower and upper `95%` confidence interval values 
# (index positions 8 & 9 from the diversified_portfolio_table)
# calculate  the range of the possible outcomes for a $10,000 investment 
diversified_portfolio_ci_lower = round(diversified_portfolio_table[8]*10000,2)
diversified_portfolio_ci_upper = round(diversified_portfolio_table[9]*10000,2)

# Print results
print(f"There is a 95% chance that an initial investment of $10,000 in the portfolio"
      f" ${diversified_portfolio_ci_lower} and ${diversified_portfolio_ci_upper}.")