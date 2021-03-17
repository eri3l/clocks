import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from os import walk
import plotly.graph_objs as go


#--------- prepare files
path = 'dat/'

f = []
for (dirpath, dirnames, filenames) in walk(path):
    f.extend(filenames)

    
# read file, rename and set column names
# note: alternatively, you can add all the files to a dictionary while reading them in the below loop.
dataframes = []
for filename in filenames:
    dataframes.append(pd.read_csv(path+filename, sep=" ", header = None))
    df = dataframes[-1]
    if filename.endswith('.clockroom'):
        df.name = filename[4:-10]
    else:
        print("Sorry, haven't written code for extensions other than .clockroom")
    df.columns = ['Time', 'Measurement']
    
# create a dictionary, where key - file name, value - corresponding dataframe
f_names_list = []
for df in dataframes:
    f_names_list.append(df.name)

data_dict = dict(zip(f_names_list, dataframes))

#---------- HTML onwards:

#---- external stylesheets:
external_css = ["https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/css/materialize.min.css"]
external_js = ['https://cdnjs.cloudflare.com/ajax/libs/materialize/1.0.0/js/materialize.min.js']
app = dash.Dash('clock-data',
                external_scripts=external_js,
                external_stylesheets=external_css)
#---- external stylesheets end

#---- app layout:
app.layout = html.Div([
    html.Div([
        html.H2('Clock Data',
                style={'float': 'left',
                       }),
        ]),
    dcc.Dropdown(id='clock-data-name',
                 options=[{'label': s, 'value': s}
                          for s in data_dict.keys()],
                 value=['Cs2869', 'Cs3396','Cs3872' ], # this value gets passed in to make_graphs()
                 multi=True,
                 placeholder = "Select a COCK"
                 ),
    html.Div(children=html.Div(id='graphs'), className='row'),
    dcc.Interval(
        id='graph-update',
        interval=100000, # interval to auto-update in milliseconds
        n_intervals=0),
    ], className="container",style={'width':'98%','margin-left':10,'margin-right':10,'max-width':50000})
#---- app layout end

#---- @app.callback
@app.callback(
    dash.dependencies.Output('graphs','children'),
    [dash.dependencies.Input('clock-data-name', 'value'),
     dash.dependencies.Input('graph-update', 'n_intervals')],
    )
#---- @app.callback end

#--- loop through dfs and make graphs
# Note: data_names gets passed in via dash.dependencies.Input() and is the value set in dcc.Dropdown()
def make_graphs(data_names, n):
    graphs = []
    
    # set size and placement of graphs, double-check this because they don't display too well at the moment
    if len(data_names)>2:
        class_choice = 'col s12 m6 l4'
    elif len(data_names) == 2:
        class_choice = 'col s12 m6 l6'
    else:
        class_choice = 'col s12'

    # loop through data_names and create graphs. 
    # TODO, FIXME: this might throw a warning "plotly.graph_objs.Line is deprecated"
    for dn in data_names:
        graphs.append(html.Div(dcc.Graph(
            id=data_dict[dn].name,
            figure={'data': [go.Line(x=data_dict[dn][data_dict[dn].columns[0]], y=data_dict[dn][data_dict[dn].columns[1]])],
                    'layout': go.Layout(margin={'l': 80, 'r': 80, 't': 100, 'b': 80, 'pad': 0},
                                        xaxis_tickformat='d',
                                        xaxis_title='MJD',
                                        yaxis_title='UTC(MSL)-{}'.format(data_dict[dn].name),
                                        title='<b>{}</b>'.format(data_dict[dn].name))
                    }
        ), className=class_choice))


    return graphs
#------------   

if __name__ == '__main__':
    app.run_server(debug=True)
