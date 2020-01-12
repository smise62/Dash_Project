# -*- coding: utf-8 -*-
"""
Created on Sun Jan 12 13:19:36 2020

@author: smise
"""

# -*- coding: utf-8 -*-
"""
Created on Fri Nov  8 15:06:59 2019

@author: smise
"""

import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input,Output,State
import plotly.graph_objs as go
import base64
import os
import pandas as pd
import numpy as np
import io
from dash.exceptions import PreventUpdate
import time
import socket

#host = socket.gethostbyname(socket.gethostname())
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
#app.css.append_css({“external_url”: “https://codepen.io/chriddyp/pen/brPBPO.css”})
connect_logo = 'logo.png'
encode_logo = base64.b64encode(open(connect_logo, 'rb').read()).decode('ascii')
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout=html.Div([html.Div(html.Img(src='data:logo/png;base64,{}'.format(encode_logo)),style={'textAlign':'center'}),
        html.H1("Upload Your CSV",style={'textAlign': 'center'}),
        dcc.Loading(id="loading-1", children=[html.Div(id="loading-output-1")], type="circle"),
        html.Div([dcc.Loading(id="loading-2",children=[html.Div(id="loading-output-2")])]),
        dcc.Upload(id='upload-file',children=html.Div(['Drag and Drop or', html.A(' Select Files')]),
                                              style={'width': '100%','height': '60px',
                                                     'lineHeight': '60px',
                                                     'borderWidth': '1px',
                                                     'borderStyle': 'dashed',
                                                     'borderRadius': '5px',
                                                     'textAlign': 'center',
                                                     'margin': '10px',
                                                     'color':'#111111'},
                                                     
                                                     multiple=False

                                            ),
                   
        html.Div(id='output-file-path'),
        html.Div(id='output-file'),
        html.H6("X-Axis",style={'width': '48%', 'display': 'inline-block'}),
        html.H6("Y-Axis",style={'width': '48%', 'textAlign': 'right', 'display': 'inline-block'}),
        html.Div([dcc.Dropdown(id='upload-columns1',  style={'width': '75%','height':'40px'},clearable=True,value='DateTime')],style={'width': '48%', 'height':'50px','display': 'inline-block'}),
        html.Div([dcc.Dropdown(id='upload-columns2',style={'width': '75%','float':'right','height':'40px'},clearable=True,value='TachographVehicleSpeed')],style={'width': '48%', 'height':'50px','float':'right','display': 'inline-block'}),
        
        html.Br(),
        html.Br(),
        html.Div([dcc.Graph(id='indicator-graphic',style={"paper_bgcolor": "rgba(0,0,0,0)","plot_bgcolor": "rgba(0,0,0,0)","background-color":"black"})]),
        html.Div(style={'width': '100%','height': '60px'}),
        html.H1("GPS Location",style={'textAlign': 'center'}),
        dcc.Graph(id='map'),
        html.Br(),
        html.Br()],style={'color':'#202020',})


def parse_contents(contents,filename):
    
    content_type, content_string = contents.split(",")
    decoded = base64.b64decode(content_string)
    #path=decoded.decode('utf-8')
    p=os.path.abspath(filename)
    #columns = pd.read_csv(io.StringIO(decoded.decode('utf-8')),nrows=0)
    df= pd.read_csv(io.StringIO(decoded.decode()),low_memory=False)
    if 'VIN' in df.columns:
        df.drop(columns=['VIN'],inplace=True)
    lst=df.columns
    lst=np.array(lst)
    lst.sort()
    df.to_csv(p)
    del df
    return lst,p



@app.callback([Output('upload-columns1','options'),Output('upload-columns2','options'),Output('output-file-path','children')],
              [Input('upload-file', 'contents')],
              [State('upload-file', 'filename')])
def update_output(content,filename):
    
    if content is None:
        raise PreventUpdate
    else:
        lst,path=parse_contents(content,filename)
        #lst.sort()
      
        return [{'label': i, 'value': i} for i in lst],[{'label': i, 'value': i} for i in lst],path


@app.callback(Output("loading-output-1", "children"), [Input("upload-file", "contents")],[State('upload-file', 'filename')])
def input_triggers_spinner(value,filename):
    time.sleep(3)
  

@app.callback(Output("loading-output-2", "children"), [Input("indicator-graphic", "figure")],)
def input_triggers_nested(value):
    time.sleep(3)


@app.callback(
    [Output('indicator-graphic', 'figure'),Output('output-file','children')],
    [Input('upload-columns1', 'value'),Input('upload-columns2', 'value'),Input('output-file-path', 'children')])
def update_graph(xaxis_column_name, yaxis_column_name,p):
    if p  is None:
        raise PreventUpdate
    else:
        path = p.replace('\\','/')   
    #df=get_dataframe(path,xaxis_column_name,yaxis_column_name)
        df=pd.read_csv(path,usecols=[xaxis_column_name,yaxis_column_name])
        
    
  
    return  {
                'data': [go.Scatter(
                        x=df[xaxis_column_name],
                        y=df[yaxis_column_name],
           
                    mode='markers',
                    marker={
                           'size': 5,
                      #      'opacity': 0.2,
                       #     'line': {'width': 0.5, 'color': 'white'}
                           }
                    )],
            'layout': go.Layout(
                    xaxis={
                            'title': xaxis_column_name,
                            #'size':18
                            #'color':'blue'
             
                },
                yaxis={
                        'title': yaxis_column_name,
                        #'size':18
                        #'color':'blue'
                
                },
                        margin={'l': 40, 'b': 40, 't': 10, 'r': 0},
                        hovermode='closest',
                        #paper_bgcolor='#000000',
                        #plot_bgcolor='#ffffff'
                
                        )
            },path
         
@app.callback(
    Output('map', 'figure'),
    [Input('output-file', 'children')])
def update_gmap(path):
     if path  is None:
        raise PreventUpdate
     else:
        path = path.replace('\\','/')   
    #df=get_dataframe(path,xaxis_column_name,yaxis_column_name)
        df=pd.read_csv(path,usecols=['Latitude','Longitude','DateTime'])
     df.reset_index(inplace=True)
     center_lat=df['Latitude'].mean()
     center_lon=df['Longitude'].mean()
        
     return {
            'data': [{ 
             'lat': df['Latitude'], 
             'lon': df['Longitude'],
             #'text1':df['Latitude'],
             #'text2':df['Longitude'],
             #'text3':df['DateTime'] ,
             'text':df['DateTime'] ,
             #'hoverinfo':'text',
             'hovertemmplate':"<b>%{'text'}</b><br>"+"Longitude: %{df.Longitude}<br>"+"Latitude:%{df.Latitude}",
             
             'marker': {
                'color': 'red',
                 'size': 12, 
                 'opacity': 0.6 
            },  
           
           'type': 'scattermapbox'
         }], 
                
        'layout': { 
             'mapbox': { 
                 'accesstoken': 'pk.eyJ1Ijoic21pc2UiLCJhIjoiY2swM2tlNnZ1MDAycTNubW53bG02b3YzbSJ9.WZWUbRf8xrK7Ar2nHE0D9w',
                 'zoom':5,
                 'center':{'lat':center_lat,'lon':center_lon}
                
             }, 
            'hovermode': 'closest',
            'autosize':True,
            'margin': {'l': 0, 'r': 0, 'b': 0, 't': 0},
            
            
            } 
        } 

if __name__ == '__main__':
    app.run_server(debug=False,port=8050)
    
