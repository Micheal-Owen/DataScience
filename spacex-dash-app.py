# Import required libraries
import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the SpaceX data into a pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")

# Get minimum and maximum payload values
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a Dash application
app = dash.Dash(__name__)

# Create the application layout
app.layout = html.Div(
    children=[
        html.H1(
            'SpaceX Launch Records Dashboard',
            style={
                'textAlign': 'center',
                'color': '#503D36',
                'font-size': 40
            }
        ),

        # TASK 1: Add a dropdown list to enable Launch Site selection
        # The default selected value is ALL sites
        dcc.Dropdown(
            id='site-dropdown',
            options=[
                {'label': 'All Sites', 'value': 'ALL'},
                {'label': 'CCAFS LC-40', 'value': 'CCAFS LC-40'},
                {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
                {'label': 'KSC LC-39A', 'value': 'KSC LC-39A'},
                {'label': 'VAFB SLC-4E', 'value': 'VAFB SLC-4E'}
            ],
            value='ALL',
            placeholder='Select a Launch Site here',
            searchable=True,
            clearable=False,
            style={
                'width': '80%',
                'margin': 'auto'
            }
        ),

        html.Br(),

        # TASK 2: Pie chart
        html.Div(
            dcc.Graph(id='success-pie-chart')
        ),

        html.Br(),

        html.P(
            "Payload range (Kg):",
            style={
                'width': '80%',
                'margin': 'auto'
            }
        ),

        # TASK 3: Add a slider to select payload range
        dcc.RangeSlider(
            id='payload-slider',
            min=0,
            max=10000,
            step=1000,
            value=[min_payload, max_payload],
            marks={
                0: '0',
                2500: '2500',
                5000: '5000',
                7500: '7500',
                10000: '10000'
            },
            tooltip={
                'placement': 'bottom',
                'always_visible': False
            }
        ),

        html.Br(),

        # TASK 4: Scatter chart
        html.Div(
            dcc.Graph(id='success-payload-scatter-chart')
        )
    ]
)


# TASK 2:
# Update the success pie chart based on the selected launch site
@app.callback(
    Output(
        component_id='success-pie-chart',
        component_property='figure'
    ),
    Input(
        component_id='site-dropdown',
        component_property='value'
    )
)
def get_pie_chart(entered_site):

    if entered_site == 'ALL':
        figure = px.pie(
            spacex_df,
            values='class',
            names='Launch Site',
            title='Total Success Launches By Site'
        )

    else:
        filtered_df = spacex_df[
            spacex_df['Launch Site'] == entered_site
        ]

        outcome_counts = (
            filtered_df['class']
            .value_counts()
            .reindex([0, 1], fill_value=0)
            .reset_index()
        )

        outcome_counts.columns = ['class', 'count']

        outcome_counts['Outcome'] = outcome_counts['class'].map(
            {
                0: 'Failed',
                1: 'Successful'
            }
        )

        figure = px.pie(
            outcome_counts,
            values='count',
            names='Outcome',
            title=f'Successful vs Failed Launches for {entered_site}'
        )

    return figure


# TASK 4:
# Update the scatter chart using the selected site and payload range
@app.callback(
    Output(
        component_id='success-payload-scatter-chart',
        component_property='figure'
    ),
    [
        Input(
            component_id='site-dropdown',
            component_property='value'
        ),
        Input(
            component_id='payload-slider',
            component_property='value'
        )
    ]
)
def get_scatter_chart(entered_site, payload_range):

    minimum_payload = payload_range[0]
    maximum_payload = payload_range[1]

    filtered_df = spacex_df[
        (
            spacex_df['Payload Mass (kg)'] >= minimum_payload
        )
        &
        (
            spacex_df['Payload Mass (kg)'] <= maximum_payload
        )
    ]

    if entered_site == 'ALL':
        figure = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title='Correlation between Payload and Success for All Sites',
            labels={
                'Payload Mass (kg)': 'Payload Mass (kg)',
                'class': 'Launch Outcome'
            }
        )

    else:
        site_df = filtered_df[
            filtered_df['Launch Site'] == entered_site
        ]

        figure = px.scatter(
            site_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title=f'Correlation between Payload and Success for {entered_site}',
            labels={
                'Payload Mass (kg)': 'Payload Mass (kg)',
                'class': 'Launch Outcome'
            }
        )

    figure.update_yaxes(
        tickmode='array',
        tickvals=[0, 1],
        ticktext=['Failed', 'Successful']
    )

    return figure


# Run the application
if __name__ == '__main__':
    app.run()