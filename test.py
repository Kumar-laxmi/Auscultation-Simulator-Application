import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.graph_objs as go
from pydub import AudioSegment
import numpy as np
import time as tm

# Load audio file and extract waveform data
audio_path = 'app/static/audio/heart/acute_myocardial_infarction/A/combined_audio.wav'
audio = AudioSegment.from_wav(audio_path)
samples = np.array(audio.get_array_of_samples())
time = np.linspace(0, len(samples) / audio.frame_rate, num=len(samples))

# Create Dash app
app = dash.Dash(__name__)

# Define layout
app.layout = html.Div([
    dcc.Graph(
        id='audio-waveform',
        animate=True,
        figure={
            'data': [
                go.Scatter(
                    x=time,
                    y=samples,
                    mode='lines',
                ),
                go.Scatter(
                    x=[time.min(), time.min()],
                    y=[min(samples), max(samples)],
                    mode='lines',
                    line=dict(color='red', width=2),
                    name='Vertical Line',
                ),
            ],
            'layout': go.Layout(
                title='Audio Waveform with Moving Vertical Line',
                xaxis={'title': 'Time (s)'},
                yaxis={'title': 'Amplitude'},
            ),
        },
    ),
    dcc.Interval(
        id='interval-component',
        interval=50,  # in milliseconds
        n_intervals=0,
    ),
])

# Update the position of the vertical line with smooth movement
@app.callback(
    Output('audio-waveform', 'figure'),
    Input('interval-component', 'n_intervals')
)
def update_graph(n_intervals):
    # Calculate the elapsed time and update the position of the vertical line
    elapsed_time = n_intervals * 0.05  # Assuming 50 ms interval
    line_position = time.min() + elapsed_time % (time.max() - time.min())

    # Update the position of the vertical line in the figure
    figure = {
        'data': [
            go.Scatter(
                x=time,
                y=samples,
                mode='lines',
            ),
            go.Scatter(
                x=[line_position, line_position],
                y=[min(samples), max(samples)],
                mode='lines',
                line=dict(color='red', width=2),
                name='Vertical Line',
            ),
        ],
        'layout': go.Layout(
            title='Audio Waveform with Moving Vertical Line',
            xaxis={'title': 'Time (s)'},
            yaxis={'title': 'Amplitude'},
        ),
    }

    return figure

if __name__ == '__main__':
    app.run_server(debug=True)
