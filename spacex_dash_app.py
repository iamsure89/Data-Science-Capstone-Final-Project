# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()
list_sites = spacex_df['Launch Site'].unique().tolist()
options = [{'label':'All Sites','value':'All'}]
for site in list_sites:
    options.append({'label':site,'value':site})

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(id='site-dropdown',
                                options=options, 
                                value='All',
                                placeholder='Select a launch site here',
                                searchable=True),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',min=0,max=10000,step=1000,
                                value=[min_payload,max_payload]),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output('success-pie-chart','figure'),
    Input('site-dropdown','value')
)
def get_pie_chart(entered_site):
    if entered_site == 'All':
        complete_df = spacex_df[['Launch Site','class']].groupby(['Launch Site']).sum().reset_index()
        complete_df.columns = ['Launch Site','Success']
        fig = px.pie(complete_df,values='Success',names='Launch Site',title='Total successful launches by launch site')
        return fig
    else:
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        filtered_df = filtered_df[['class','Launch Site']].groupby(['class']).count().reset_index()
        filtered_df.columns = ['class','count']
        fig = px.pie(filtered_df,values='count',names='class',title='Total successful launches at Launch Site:{}'.format(entered_site))
        return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output('success-payload-scatter-chart','figure'),
    Input('site-dropdown','value'),
    Input('payload-slider','value')
)
def get_scatter_plot(entered_site,selected_range):
    df_selected_range = spacex_df[spacex_df['Payload Mass (kg)'].between(selected_range[0],selected_range[1],inclusive='both')]
    if entered_site == 'All':
        fig = px.scatter(df_selected_range,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title='Correlation between Payload Mass and Success for All Sites')
        fig.update_yaxes(tickvals=[0,1])
        return fig
    else:
        filtered_df = df_selected_range[df_selected_range['Launch Site'] == entered_site]
        fig = px.scatter(filtered_df,
        x='Payload Mass (kg)',
        y='class',
        color='Booster Version Category',
        title='Correlation between Payload Mass and Success for {}'.format(entered_site)
        )
        fig.update_yaxes(tickvals=[0,1])
        return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
