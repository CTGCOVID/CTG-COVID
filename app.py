import pandas as pd
import json
import os
from datetime import date
from datetime import timedelta



########################################################################################################################################
#Import all FIPS Information
########################################################################################################################################
FIPSurl = 'https://raw.githubusercontent.com/CSSEGISandData/COVID-19/master/csse_covid_19_data/UID_ISO_FIPS_LookUp_Table.csv'
FIPS_pd = pd.read_csv(FIPSurl, error_bad_lines=False)
FIPS_pd = FIPS_pd.drop(['UID', 'iso2', 'iso3', 'code3', 'Country_Region','Lat', 'Long_'],axis=1).dropna(subset=['FIPS'])
FIPS_pd = FIPS_pd[FIPS_pd['FIPS']>1000]
FIPS_pd = FIPS_pd[FIPS_pd['FIPS']<60000].reset_index(drop = True)
FIPS_pd['Combined_Key'] = [x[:-4] for x in FIPS_pd['Combined_Key']] 
Total_pd = FIPS_pd
#display(FIPS_pd)
########################################################################################################################################




########################################################################################################################################
#Import COVID Data
########################################################################################################################################
i=62

os.chdir(r'C:\Users\borde\Desktop\COVID\Daily County Reports')

while i>0:
    badDate = date(2020,5,28)
    day1 = date.today() - timedelta(days=i)
    d1 = day1.strftime("%m-%d-%Y")
    day2 = day1 - timedelta(days=14)
    d2 = day2.strftime("%m-%d-%Y")
    
    COVID1_pd = pd.read_csv(str(d1) + '.csv')
    if day1 <= badDate:
        COVID1_pd = COVID1_pd.drop(['Admin2', 'Province_State', 'Country_Region', 'Last_Update', 'Confirmed','Lat', 'Long_', 'Deaths', 'Recovered', 'Combined_Key'],axis=1).dropna(subset=['FIPS'])    
    else:
        COVID1_pd = COVID1_pd.drop(['Admin2', 'Province_State', 'Country_Region', 'Last_Update', 'Confirmed','Lat', 'Long_', 'Deaths', 'Recovered', 'Combined_Key', 'Incidence_Rate', 'Case-Fatality_Ratio'],axis=1).dropna(subset=['FIPS'])
    COVID1_pd = COVID1_pd[COVID1_pd['FIPS']>1000]
    COVID1_pd = COVID1_pd[COVID1_pd['FIPS']<60000].reset_index(drop = True)
    COVID1_pd = COVID1_pd.rename(columns={'Active' : 'Total'})

    COVID2_pd = pd.read_csv(str(d2) + '.csv')
    if day2 <= badDate:
        COVID2_pd = COVID2_pd.drop(['Admin2', 'Province_State', 'Country_Region', 'Last_Update', 'Confirmed','Lat', 'Long_', 'Deaths', 'Recovered', 'Combined_Key'],axis=1).dropna(subset=['FIPS'])
    else:
        COVID2_pd = COVID2_pd.drop(['Admin2', 'Province_State', 'Country_Region', 'Last_Update', 'Confirmed','Lat', 'Long_', 'Deaths', 'Recovered', 'Combined_Key', 'Incidence_Rate', 'Case-Fatality_Ratio'],axis=1).dropna(subset=['FIPS'])
    COVID2_pd = COVID2_pd[COVID2_pd['FIPS']>1000]
    COVID2_pd = COVID2_pd[COVID2_pd['FIPS']<60000].reset_index(drop = True)
    COVID2_pd = COVID2_pd.rename(columns={'Active' : 'Total14'})

    combined_pd = COVID1_pd.merge(COVID2_pd, on='FIPS',how='left').fillna(0)
    total_pd = combined_pd.drop(['Total14'], axis=1)
    combined_pd['Active'] = (combined_pd['Total'] - combined_pd['Total14']).abs()
    combined_pd = combined_pd.drop(['Total', 'Total14'],axis=1)
    total_pd = total_pd.sort_values(['FIPS']).reset_index(drop=True)
    total_pd = total_pd.rename(columns={'Total':str(d1)})
    combined_pd = combined_pd.sort_values(['FIPS']).reset_index(drop=True)
    combined_pd = combined_pd.rename(columns={'Active' : str(d1)})

    Total_pd = Total_pd.merge(total_pd, on='FIPS',how='left').fillna(0)
    FIPS_pd = FIPS_pd.merge(combined_pd, on='FIPS',how='left').fillna(0)
    i -= 1

strFIPS = []

FIPS_pd['FIPS'] = FIPS_pd['FIPS'].astype('int64', copy=True)
Total_pd['FIPS'] = Total_pd['FIPS'].astype('int64', copy=True)
Total_pd = Total_pd.drop(['Population', 'Combined_Key'],axis=1)

for x in range(0,len(FIPS_pd)):
    strFIPS.append(str(FIPS_pd['FIPS'][x]).rjust(5,'0'))
FIPS_pd['FIPS'] = strFIPS
Total_pd['FIPS'] = strFIPS


FIPS_pd = FIPS_pd.fillna(0)    
FIPS_pd['Incidence_Rate'] = FIPS_pd[str(d1)]/FIPS_pd['Population']*100000
mean = FIPS_pd['Incidence_Rate'].mean()
std = FIPS_pd['Incidence_Rate'].std()

########################################################################################################################################





########################################################################################################################################
#Graph County Map
########################################################################################################################################
import plotly.express as px

risk = []

for x in range(0,len(FIPS_pd)):
    if (FIPS_pd['Incidence_Rate'][x] < mean+std):
        risk.append("LOW")
    elif (FIPS_pd['Incidence_Rate'][x] >= mean+std) and (FIPS_pd['Incidence_Rate'][x] < mean+2*std):
        risk.append("MEDIUM")
    elif (FIPS_pd['Incidence_Rate'][x] >= mean+std*2):
        risk.append("HIGH")
    else:
        risk.append("ERROR")

FIPS_pd['Risk'] = risk
        
colorscale = ["#CCFFCC","#00FF00","#99FF00","#CCFF00","#FFFF00","#FFCC00","#FF6600","#FF0000"]

fig = px.choropleth(FIPS_pd, geojson=counties, locations='FIPS', color= 'Incidence_Rate',
                    color_continuous_scale=colorscale,
                    range_color=(0, mean+std*2), 
                    scope="usa", title='Active Incidence Rate per County', hover_name = "Combined_Key", hover_data=['Risk', str(d1)])


fig.update_traces(marker_line_width=.3, marker_opacity=.8,hovertemplate='<b>%{hovertext}</b><br>Risk: %{customdata[0]}<br><br>Incidence Rate: %{z}<br>Active Cases: %{customdata[1]}<extra></extra>')
fig.update_layout(height=700, legend = dict(x=0.8),title_x = 0.4, font={"size":20, "color":"white"},geo=dict(bgcolor='#323130', lakecolor='#323130', subunitcolor='black'), plot_bgcolor='#111110', paper_bgcolor='#111110')
fig.update_geos(showsubunits=True, subunitcolor='black')
########################################################################################################################################






########################################################################################################################################
#Add State daily data
########################################################################################################################################
States_pd = FIPS_pd.drop(['Admin2', 'FIPS', 'Combined_Key', 'Incidence_Rate', 'Risk'],axis=1)
States_pd = States_pd.groupby(['Province_State'], as_index=False).sum()
States_pd['Incidence_Rate'] = States_pd[str(d1)]/States_pd['Population']*100000
States_pd['Admin2'] = 'All'
States_pd['Combined_Key'] = States_pd['Admin2'] + ', ' + States_pd['Province_State']
StateTotal_pd = Total_pd.drop(['Admin2', 'FIPS'],axis=1)
StateTotal_pd = StateTotal_pd.groupby(['Province_State'], as_index=False).sum()
StateTotal_pd['Admin2'] = 'All'

risk = []
    
for x in range(0,len(States_pd)):
    if (States_pd['Incidence_Rate'][x] < mean+std):
        risk.append("LOW")
    elif (States_pd['Incidence_Rate'][x] >= mean+std) and (States_pd['Incidence_Rate'][x] < mean+2*std):
        risk.append("MEDIUM")
    elif (States_pd['Incidence_Rate'][x] >= mean+std*2):
        risk.append("HIGH")
    else:
        risk.append("ERROR")

States_pd['Risk'] = risk
States_pd['FIPS'] = 'NaN'

CombinedFIPS_pd = pd.concat([FIPS_pd, States_pd], sort = False).reset_index(drop = True)
CombinedTotal_pd = pd.concat([Total_pd, StateTotal_pd], sort=False).reset_index(drop=True)
#######################################################################################################################################





#######################################################################################################################################
#Create DOD State Map
#######################################################################################################################################
States_pd['DOD_Rank'] = 'green'
States_pd.loc[States_pd['Province_State'] == 'Florida','DOD_Rank'] = 'red'
state_codes = {
    'District of Columbia' : 'dc','Mississippi': 'MS', 'Oklahoma': 'OK', 
    'Delaware': 'DE', 'Minnesota': 'MN', 'Illinois': 'IL', 'Arkansas': 'AR', 
    'New Mexico': 'NM', 'Indiana': 'IN', 'Maryland': 'MD', 'Louisiana': 'LA', 
    'Idaho': 'ID', 'Wyoming': 'WY', 'Tennessee': 'TN', 'Arizona': 'AZ', 
    'Iowa': 'IA', 'Michigan': 'MI', 'Kansas': 'KS', 'Utah': 'UT', 
    'Virginia': 'VA', 'Oregon': 'OR', 'Connecticut': 'CT', 'Montana': 'MT', 
    'California': 'CA', 'Massachusetts': 'MA', 'West Virginia': 'WV', 
    'South Carolina': 'SC', 'New Hampshire': 'NH', 'Wisconsin': 'WI',
    'Vermont': 'VT', 'Georgia': 'GA', 'North Dakota': 'ND', 
    'Pennsylvania': 'PA', 'Florida': 'FL', 'Alaska': 'AK', 'Kentucky': 'KY', 
    'Hawaii': 'HI', 'Nebraska': 'NE', 'Missouri': 'MO', 'Ohio': 'OH', 
    'Alabama': 'AL', 'Rhode Island': 'RI', 'South Dakota': 'SD', 
    'Colorado': 'CO', 'New Jersey': 'NJ', 'Washington': 'WA', 
    'North Carolina': 'NC', 'New York': 'NY', 'Texas': 'TX', 
    'Nevada': 'NV', 'Maine': 'ME'}

States_pd['State_Code'] = States_pd['Province_State'].apply(lambda x : state_codes[x])

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
