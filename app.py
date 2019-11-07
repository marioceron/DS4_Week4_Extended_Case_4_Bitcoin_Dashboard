import pandas as pd
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import plotly.graph_objects as go
import datetime as dt
import numpy as np
from sqlalchemy import create_engine
import os

my_db      = os.environ.get('DB_NAME')
my_user    = os.environ.get('DB_USER')
my_passwd  = os.environ.get('DB_USER_PASSWORD')
my_db_port = os.environ.get('DB_PORT')
my_host_endpoint= = os.environ.get('DB_ENDPOINT_HOST')

sql_conn_str='postgresql://'+my_user+':'+my_passwd+'@'+my_rds_host_endpoint+':'+my_db_port+'/'+my_db

#Connect to PostgreSQL database
engine = create_engine(sql_conn_str)

df = pd.read_sql("SELECT * from trades", engine.connect(), parse_dates=('Entry time',))
#df = pd.read_csv('aggr.csv', parse_dates=['Entry time'])


def exchange_min_date(value):
    #Filter by the Exchange value: df[df['Exchange']=='Bitmex'] or df[df['Exchange']=='Deribit']
    dff=df[df['Exchange']==value]
    #Extract the min and max value of Entry time (start_date) given the Exchange selected
    min_start_date=dff['Entry time'].min()
    #Put into format YYYY MM
    start_date=min_start_date.strftime("%Y")+' '+min_start_date.strftime("%b")
    return start_date

def exchange_max_date(value):
    #Filter by the Exchange value: df[df['Exchange']=='Bitmex'] or df[df['Exchange']=='Deribit']
    dff=df[df['Exchange']==value]
    #Extract the min and max value of Entry time (end_date) given the Exchange selected
    max_end_date=dff['Entry time'].max()
    #Put into format YYYY MM
    end_date=max_end_date.strftime("%Y")+' '+max_end_date.strftime("%b")
    return end_date

def filter_df( df, exchange=None, margin=None, start_date=None, end_date=None):    
    #Copy the dataframe received
    dff = df.copy()
    #dff['YearMonth']=dff['Entry time'].apply(lambda x:x.strftime('%Y%m'))
    #Filter by exchange parameter:
    if exchange:
       dff = dff[dff['Exchange']==exchange]

    #Filter by margin parameter:
    if margin:
        dff = dff[dff['Margin']==int(margin)]
         
    #Filter by start_date and end_date parameters:    
    if  start_date and end_date:
        dff = dff[(dff['Entry time'] >= start_date) & (dff['Entry time'] <= end_date)] 
    #Return the dataframe filtered: dff                  
    return dff

def calc_returns_over_month(dff):
    out = []

    for name, group in dff.groupby('YearMonth'):
        exit_balance = group.head(1)['Exit balance'].values[0]
        entry_balance = group.tail(1)['Entry balance'].values[0]
        monthly_return = (exit_balance*100 / entry_balance)-100
        out.append({
            'month': name,
            'entry': entry_balance,
            'exit': exit_balance,
            'monthly_return': monthly_return
        })
    return out

def calc_btc_returns(dff):
    btc_start_value = dff.tail(1)['BTC Price'].values[0]
    btc_end_value = dff.head(1)['BTC Price'].values[0]
    btc_returns = (btc_end_value * 100/ btc_start_value)-100
    return btc_returns

def calc_strat_returns(dff):
    start_value = dff.tail(1)['Exit balance'].values[0]
    end_value = dff.head(1)['Entry balance'].values[0] 
    returns = (end_value * 100/ start_value)-100
    return returns

def pnl_vs_trade_type(exchange, leverage, start_date, end_date):
    dff = filter_df(df, exchange, leverage, start_date, end_date)
    #Create the :  YearMonth column for the Bar graphic in datetime format: MM YYYY 
    #dff['Year_Month']=dff['Entry time'].apply(lambda x:x.strftime('%b-%Y'))
    dff['Year_Month'] = pd.to_datetime(dff['Entry time'], format='%Y%m')
    #2 Bar Plots of Year_Month vs. Profit group by Trade Type
    data = []
    #Filter fot the Trade type=long in dff1
    dff1=dff[dff['Trade type']=='Long']
    #Plot the bar chart:
    data.append(      
         go.Bar(y=dff1['Pnl (incl fees)'], x=dff1['Year_Month'] ,base=0, name='Long', marker_color='salmon')
     ) 
    #Filter fot the Trade type=Short in dff2
    dff2=dff[dff['Trade type']=='Short']
     #Plot the bar chart:   
    data.append(      
         go.Bar(y=dff2['Pnl (incl fees)'], x=dff2['Year_Month'] , base=0, name='Short', marker_color='black')
     )      
    #Return data   
    return data


def daily_btc_plot(exchange, leverage, start_date, end_date):
    dff = filter_df(df, exchange, leverage, start_date, end_date)
    #Create the :  YearMonth column for the Bar graphic in datetime format: MM YYYY 
    dff['Year_Month'] = pd.to_datetime(dff['Entry time'], format='%Y%m')
    #Line Plot of Year_Month vs. BTC Price
    data = []
    data.append(      
        go.Scatter(y=dff['BTC Price'], x=dff['Year_Month'],name='Daily BTC Price')
     ) 
    return data

def balance_plot(exchange, leverage, start_date, end_date):
    dff = filter_df(df, exchange, leverage, start_date, end_date)
    #Create the :  YearMonth column for the Bar graphic in datetime format: MM YYYY 
    dff['Year_Month'] = pd.to_datetime(dff['Entry time'], format='%Y%m')
    #Balance = Entry balance + Pnl (incl fees):
    dff['balance'] = dff['Exit balance']+dff['Pnl (incl fees)']
    #Line Plot of Year_Month vs. Profit
    data = []
    data.append(      
        go.Scatter(y=dff['balance'], x=dff['Year_Month'],name='Balance')
     ) 
    return data

app = dash.Dash(__name__, external_stylesheets=['https://codepen.io/uditagarwal/pen/oNvwKNP.css', 'https://codepen.io/uditagarwal/pen/YzKbqyV.css'])
app.config.suppress_callback_exceptions = True


app.layout = html.Div(
    children=[
    html.Div(
            children=[
                html.H2(children="Bitcoin Leveraged Trading Backtest Analysis", className='h2-title'),
            ],
            className='study-browser-banner row'
    ),
    html.Div(
        className="row app-body",
        children=[
            html.Div(
                className="twelve columns card",
                children=[
                    html.Div(
                        className="padding row",
                        children=[
                            html.Div(
                                className="two columns card",
                                children=[
                                    html.H6("Select Exchange",),
                                    dcc.RadioItems(
                                        id="exchange-select",
                                        options=[
                                            {'label': label, 'value': label} for label in df['Exchange'].unique()
                                        ],
                                        value='Bitmex',
                                        labelStyle={'display': 'inline-block'}
                                    )
                                ]
                            ),
                            # Leverage Selector
                            html.Div(
                                className="two columns card",
                                children=[
                                    html.H6("Select Leverage"),
                                    dcc.RadioItems(
                                        id="leverage-select",
                                        options=[
                                            {'label': str(label), 'value': str(label)} for label in df['Margin'].unique()
                                        ],
                                        value='1',
                                        labelStyle={'display': 'inline-block'}
                                    ),
                                ]
                            ),
                            html.Div(
                                className="three columns card",
                                children=[
                                    html.H6("Select a Date Range"),
                                    dcc.DatePickerRange(
                                        id="date-range",
                                        display_format="MMM YY",
                                        start_date=df['Entry time'].min(),
                                        end_date=df['Entry time'].max()
                                    ),
                                ]
                            ),
                            html.Div(
                                id="strat-returns-div",
                                className="two columns indicator pretty_container",
                                children=[
                                    html.P(id="strat-returns", className="indicator_value"),
                                    html.P('Strategy Returns', className="twelve columns indicator_text"),
                                ]
                            ),
                            html.Div(
                                id="market-returns-div",
                                className="two columns indicator pretty_container",
                                children=[
                                    html.P(id="market-returns", className="indicator_value"),
                                    html.P('Market Returns', className="twelve columns indicator_text"),
                                ]
                            ),
                            html.Div(
                                id="strat-vs-market-div",
                                className="two columns indicator pretty_container",
                                children=[
                                    html.P(id="strat-vs-market", className="indicator_value"),
                                    html.P('Strategy vs. Market Returns', className="twelve columns indicator_text"),
                                ]
                            ),
                        ]
                )
        ]),
        html.Div(
            className="twelve columns card",
            children=[
                dcc.Graph(
                    id="monthly-chart",
                    figure={
                        'data': []
                    }
                )
            ]
        ),
        html.Div(
                className="padding row",
                children=[
                    html.Div(
                        className="six columns card",
                        children=[
                            dash_table.DataTable(
                                id='table',
                                columns=[
                                    {'name': 'Number', 'id': 'Number'},
                                    {'name': 'Trade type', 'id': 'Trade type'},
                                    {'name': 'Exposure', 'id': 'Exposure'},
                                    {'name': 'Entry balance', 'id': 'Entry balance'},
                                    {'name': 'Exit balance', 'id': 'Exit balance'},
                                    {'name': 'Pnl (incl fees)', 'id': 'Pnl (incl fees)'},
                                ],
                                style_cell={'width': '50px'},
                                style_table={
                                    'maxHeight': '450px',
                                    'overflowY': 'scroll'
                                },
                            )
                        ]
                    ),
                    html.Div(
                        className="six columns card",
                        children=[
                            dcc.Graph(
                                id="pnl-types",
                                figure={
                                        'data': []                                        
                                       }
                            )
                        ]
                    )
                ]
        ),
        html.Div(
                className="padding row",
                children=[
                   html.Div(
                        className="six columns card",
                        children=[                    
                            dcc.Graph(
                                id="daily-btc",
                                className="six columns card",
                                figure={
                                        'data': [] 
                                        }
                            )
                        ]
                    ),
                    html.Div(
                        className="six columns card",
                        children=[                   
                            dcc.Graph(
                                id="balance",
                                className="six columns card",
                                figure={
                                        'data': [] 
                                       }
                            )
                        ]
                    ),    
                ]
        ),       
    ])
])



@app.callback(
    dash.dependencies.Output('date-range', 'start_date'), # component with id date-range" will be changed, the 'start_date' argument is updated
    [
        dash.dependencies.Input('exchange-select', 'value') # component dependency: exchange-select
    ]
)

def update_exchange_min(value):
    return exchange_min_date(value)

@app.callback(
    dash.dependencies.Output('date-range', 'end_date'), # component with id date-range" will be changed, the 'end_date' argument is updated
    [
        dash.dependencies.Input('exchange-select', 'value') # component dependency: exchange-select
    ]
)

def update_exchange_max(value):
    return exchange_max_date(value)

@app.callback(
    [
        dash.dependencies.Output('monthly-chart', 'figure'),
        dash.dependencies.Output('market-returns', 'children'),  
        dash.dependencies.Output('strat-returns', 'children'),
        dash.dependencies.Output('strat-vs-market', 'children'),              
    ],
    (
        dash.dependencies.Input('exchange-select', 'value'),
        dash.dependencies.Input('leverage-select', 'value'),
        dash.dependencies.Input('date-range', 'start_date'),
        dash.dependencies.Input('date-range', 'end_date'),

    )
)
def update_monthly(exchange, leverage, start_date, end_date):
    dff = filter_df(df, exchange, leverage, start_date, end_date)
    #Create the :  YearMonth column for the Candlestick graphic
    #dff['YearMonth'] = pd.to_datetime(dff['Entry time'], format='%Y%m')
    dff['YearMonth'] = dff['Entry time'].dt.year.astype(str) + '-' + dff['Entry time'].dt.month.astype(str)
    data = calc_returns_over_month(dff)

    btc_returns = calc_btc_returns(dff)
    strat_returns = calc_strat_returns(dff)
    strat_vs_market = strat_returns - btc_returns

    return {
        'data': [
            go.Candlestick(
                open=[each['entry'] for each in data],
                close=[each['exit'] for each in data],
                x=[each['month'] for each in data],
                low=[each['entry'] for each in data],
                high=[each['exit'] for each in data]
            )
        ],
        'layout': {
            'title': 'Overview of Monthly performance'
        }
    }, f'{btc_returns:0.2f}%', f'{strat_returns:0.2f}%', f'{strat_vs_market:0.2f}%'


@app.callback(
    dash.dependencies.Output('table', 'data'),
    (
        dash.dependencies.Input('exchange-select', 'value'),
        dash.dependencies.Input('leverage-select', 'value'),
        dash.dependencies.Input('date-range', 'start_date'),
        dash.dependencies.Input('date-range', 'end_date'),
    )
)
def update_table(exchange, leverage, start_date, end_date):
    dff = filter_df(df, exchange, leverage, start_date, end_date)
    return dff.to_dict('records')


@app.callback(
    dash.dependencies.Output('pnl-types', 'figure'),
    [
        dash.dependencies.Input('exchange-select', 'value'),
        dash.dependencies.Input('leverage-select', 'value'),
        dash.dependencies.Input('date-range', 'start_date'),
        dash.dependencies.Input('date-range', 'end_date'),
    ]
)
def update_bar_plot(exchange, leverage, start_date, end_date):
    return { 
        'data': 
        pnl_vs_trade_type(exchange, leverage, start_date, end_date),
        'layout': {
            'title': {
                'text': 'PnL vs Trade type',
            }
        }
    }  


@app.callback(
    dash.dependencies.Output('daily-btc', 'figure'),
    [
        dash.dependencies.Input('exchange-select', 'value'),
        dash.dependencies.Input('leverage-select', 'value'),
        dash.dependencies.Input('date-range', 'start_date'),
        dash.dependencies.Input('date-range', 'end_date'),
    ]
)
def update_line_plot_daily_btc(exchange, leverage, start_date, end_date):
    return { 
        'data': 
        daily_btc_plot(exchange, leverage, start_date, end_date),
        'layout': {
            'title': {
                'text': 'Daily BTC Price',
            },
            'height': 500, 
            'width': 500
        }
    } 


@app.callback(
    dash.dependencies.Output('balance', 'figure'),
    [
        dash.dependencies.Input('exchange-select', 'value'),
        dash.dependencies.Input('leverage-select', 'value'),
        dash.dependencies.Input('date-range', 'start_date'),
        dash.dependencies.Input('date-range', 'end_date'),
    ]
)
def update_line_plot_balance(exchange, leverage, start_date, end_date):
    return { 
        'data': 
        balance_plot(exchange, leverage, start_date, end_date),
        'layout': {
            'title': {
                'text': 'Balance overtime',
            },
            'height': 500,
            'width': 500
        }
    }



if __name__ == "__main__":
    app.run_server(debug=True)