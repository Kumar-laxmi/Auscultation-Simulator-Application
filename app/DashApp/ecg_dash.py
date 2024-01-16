import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import neurokit2 as nk
from django_plotly_dash import DjangoDash
import time
import numpy as np

# Create Dash app
app = DjangoDash('ecgDash')

hr_show = 60

# Generate and store ECG signal
duration = 10
sampling_rate = 1000
ecg_signal = nk.ecg_simulate(duration=duration, sampling_rate=sampling_rate)[:5000]
x_values = np.linspace(0, duration, len(ecg_signal))
ecg_data = {'x_values': x_values.tolist(), 'ecg_signal': ecg_signal.tolist()}

# Layout of the app
app.layout = html.Div([
    dcc.Graph(id='animated-ecg-chart', style={'height': '95vh'}),
    dcc.Store(id='ecg-data-store', data=ecg_data),
    dcc.Store(id='interval-store', data=time.time()),  # Store the start time
    dcc.Interval(
        id='interval-component',
        interval=25,  # Interval in milliseconds
        n_intervals=0
    )
])

# Clientside callback to update the graph
app.clientside_callback(
    """
    function(n, ecgData, startTime) {
        // Get the ECG signal and x_values from the stored data
        var xValues = ecgData['x_values'];
        var ecgSignal = ecgData['ecg_signal'];

        // Calculate the time passed since the start
        var currentTime = new Date().getTime() / 1000;  // Convert milliseconds to seconds
        var elapsedTime = currentTime - startTime;

        // Calculate the position of the vertical line
        var linePosition = Math.floor(elapsedTime * xValues.length / 5) % xValues.length;  // 10 seconds duration

        // Create the figure
        var figure = {
            data: [
                {x: xValues, y: ecgSignal, mode: 'lines', name: 'ECG Signal', line: {color: 'red'}},
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
    Output('animated-ecg-chart', 'figure'),
    Output('interval-store', 'data'),
    Input('interval-component', 'n_intervals'),
    State('ecg-data-store', 'data'),
    State('interval-store', 'data')
)