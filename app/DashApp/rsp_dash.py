import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import neurokit2 as nk
from django_plotly_dash import DjangoDash
import time
import numpy as np

# Create Dash app
app = DjangoDash('rspDash')

rr_show = 15

# Generate and store ECG signal
duration = 10
sampling_rate = 1000
rsp_signal = nk.rsp_simulate(duration=10, respiratory_rate=15, sampling_rate=1000)
x_values = np.linspace(0, duration, len(rsp_signal))
rsp_data = {'x_values': x_values.tolist(), 'rsp_signal': rsp_signal.tolist()}

# Layout of the app
app.layout = html.Div([
    dcc.Graph(id='animated-rsp-chart', style={'height': '95vh'}),
    dcc.Store(id='ecg-data-store', data=rsp_data),
    dcc.Store(id='interval-store', data=time.time()),  # Store the start time
    dcc.Interval(
        id='interval-component',
        interval=50,  # Interval in milliseconds
        n_intervals=0
    )
])

# Clientside callback to update the graph
app.clientside_callback(
    """
    function(n, rspData, startTime) {
        // Get the RSP signal and x_values from the stored data
        var xValues = rspData['x_values'];
        var rspSignal = rspData['rsp_signal'];

        // Calculate the time passed since the start
        var currentTime = new Date().getTime() / 1000;  // Convert milliseconds to seconds
        var elapsedTime = currentTime - startTime;

        // Calculate the position of the vertical line
        var linePosition = Math.floor(elapsedTime * xValues.length / 10) % xValues.length;  // 10 seconds duration

        // Create the figure
        var figure = {
            data: [
                {x: xValues, y: rspSignal, mode: 'lines', line: {color: 'blue'}},
                {x: [xValues[linePosition], xValues[linePosition]], y: [-1,1.2], mode: 'lines', line: {color: 'black', width: 10}}
            ],
            layout: {
                showlegend: false,  // Remove legend
                paper_bgcolor: 'black',  // Set background color to black
                plot_bgcolor: 'black'    // Set plot background color to black
            }
        };
        
        // Return the updated figure and startTime
        return [figure, startTime];
    }
    """,
    Output('animated-rsp-chart', 'figure'),
    Output('interval-store', 'data'),
    Input('interval-component', 'n_intervals'),
    State('ecg-data-store', 'data'),
    State('interval-store', 'data')
)