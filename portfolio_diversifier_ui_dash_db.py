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
#from MCForecastTools import plot_simulation
#Saved Data Files from CSV or DataFrame need to add some sample data for visual help
#CSV file need help with the explanation of each

#Different questions we can use for the data frame
#data = data.query("") For Rodrigo's quesitons

#print(data_tickers)

#risk return ratio 60 and 40 ratio with all mixes of Tickers 
risk_return = pd.read_csv("risk_ret.csv")
column_names = ['Tickers','Start Date','End Date','WARP','+Sortino','+Ret_To_MaxDD','Sharpe','Sortino','Max_DD']
risk_return.columns = column_names


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

#Cumulative Returns
cumulative_total= pd.read_csv('cumulative_returns_selected.csv',index_col='Date')
fig_cumulative_total = px.line(cumulative_total,
 title='Cumulative Returns since 2008 to 2020', template='plotly_dark')

cumulative_bull= pd.read_csv('cumulative_returns_selected_2010_2019.csv',index_col='Date')
fig_cumulative_bull = px.line(cumulative_bull,
                            title='Cumulative returns would be in a bull market 10-19')

cumulative_bear= pd.read_csv('cumulative_returns_selected_2008_2009.csv', index_col='Date')
fig_cumulative_bear= px.line(cumulative_bear,
 title='Cumulative Returns during a bear market 08-09', template='plotly_dark')

#MonteCarlo Forcasting
mc_gld_table = pd.read_csv('monte_carlo_simulation_table_gld.csv')
mc_gld_table.columns= ['type', 'value']
mc_gld = pd.read_csv('monte_carlo_simulative_returns_gld.csv')
mc_gld.columns= ['Trading Days','mean','median','min','max']
mc_gld.set_index('Trading Days',inplace=True)
fig_mc_gld = px.line(mc_gld, y=['max','min','mean','median'], template='plotly_dark')

mc_shy = pd.read_csv('monte_carlo_simulative_returns_shy.csv')
fig_mc_shy = px.line(mc_shy, y=['max','min','mean','median'])

mc_tlt= pd.read_csv('monte_carlo_simulative_returns_tlt.csv')
fig_mc_tlt = px.line(mc_tlt,  y=['max','min','mean','median'], template='plotly_dark')







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
                 dcc.Graph(figure=fig_cumulative_bear)
            ]),
            dcc.Tab(label='Forcasting Results', value='tab-3', children=[
          #     dash_table.DataTable(id='table',
          #             columns=[{"name": 'type', "id": 'value'}],
          #             data=mc_gld_table.to_dict(),
          # ),
                dcc.Graph(figure=fig_mc_gld),
                dcc.Graph(figure=fig_mc_shy),
                dcc.Graph(figure=fig_mc_tlt),
        ]),
    ])
         
    ]
)


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
 
 
 

html_run = '''
HTML
<div>
   <h1>Analyzing your Current Portfolio</h1>
  <p>Current stock and bond split</p>
   <!-- Rest of the app -->
<div>
'''

if __name__ == "__main__":
    app.run_server(debug=True)