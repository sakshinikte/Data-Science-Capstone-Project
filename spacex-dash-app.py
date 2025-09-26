# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the spacex data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a list of launch sites for the dropdown options
launch_sites = spacex_df['Launch Site'].unique().tolist()
dropdown_options = [{'label': 'All Sites', 'value': 'ALL'}]
for site in launch_sites:
    dropdown_options.append({'label': site, 'value': site})

# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                dcc.Dropdown(id='site-dropdown',
                                             options=dropdown_options,
                                             value='ALL',
                                             placeholder="Select a Launch Site here",
                                             searchable=True
                                             ),
                                html.Br(),

                                # TASK 2: Add a pie chart
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):", style={'textAlign': 'left'}),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                                min=0, max=10000, step=1000,
                                                marks={0: '0 kg', 2500: '2500 kg', 5000: '5000 kg', 7500: '7500 kg', 10000: '10000 kg'},
                                                value=[min_payload, max_payload]
                                                ),

                                # TASK 4: Add a scatter chart
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2: Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Calculate total successes for all sites
        fig = px.pie(spacex_df, 
                     values='class',  
                     names='Launch Site', 
                     title='Total Successful Launches By Site')
        return fig
    else:
        # Filter data for the selected site
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        # Count success (1) and failure (0) for the site
        class_counts = filtered_df.groupby(['class']).size().reset_index(name='count')
        # Map class to labels for the pie chart
        class_counts['class_label'] = class_counts['class'].map({0: 'Failure', 1: 'Success'})
        
        fig = px.pie(class_counts, 
                     values='count', 
                     names='class_label', 
                     title=f'Total Launches for site {entered_site}: Success vs. Failure')
        return fig

# TASK 4: Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='site-dropdown', component_property='value'), 
               Input(component_id="payload-slider", component_property="value")])
def get_scatter_chart(entered_site, payload_range):
    # Filter by payload range first
    low, high = payload_range
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) & 
                            (spacex_df['Payload Mass (kg)'] <= high)]
    
    if entered_site == 'ALL':
        # Scatter plot for ALL sites within the payload range
        fig = px.scatter(filtered_df, 
                         x='Payload Mass (kg)', 
                         y='class', 
                         color='Booster Version Category',
                         title='Correlation between Payload and Success for All Sites (Payload Range: %s-%s kg)' % (low, high))
        return fig
    else:
        # Filter for selected site and payload range
        site_filtered_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        # Scatter plot for the selected site within the payload range
        fig = px.scatter(site_filtered_df, 
                         x='Payload Mass (kg)', 
                         y='class', 
                         color='Booster Version Category',
                         title=f'Correlation between Payload and Success for site {entered_site} (Payload Range: {low}-{high} kg)')
        return fig


# Run the app
if __name__ == '__main__':
    app.run(debug=True) # Use app.run() for modern Dash versions