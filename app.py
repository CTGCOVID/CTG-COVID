from urllib.request import urlopen
import pandas as pd
import json
with urlopen('https://raw.githubusercontent.com/plotly/datasets/master/geojson-counties-fips.json') as response:
    counties = json.load(response)
import os
from datetime import date
from datetime import timedelta
import plotly.express as px


FIPS_pd = pd.read_csv('https://raw.githubusercontent.com/CTGCOVID/CTG-COVID/master/FIPS.csv')
States_pd = pd.read_csv('https://raw.githubusercontent.com/CTGCOVID/CTG-COVID/master/States.csv')
CombinedFIPS_pd = pd.read_csv('https://raw.githubusercontent.com/CTGCOVID/CTG-COVID/master/CombinedFIPS.csv')
CombinedTotal_pd = pd.read_csv('https://raw.githubusercontent.com/CTGCOVID/CTG-COVID/master/CombinedTotal.csv')

FIPS_pd['FIPS'] = FIPS_pd['FIPS'].astype('int64', copy=True)

strFIPS=[]

for x in range(0,len(FIPS_pd)):
    strFIPS.append(str(FIPS_pd['FIPS'][x]).rjust(5,'0'))
FIPS_pd['FIPS'] = strFIPS


mean = FIPS_pd['Incidence_Rate'].mean()
std = FIPS_pd['Incidence_Rate'].std()

colorscale = ["#CCFFCC","#00FF00","#99FF00","#CCFF00","#FFFF00","#FFCC00","#FF6600","#FF0000"]

fig = px.choropleth(FIPS_pd, geojson=counties, locations='FIPS', color= 'Incidence_Rate',
                    color_continuous_scale=colorscale,
                    range_color=(0, mean+std*2), 
                    scope="usa", title='Active Incidence Rate per County', hover_name = "Combined_Key", hover_data=['Risk'])


fig.update_traces(marker_line_width=.3, marker_opacity=.8,hovertemplate='<b>%{hovertext}</b><br>Risk: %{customdata[0]}<br><br>Incidence Rate: %{z}<br>Active Cases: %{customdata[1]}<extra></extra>')
fig.update_layout(height=700, legend = dict(x=0.8),title_x = 0.4, font={"size":20, "color":"white"},geo=dict(bgcolor='#323130', lakecolor='#323130', subunitcolor='black'), plot_bgcolor='#111110', paper_bgcolor='#111110')
fig.update_geos(showsubunits=True, subunitcolor='black')

fig2 = px.choropleth(States_pd, locations='State_Code', color= 'DOD_Rank',
                    scope = "usa",hover_name = "Province_State", locationmode='USA-states', color_discrete_sequence = ['#4CBB17','red'], title='DOD State Rankings')

fig2.update_layout(height=700, legend = dict(x=0.8),title_x = 0.4, font={"size":20, "color":"white"},geo=dict(bgcolor='#323130', lakecolor='#323130', 
                    subunitcolor='black'), plot_bgcolor='#111110', paper_bgcolor='#111110')
########################################################################################################################################





import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import math

states = States_pd['Province_State'].unique()
states.sort()
counties = CombinedFIPS_pd['Admin2'].unique()
counties.sort()

app = dash.Dash(__name__)

##APP LAYOUT
app.layout = html.Div([
    html.Div([
        html.Div([
            dcc.Graph(id = 'g1',figure=fig),
        ],className='ten columns', style={'width':'60%'}),
        html.Div([
            dcc.Graph(id='g2',figure=fig2),
        ],className='two columns', style={'width':'40%'}),
    ],className='row', style={'display':'flex'}),
    
    html.Br(),
    html.Br(),
    html.Div([
        html.Div([
            html.Div(children='State: '),
            dcc.Dropdown(id = 'state_dropdown', options=[{'label' : s, 'value' : s} for s in states], value='Florida', style={'height':'50px', 'width':'90%', 'font-size':'120%'}),
            html.Div(children='County: ',style={'font-color':'white'}),
            dcc.Dropdown(id = 'county_dropdown', options=[{'label' : c, 'value' : c} for c in counties], value='All', style={'height':'50px', 'width':'90%', 'font-size':'120%'}),
            html.Br(),
            html.Br(),
            dcc.Graph(id='riskgraph'),
        ],className='four columns', style={'width':'50%'}),
        html.Br(),
        html.Div([
            html.Div(children=html.Div(id='graphs'),className='row'),
        ],className='eight columns', style={'width':'50%'}),
    ],className='row', style={'display':'flex'}),
    
    dcc.Interval(
        id='graph-update',
        interval = 100),
    ], className='container', style={'backgroundColor':'#111110'})


@app.callback(
    Output(component_id='graphs', component_property='children'),
    [Input(component_id='state_dropdown', component_property='value'), Input(component_id='county_dropdown', component_property='value')]
)
def graph_active(state_slctd, county_slctd):
    graphs=[]
    class_choice = 'col s12, m12 l6'
    
    local = CombinedFIPS_pd.copy()
    local = local[local["Admin2"]=='Okaloosa'].reset_index(drop=True)
    total = CombinedTotal_pd.copy()
    total = total[total['Province_State']== state_slctd]
    total = total[total['Admin2']==county_slctd]
    total = total.reset_index(drop=True)
    dff = CombinedFIPS_pd.copy()
    dff = dff[dff["Province_State"] == state_slctd]
    dff = dff[dff["Admin2"] == county_slctd]
    dff = dff.reset_index(drop=True)

    x=[]
    y=[]
    z=[]
    z2 = []
    z3=[]
    i=61

    while i > 0:
        day = date.today() - timedelta(days=i)
        di = day.strftime("%m-%d-%Y")
        day2 = date.today() - timedelta(days=(i+1))
        di2 = day2.strftime("%m-%d-%Y")
        x.append(di)
        y.append(dff[di][0])
        z.append(dff[di][0]/dff['Population'][0]*100000)
        z2.append(local[di][0]/local['Population'][0]*100000)
        difference = abs(total[di][0]-total[di2][0])
        z3.append(difference)
        i-=1
    
    fig3 = px.bar(x=x, y=y, title='Active Cases')
    fig3.update_traces(marker_color='#00ff00')
    fig3.update_xaxes(showline=True, linecolor='white', title_text='Date')
    fig3.update_yaxes(showline=True, linecolor='white', title_text='Active Cases')
    fig3.update_layout(height=300,yaxis_showgrid=False, xaxis_tickangle = -45, title_x = 0.4, font={"size":15, "color":"gray"}, plot_bgcolor='#111110', paper_bgcolor='#111110', title_font_color='white')
    
    graphs.append(html.Div(dcc.Graph(
        id='Active_Graph', 
        figure=fig3)))
    
    LineData = pd.DataFrame(list(zip(x,z,z2)), columns = ['Dates', county_slctd, 'Local']) 
    
    fig4 = px.line(LineData, x='Dates', y=[county_slctd, 'Local'], title='Incidence Rate')
    fig4.update_xaxes(title_text='Date')
    fig4.update_yaxes(showline=True, linecolor='white', title_text='Active Cases')
    fig4.update_layout(height=300,yaxis_showgrid=False, xaxis_showgrid=False, xaxis_tickangle = -45, title_x = 0.4, font={"size":15, "color":"gray"}, plot_bgcolor='#111110', paper_bgcolor='#111110', title_font_color='white')
    
    graphs.append(html.Div(dcc.Graph(
        id='IR_Graph', 
        figure=fig4)))
    
    fig5 = px.bar(x=x, y=z3, title='New Cases')
    fig5.update_traces(marker_color='#00ff00')
    fig5.update_xaxes(showline=True, linecolor='white', title_text='Date')
    fig5.update_yaxes(showline=True, linecolor='white', title_text='New Cases')
    fig5.update_layout(height=300,yaxis_showgrid=False, xaxis_tickangle = -45, title_x = 0.4, font={"size":15, "color":"gray"}, plot_bgcolor='#111110', paper_bgcolor='#111110', title_font_color='white')
    
    graphs.append(html.Div(dcc.Graph(
        id='New_Graph', 
        figure=fig5)))
    
    return graphs



@app.callback(
    Output(component_id='riskgraph', component_property='figure'),
    [Input(component_id='state_dropdown', component_property='value'), Input(component_id='county_dropdown', component_property='value')]
)
def graph_risk(state_slctd, county_slctd):
    
    x_vals=[mean-std*3]
    y_vals=[]
    ranges=[]
    
    point = CombinedFIPS_pd.copy()
    point = point[point["Province_State"] == state_slctd]
    point = point[point["Admin2"] == county_slctd]
    point = point.reset_index(drop=True)
 
    
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

    fig6 = px.area(Curve, x='X', y='Y', title = 'Risk Level', color='Range', color_discrete_sequence=['#C0C0C0', '#00FF00', '#FFFF00', '#FF0000'])
    fig6.update_traces(marker_color='#00ff00')
    fig6.update_xaxes(showline=True, linecolor='white', title_text='Date')
    fig6.update_yaxes(showline=True, linecolor='white', title_text='New Cases')
    fig6.update_layout(annotations=[dict(x=point['Incidence_Rate'][0], y=0, showarrow=True, arrowhead=2, arrowwidth=3, arrowcolor='white', ax = 0, ay = -80, )], height=500,yaxis_showgrid=False, xaxis_showgrid=False, xaxis_tickangle = -45, title_x = 0.4, font={"size":15, "color":"gray"}, plot_bgcolor='#111110', paper_bgcolor='#111110', title_font_color='white')
    
    return fig6

if __name__ == '__main__':
    app.run_server(debug=False)
# ------------------------------------------------------------------------------
