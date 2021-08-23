"""
portfolio_diversifier_ui_dash_db.py

Author: Dylan Bowsky

"""

# import appropriate modules
import csv
import dash
import dash_core_components as dcc
from dash_core_components.Dropdown import Dropdown
from dash_core_components.Graph import Graph
import dash_html_components as html
import pandas as pd
import plotly.express as px
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output
import dash_table
from pathlib import Path
import os
import sys

# get current directory
cur_dir = os.getcwd()

# create the full path - if the cur dir does not included portfolio diversifier then add it
def create_full_path(file_name):
  if os.path.basename(cur_dir) != 'portfolio_diversifier':
    cur_full_path = os.path.join(cur_dir, "portfolio_diversifier", file_name)
  else:
    cur_full_path = os.path.join(cur_dir, file_name)
  return cur_full_path

#Read risk return ratio with all mixes of Tickers 
try:
  risk_return = pd.read_csv(create_full_path("risk_return.csv"))
  column_names = ['Tickers','Start Date','End Date','WARP','+Sortino','+Ret_To_MaxDD','Sharpe','Sortino','Max_DD']
  risk_return.columns = column_names
except:
  sys.exit("Please run python portfolio_diviersifier_ui.py")

"""Here are all the graphs we will be using for the dash
as of now we currently have 3 categories with risk return ratio, cumulative return,
and Forcasting using Monte Carlo. The Dataframes we are using are the ones created 
by the csv files selected by the user this Dash gives an interactive look into the 
possible returns for user"""

risk_return.sort_values('WARP', inplace=True, ascending=False)
fig_bar_warp = px.bar(risk_return,
 x="Tickers",y='WARP',
  hover_data=["Tickers"],
   title="Risk and return looking at only WARP Ratio", template='plotly_dark')
risk_return.sort_values('Sharpe', inplace=True, ascending=False)
fig_bar_sharpe = px.bar(risk_return,
 x="Tickers",y='Sharpe',
  hover_data=["Tickers"], title="Risk and return looking at only Sharpe Ratio")

risk_return.sort_values('Sortino', inplace=True, ascending=False)
fig_bar_sortino = px.bar(risk_return,
 x="Tickers",y='Sortino',
  hover_data=["Tickers"],
   title="Risk and return looking at Sortino Ratio", template='plotly_dark')

# Cumulative Returns
# Read Cumulative returns of selected tickers and plot
try:
  cumulative_total= pd.read_csv(create_full_path('cumulative_returns_selected.csv'),index_col='Date')
  fig_cumulative_total = px.line(cumulative_total,
    title='Cumulative Returns since 2008 to 2020', template='plotly_dark')
except:
  sys.exit("Please run python portfolio_diviersifier_ui.py")

# Read cumulative returns from 2010 to 2019 and plot  
try: 
  cumulative_bull= pd.read_csv(create_full_path('cumulative_returns_selected_2010_2019.csv'),index_col='Date')
  fig_cumulative_bull = px.line(cumulative_bull,
                            title='Cumulative returns would be in a bull market 2010-2019')
except:
  sys.exit("Please run python portfolio_diviersifier_ui.py")

# Read cumulative returns from 2008 to 2009 and plot
try:
  cumulative_bear= pd.read_csv(create_full_path('cumulative_returns_selected_2008_2009.csv'), index_col='Date')
  fig_cumulative_bear= px.line(cumulative_bear,
  title='Cumulative Returns during a bear market 2008-2009', template='plotly_dark')
except:
  sys.exit("Please run python portfolio_diviersifier_ui.py")

# Read cumulative returns from 2020 and plot
try:
  cumulative_2020= pd.read_csv(create_full_path('cumulative_returns_selected_2020.csv'), index_col='Date')
  fig_cumulative_2020= px.line(cumulative_2020,
    title='Cumulative Returns during Pandemic of 2020')
except:
  sys.exit("Please run python portfolio_diviersifier_ui.py")

# Read tickers to be used for reading and displaying monte carlo simulations
selected_tickers = []
try:
  file = open(create_full_path('selected_tickers.csv'), 'r', newline = '')
  with file:
    reader = csv.reader(file, delimiter=',')
    for row in reader:
      selected_tickers = selected_tickers + row
except:
  sys.exit("Please run python portfolio_diviersifier_ui.py and monte carlo simulations using forecast option")

# Use tickers to read appropriate montecarlo files and set up the right tables
i = 0
for ticker in selected_tickers:
  try:
    globals()[f'mc_{ticker}_table'] = pd.read_csv(create_full_path(f"monte_carlo_simulation_table_{ticker}.csv"))
  except:
    sys.exit("Please run python portfolio_diviersifier_ui.py and monte carlo simulations using forecase option")
  globals()[f'mc_{ticker}_table'].columns= ['type', 'value']
  globals()[f'mc_{ticker}'] = pd.read_csv(create_full_path(f'monte_carlo_simulative_returns_{ticker}.csv'))
  globals()[f'mc_{ticker}'].columns= ['Trading Days','mean','median','min','max']
  globals()[f'mc_{ticker}'].set_index('Trading Days',inplace=True)
  if i%2 == 0:
    globals()[f'fig_mc_{ticker}'] = px.line(globals()[f'mc_{ticker}'], y=['max','min','mean','median'], template='plotly_dark')
  else:
    globals()[f'fig_mc_{ticker}'] = px.line(globals()[f'mc_{ticker}'], y=['max','min','mean','median'])


#Creating the style of the Dashboard currently using a simple tab measure
external_stylesheets= [dbc.themes.CYBORG]
"""<nav class="navbar navbar-expand-lg navbar-dark bg-Primary">
  <div class="container-fluid">
    <a class="navbar-brand" href="#">Navbar</a>
    <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navbarColor03" aria-controls="navbarColor01" aria-expanded="false" aria-label="Toggle navigation">
      <span class="navbar-toggler-icon"></span>
    </button>

    <div class="collapse navbar-collapse" id="navbarColor02">
      <ul class="navbar-nav me-auto">
        <li class="nav-item">
          <a class="nav-link active" href="#">Home
            <span class="visually-hidden">(current)</span>
          </a>
        </li>
        <li class="nav-item">
          <a class="nav-link" href="#">Features</a>
        </li>
        <li class="nav-item">
          <a class="nav-link" href="#">Pricing</a>
        </li>
        <li class="nav-item">
          <a class="nav-link" href="#">About</a>
        </li>
        <li class="nav-item dropdown">
          <a class="nav-link dropdown-toggle" data-bs-toggle="dropdown" href="#" role="button" aria-haspopup="true" aria-expanded="false">Dropdown</a>
          <div class="dropdown-menu">
            <a class="dropdown-item" href="#">Action</a>
            <a class="dropdown-item" href="#">Another action</a>
            <a class="dropdown-item" href="#">Something else here</a>
            <div class="dropdown-divider"></div>
            <a class="dropdown-item" href="#">Separated link</a>
          </div>
        </li>
      </ul>
      <form class="d-flex">
        <input class="form-control me-sm-2" type="text" placeholder="Search">
        <button class="btn btn-secondary my-2 my-sm-0" type="submit">Search</button>
      </form>
    </div>
  </div>
</nav>"""
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)


app.title = "Portfolio Diversifier"

#Centering the Titles and sub titles
body = dbc.Container([ 
dbc.Row(
            [
            html.H1(children = "Portfolio Diversifier", style={"fontSize": "48px",
             "color": "cyan"},
         className="header-title")
            ], justify="center", align="center", className="h-50"
            )
],style={"height": "10vh"})
body_sub = dbc.Container([ 
dbc.Row(
            [
            html.P(children = "Welcome to your interactive portfolio diversifier please look below to see the latest trends",
         style={"fontSize": "24px", "color": "white"})
            ], justify="center", align="center", className="h-50"
            )
],style={"height": "10vh"})


#clean up graph hover ticker
app.layout = html.Div(id="output_container",
    children =[
        html.H1( body),
        html.P(body_sub),
        dcc.Tabs(id='tabs', value="tab-1",
         children=[
             dcc.Tab(label="Risk Ratio Graphs and Data", children=[
                 dcc.Graph(figure=fig_bar_warp),
        html.Br(),
        dcc.Graph(id="sharpe_ratio",
            figure= fig_bar_sharpe),
        dcc.Graph(
            figure=fig_bar_sortino),
            ] ),
            dcc.Tab(label='Cumulative returns', value= 'tab-2', children=[
                 dcc.Graph(figure=fig_cumulative_total),
                 dcc.Graph(figure=fig_cumulative_bull),
                 dcc.Graph(figure=fig_cumulative_bear),
                 dcc.Graph(figure=fig_cumulative_2020),
            ]),
            dcc.Tab(label='Forcasting Results', value='tab-3', children=[
          #     dash_table.DataTable(id='table',
          #             columns=[{"name": 'type', "id": 'value'}],
          #             data=mc_gld_table.to_dict(),
          # ),
          # Hard coded for now - future improvement is to dynamically load thse figures
                dcc.Graph(figure=fig_mc_gld),
                dcc.Graph(figure=fig_mc_shy),
                dcc.Graph(figure=fig_mc_tlt),
        ]),
    ])
         
    ]
)

# The dash application callback 
@app.callback(Output('tabs_selection', 'children'),
              Input('tabs', 'value'))
def render_content(tab):
    if tab == 'tab-1':
        return html.Div([
            html.H3('Tab content 1')
        ])
    elif tab == 'tab-2':
        return html.Div([
            html.H3('Tab content 2')
            ])
    elif tab == 'tab-3':
        return html.Div([
            html.H3('Tab content 3')
        ])
 
 
 
# Html code
html_run = '''
HTML
<div>
   <h1>Analyzing your Current Portfolio</h1>
  <p>Current stock and bond split</p>
   <!-- Rest of the app -->
<div>
'''

# Main entry point
if __name__ == "__main__":
    app.run_server(debug=True)