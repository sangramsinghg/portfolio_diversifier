# portfolio_diversifier
Portfolio Diversifier

## Why not use Sharpe for picking stocks:

![Sharpe 1](Images/why_not_sharpe_1.png)
![Sharpe 2](Images/why_not_sharpe_2.png)

## What is the solution? WARP (Win Above Replacement Portfolio - courtesy Artemis Capital Management):

![WARP](Images/warp.png)

WARP > 0 
ASSET IS IMPROVING YOUR PORTFOLIO BY INCREASING: 
            1. Return to Downside Volatility; 
            2. Return to MAX Drawdown; 
            3. Or BOTH. 
WARP < 0 
ASSET HURTS YOUR PORTFOLIO BY REPLICATING EXISTING EXPOSURES AND/OR INCREASING DRAWDOWNS AND VOLATILITY.

## Picking Stocks based on WARP vs Sharpe:

![Picking Stocks using WARP](Images/picking_stocks_using_warp.png)

WARP > 0 
ASSET IS IMPROVING YOUR PORTFOLIO BY INCREASING: 
            1. Return to Downside Volatility; 
            2. Return to MAX Drawdown; 
            3. Or BOTH. 
WARP < 0 
ASSET HURTS YOUR PORTFOLIO BY REPLICATING EXISTING EXPOSURES AND/OR INCREASING DRAWDOWNS AND VOLATILITY.

![Picking Stocks using Sharpe](Images/picking_stocks_using_sharpe.png)

## Analyzing stocks historically:

portfolio mixing 20% tlt (picked based on WARP) with 80% spy performs better than portfolio mixing 20% shy (picked based on Sharpe) with 80% spy

### 2008 to 2020:
![Historic Performance in 2008 to 2020](Images/analyzing_stocks_historically_from_2008_to_2020.png)

### 2008 to 2009:
![Historic Performance in 2008 to 2009](Images/analyzing_stocks_historically_from_2008_to_2009.png)

### 2020:
![Historic Performance in 2020](Images/analyzing_stocks_historically_in_2020.png)

## Forecasting for a 20% tlt 48% spy 32% ier portfolio using Monte Carlo - 
![Forecasting 20% tlt 48% spy 32% ier](Images/forecasting_of_a_20_tlt_48_spy_32_ier_portfolio_using_monte_carlo.png)

count        500 
mean         1.55 
std          0.37
min          0.69 
25%          1.29 
50%          1.51 
75%          1.76 
max          2.95 
95% CI - 
Lower        0.91 
Upper        2.41

There is a 95% chance that an initial investment of $10,000 in the portfolio Returns $9071.96 to $24128.53.

## Identifying Target Customers for the MVP:

![Target Customer SF](Images/identifying_target_customers_in_sf.png)

## UI Flow:

![UI Flow](Images/ui_flow.png)

## Dash Output:

![Dash Output](Images/dash_output.png)

---

## Technologies

This project uses python 3.7 along with the following packages:

* [JupyterLab](https://jupyterlab.readthedocs.io/en/stable/) - Web based user interface for data analysis.

* [pandas](https://github.com/pandas-dev/pandas) - Data analysis and manipulation library.

* [Dash](https://dash.plotly.com/) - Dash is a productive Python framework for building web analytic applications.

* [Yfinance](https://pypi.org/project/yfinance/) - reliable, threaded, and Pythonic way to download historical market data from Yahoo! finance.

* [hvplot](https://hvplot.holoviz.org/) - hvPlot provides a high-level plotting API built on HoloViews that provides a general and consistent API for plotting data

* [Questionary](https://pypi.org/project/questionary/) - Questionary is a Python library for effortlessly building pretty command line interfaces

* [Numpy](https://numpy.org/) - NumPy brings the computational power of languages like C and Fortran to Python

* Monte Carlo - Forecasting data to the future.
---

## Installation Guide

Please install the following before starting the application

```python
  pip install jupyterlab
  pip install pandas
  pip install dash
  pip install dash_core_components
  pip install dash_html_components
  pip install pandas
  pip install plotly
  pip install dash_bootstrap_components
  pip install dash_table
  pip install pathlib
  pip install fire
  pip install questionary 
  pip install hvplot
  pip install datetime
  pip install numpy
  pip install yfinance

```
In case of issues, please see the requirements.txt for a complete list of packages with versions needed to run this application

For problems with the installation:
```python
  conda deactivate
  conda install ipykernel -y
  conda create -n pyvizenv python=3.7 -y
  conda activate pyvizenv
  conda install -c conda-forge jupyterlab=2 -y
  conda install -c plotly plotly=4.13. -y
  conda install -c pyviz hvplot -y
  conda install -c conda-forge nodejs=12 -y
  conda install streamz -y
  pip install python-dotenv decorator==4.3 networkx
  conda install nb_conda_kernels ipykernel -y
  jupyter labextension install jupyterlab-plotly@4.13.0 --no-build
  jupyter labextension install @jupyter-widgets/jupyterlab-manager plotlywidget@4.13.0 --no-build
  jupyter labextension install @pyviz/jupyterlab_pyviz --no-build
  conda list plotly
  conda list hvplot
  conda list nodejs
```
---

## Usage

```python
python portfolio_diversifier_ui.py
```
Command Line Usage
![Command Line Usage](Images/command_line_usage.png)

To launch web output using Dash:
```python
python portfolio_diversifier_ui_dash_db.py
```

---

## Contributors

* Sangram Singh (sangramsinghg@yahoo.com)
* Dylan Bowsky
* Rodrigo Monge
* George Kraft

---

## License

MIT