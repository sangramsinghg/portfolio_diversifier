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
from MCForecastTools import plot_simulation
#Saved Data Files from CSV or DataFrame need to add some sample data for visual help
#CSV file need help with the explanation of each
data_tickers = pd.read_csv("ticker_data.csv")
#Different questions we can use for the data frame
#data = data.query("") For Rodrigo's quesitons
data_tickers.sort_index(inplace=True)
#print(data_tickers)

#risk return ratio 60 and 40 ratio with all mixes of Tickers 
risk_return = pd.read_csv("risk_ret.csv")
column_names = ['Tickers','Start Date','End Date','WARP','+Sortino','+Ret_To_MaxDD','Sharpe','Sortino','Max_DD']
risk_return.columns = column_names

#print(risk_return)





#risk and return updated to 60/40 with added diversifier with 25% weight(default)
risk_return_updated = pd.read_csv("new_risk_ret.csv")
#print(risk_return_updated)
risk_return_updated= risk_return_updated.transpose()

new_ports = pd.read_csv("new_ports.csv")
#print(new_ports)
new_ports= new_ports.transpose()



#Plotly Graphs 
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
fig_cumulative_bull=  px.line(cumulative_bull,
 title='Cumulative returns would be in a bull market 10-19')

cumulative_bear= pd.read_csv('cumulative_returns_selected_2008_2009.csv', index_col='Date')
fig_cumulative_bear= px.line(cumulative_bear, title='Cumulative Returns during a bear market 08-09', template='plotly_dark')

#MonteCarlo Forcasting
mc_gld = pd.read_csv('monte_carlo_simulation_table_gld.csv')
fig_mc_gld = mc_gld.plot_simulation()

mc_shy = pd.read_csv('monte_carlo_simulation_table_shy.csv')
fig_mc_shy = mc_shy.plot_simulation()

mc_tlt= pd.read_csv('monte_carlo_simulation_table_tlt.csv')
fig_mc_tlt = mc_tlt.plot_simulation()






#Creating the style of the Dashboard currently using a simple tab measure
external_stylesheets= [dbc.themes.BOOTSTRAP]
app = dash.Dash(__name__, external_stylesheets=external_stylesheets, suppress_callback_exceptions=True)


app.title = "Portfolio Diversifier"

#Centering the Titles and sub titles
body = dbc.Container([ 
dbc.Row(
            [
            html.H1(children = "Portfolio Diversifier", style={"fontSize": "48px",
             "color": "blue"},
         className="header-title")
            ], justify="center", align="center", className="h-50"
            )
],style={"height": "10vh"})
body_sub = dbc.Container([ 
dbc.Row(
            [
            html.P(children = "Current Risk returns for most common tickers using different ratios",
         style={"fontSize": "24px", "color": "green"})
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
                 dcc.Graph(id="line_graph_ratio", figure=fig_bar_warp
        ),
        html.Br(),
        dcc.Graph(id="sharpe_ratio",
            figure=fig_bar_sharpe),
        dcc.Graph(
            figure=fig_bar_sortino),
            ] ),
            dcc.Tab(label='Forecasting', value= 'tab-2', children=[
                 dcc.Graph(figure=fig_mc_gld),
                 dcc.Graph(figure=fig_mc_shy),
                 dcc.Graph(figure=fig_mc_tlt)
            ]),
            dcc.Tab(label='Cumulative', value='tab-3', children=[
                dcc.Graph(figure=fig_cumulative_total),
                dcc.Graph(figure=fig_cumulative_bull),
                dcc.Graph(figure=fig_cumulative_bear),
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
 
 
 
# @app.callback(
#     [Output(component_id='output_container', component_property='children'),
#     Output(component_id="sharpe_ratio", component_property='figure')],
#     [Input(component_id='select_ratio', component_property='value')]
# )
# def update_ratio(option):
#     print(option)
#     print(type(option))

#     container= f"The ratio selected was: {option}"
#     dff = risk_return.copy()
#     dff = dff[dff["Sharpe"] == option]

#     fig = px.line(data_frame=dff,x= "Tickers" ,y= "Sharpe")
    
    
#     return container, fig

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