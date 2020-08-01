from urllib.request import urlopen
import pandas as pd
import json
with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)
import os
import plotly.express as px
from datetime import datetime
from datetime import date
from datetime import timedelta
import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
from statistics import mean
from statistics import stdev
import math

url = 'https://usafactsstatic.blob.core.windows.net/public/data/covid-19/covid_confirmed_usafacts.csv'
popUrl = 'https://usafactsstatic.blob.core.windows.net/public/data/covid-19/covid_county_population_usafacts.csv'
deathUrl = 'https://usafactsstatic.blob.core.windows.net/public/data/covid-19/covid_deaths_usafacts.csv'

confirmed_pd = pd.read_csv(url, index_col=False)
population_pd = pd.read_csv(popUrl, index_col=False)
deaths_pd = pd.read_csv(deathUrl, index_col=False)
confirmed_pd.columns = confirmed_pd.columns.astype(str)
deaths_pd.columns = deaths_pd.columns.astype(str)

columns = confirmed_pd.columns

confirmed_pd['Population'] = population_pd['population']
deaths_pd['Population'] = population_pd['population']

confirmed_pd = confirmed_pd[confirmed_pd['Population']!=0].reset_index(drop=True)
deaths_pd = deaths_pd[deaths_pd['Population']!=0].reset_index(drop=True)

y_vals=[]
ranges=[]

sunday = datetime.strptime(columns[-1],'%m/%d/%y').date()
day = sunday.weekday()
gap = 1

while(day != 6):
    gap += 1
    sunday = sunday - timedelta(days=1)
    day = sunday.weekday()

TE = columns[-gap]
TS = columns[-(gap+7)]
LE = TS
LS = columns[-(gap+14)]

risk = []
graphIR = []

for x in range(0,len(confirmed_pd)):
    graphIR.append((confirmed_pd[TE][x]-confirmed_pd[TS][x])/confirmed_pd['Population'][x]*100000)
    
mean = mean(graphIR)
std = stdev(graphIR)
x_vals=[mean-std*3]

for x in range(1,61):
    x_vals.append(x_vals[x-1]+std/10)

for x in range(0,len(x_vals)):
    y_vals.append((1/(std*math.sqrt(2*math.pi)))*math.exp(-1/2*((x_vals[x]-mean)/(std))**2))

for x in range(0,len(x_vals)):
    if x_vals[x]<0:
        ranges.append('Out')
    elif x<40:
        ranges.append('Low')
    elif x>=40 and x<51:
        ranges.append('Medium')
    else:
        ranges.append('High')

Curve = pd.DataFrame(list(zip(x_vals, y_vals, ranges)), columns = ['X', 'Y', 'Range']) 
   
########################################################################################################################################



########################################################################################################################################
#Import COVID DataZ
########################################################################################################################################


########################################################################################################################################


states = confirmed_pd['State'].unique()
states.sort()
counties = confirmed_pd['County Name'].unique()
counties.sort()





States_pd = pd.DataFrame(list(zip(states)), columns = ['State'])
States_pd['Color'] = 'Green'
States_pd.loc[States_pd['State'] == 'FL','Color'] = 'Red'
    
fig2 = px.choropleth(States_pd, locations='State', color= 'Color',
            scope = "usa",hover_name = "State", locationmode='USA-states', color_discrete_sequence = ['#4CBB17','red'], title='DOD State Rankings')

fig2.update_layout(height=700, legend = dict(x=0.8),title_x = 0.4, font={"size":20, "color":"white"},geo=dict(bgcolor='#323130', lakecolor='#323130', 
                subunitcolor='black'), plot_bgcolor='#111110', paper_bgcolor='#111110')




app = dash.Dash(__name__)
server=app.server

##APP LAYOUT
app.layout = html.Div([
    html.Div([
        html.Div([
            html.Div(children='State: '),
            dcc.Dropdown(id = 'state_dropdown', options=[{'label' : s, 'value' : s} for s in states], value='FL', style={'height':'50px', 'width':'90%', 'font-size':'120%'}),
            html.Div(children='County: ',style={'font-color':'white'}),
            dcc.Dropdown(id = 'county_dropdown', options=[{'label' : c, 'value' : c} for c in counties], value='Okaloosa County', style={'height':'50px', 'width':'90%', 'font-size':'120%'}),
            html.Br(),
            dcc.Graph(id='riskgraph'),
            dcc.Graph(id='totalgraph'),
        ],className='four columns', style={'width':'50%'}),
        html.Br(),
        html.Div([
            dcc.Graph(id='activegraph'),
            dcc.Graph(id='IRgraph'),
            dcc.Graph(id='newgraph'),
        ],className='eight columns', style={'width':'50%'}),
    ],className='row', style={'display':'flex'}),
    
    dcc.Interval(
        id='graph-update',
        interval = 100),
    ], className='container', style={'backgroundColor':'#111110'})


@app.callback(
    Output(component_id='activegraph', component_property='figure'),
    [Input(component_id='state_dropdown', component_property='value'), Input(component_id='county_dropdown', component_property='value')]
)
def graph_active(state_slctd, county_slctd):
    dff = confirmed_pd.copy()
    dff = dff[dff["State"] == state_slctd]
    dff = dff[dff["County Name"] == county_slctd]
    dff = dff.reset_index(drop=True)

    x=[]
    y=[]

    i=60
    while i>0:
        d1 = columns[-i]
        d2 = columns[-(i+14)]

        x.append(d1)
        y.append(dff[d1][0] - dff[d2][0])
        i -= 1

    fig3 = px.bar(x=x, y=y, title='Active Cases')
    fig3.update_traces(marker_color='#00ff00')
    fig3.update_xaxes(showline=True, linecolor='white', title_text='Date')
    fig3.update_yaxes(showline=True, linecolor='white', title_text='Active Cases')
    fig3.update_layout(height=300,yaxis_showgrid=False, xaxis_tickangle = -45, title_x = 0.4, font={"size":15, "color":"gray"}, plot_bgcolor='#111110', paper_bgcolor='#111110', title_font_color='white')

    return fig3


@app.callback(
    Output(component_id='IRgraph', component_property='figure'),
    [Input(component_id='state_dropdown', component_property='value'), Input(component_id='county_dropdown', component_property='value')]
)
def graph_IR(state_slctd, county_slctd):
    local = confirmed_pd.copy()
    local = local[local["State"]=='FL']
    local1 = local[local["County Name"]=='Okaloosa County'].reset_index(drop=True)
    local2 = local[local["County Name"]=='Walton County'].reset_index(drop=True)
    local3 = local[local["County Name"]=='Santa Rosa County'].reset_index(drop=True)
    dff = confirmed_pd.copy()
    dff = dff[dff["State"] == state_slctd]
    dff = dff[dff["County Name"] == county_slctd].reset_index(drop=True)

    localPop = local1['Population'][0] + local2['Population'][0] + local3['Population'][0]

    x=[]
    y=[]
    z=[]

    i=60
    while i>0:
        d1 = columns[-i]
        d2 = columns[-(i+14)]

        x.append(d1)
        localsum = local1[d1][0] + local2[d1][0] + local3[d1][0]
        local14sum = local1[d2][0] + local2[d2][0] + local3[d2][0]
        y.append((localsum - local14sum)/localPop*100000)
        z.append((dff[d1][0] - dff[d2][0])/dff['Population'][0]*100000)
        i -= 1

    LineData = pd.DataFrame(list(zip(x,z,y)), columns = ['Dates', county_slctd, 'Local']) 
    
    fig4 = px.line(LineData, x='Dates', y=[county_slctd, 'Local'], title='Incidence Rate')
    fig4.update_xaxes(title_text='Date')
    fig4.update_yaxes(showline=True, linecolor='white', title_text='Active Cases')
    fig4.update_layout(height=300,yaxis_showgrid=False, xaxis_showgrid=False, xaxis_tickangle = -45, title_x = 0.4, font={"size":15, "color":"gray"}, plot_bgcolor='#111110', paper_bgcolor='#111110', title_font_color='white')
    
    return fig4


@app.callback(
    Output(component_id='newgraph', component_property='figure'),
    [Input(component_id='state_dropdown', component_property='value'), Input(component_id='county_dropdown', component_property='value')]
)
def graph_new(state_slctd, county_slctd):
    dff = confirmed_pd.copy()
    dff = dff[dff["State"] == state_slctd]
    dff = dff[dff["County Name"] == county_slctd]
    dff = dff.reset_index(drop=True)

    x=[]
    y=[]
    
    i=60
    while i>0:
        d1 = columns[-i]
        d2 = columns[-(i+1)]

        x.append(d1)
        y.append(dff[d1][0] - dff[d2][0])
        i -= 1
    
    fig5 = px.bar(x=x, y=y, title='New Cases')
    fig5.update_traces(marker_color='#00ff00')
    fig5.update_xaxes(showline=True, linecolor='white', title_text='Date')
    fig5.update_yaxes(showline=True, linecolor='white', title_text='New Cases')
    fig5.update_layout(height=300,yaxis_showgrid=False, xaxis_tickangle = -45, title_x = 0.4, font={"size":15, "color":"gray"}, plot_bgcolor='#111110', paper_bgcolor='#111110', title_font_color='white')
    
    return fig5


@app.callback(
    Output(component_id='riskgraph', component_property='figure'),
    [Input(component_id='state_dropdown', component_property='value'), Input(component_id='county_dropdown', component_property='value')]
)
def graph_new(state_slctd, county_slctd):
    point = confirmed_pd.copy()
    point = point[point["State"] == state_slctd]
    point = point[point["County Name"] == county_slctd]
    point = point.reset_index(drop=True)

    thisIR = (point[TE][0] - point[TS][0])/point['Population'][0]*100000
    lastIR = (point[LE][0] - point[LS][0])/point['Population'][0]*100000

    if thisIR > lastIR:
        highIR = thisIR
    else:
        highIR = lastIR
    
    fig6 = px.area(Curve, x='X', y='Y', title = 'Risk Level', color='Range', color_discrete_sequence=['#C0C0C0', '#00FF00', '#FFFF00', '#FF0000'])
    fig6.update_traces(marker_color='#00ff00')
    fig6.update_xaxes(showline=True, linecolor='white', title_text='Date')
    fig6.update_yaxes(showline=True, linecolor='white', title_text='New Cases')
    fig6.update_layout(annotations=[dict(x=highIR, y=0, showarrow=True, arrowhead=2, arrowwidth=3, arrowcolor='white', ax = 0, ay = -80, )], height=410,yaxis_showgrid=False, xaxis_showgrid=False, xaxis_tickangle = -45, title_x = 0.4, font={"size":15, "color":"gray"}, plot_bgcolor='#111110', paper_bgcolor='#111110', title_font_color='white')

    return fig6

@app.callback(
    Output(component_id='totalgraph', component_property='figure'),
    [Input(component_id='state_dropdown', component_property='value'), Input(component_id='county_dropdown', component_property='value')]
)
def graph_total(state_slctd, county_slctd):
    total = confirmed_pd.copy()
    total = total[total["State"] == state_slctd]
    total = total[total["County Name"] == county_slctd].reset_index(drop=True)
    deaths = deaths_pd.copy()
    deaths = deaths[deaths['State'] == state_slctd]
    deaths = deaths[deaths['County Name'] == county_slctd].reset_index(drop=True)

    x=[]
    y=[]
    z=[]
    z2=[]

    i=60
    while i>0:
        d1 = columns[-i]
        d2 = columns[-(i+14)]

        x.append(d1)
        y.append(total[d1][0])
        z.append(total[d1][0] - ((total[d1][0] - total[d2][0])/total['Population'][0]*100000) - deaths[d1][0])
        z2.append(deaths[d1][0])
        i -= 1

    LineData = pd.DataFrame(list(zip(x,y,z,z2)), columns = ['Dates', "Total", 'Recovered', 'Deaths']) 

    fig7 = px.line(LineData, x='Dates', y=['Total','Recovered','Deaths'], title='Total Cases', color_discrete_sequence = ['blue','green','red'])
    fig7.update_xaxes(title_text='Date')
    fig7.update_yaxes(showline=True, linecolor='white', title_text='Total Cases')
    fig7.update_layout(height=330,yaxis_showgrid=False, xaxis_showgrid=False, xaxis_tickangle = -45, title_x = 0.4, font={"size":15, "color":"gray"}, plot_bgcolor='#111110', paper_bgcolor='#111110', title_font_color='white')

    return fig7

if __name__ == '__main__':
    app.run_server(debug=False)
#------------------------------------------------------------------------------
