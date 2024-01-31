import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import numpy as np
import pyaudio

# Set up PyAudio
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16,
                channels=1,
                rate=44100,
                input=True,
                frames_per_buffer=1024)

# Set up the Dash app
app = dash.Dash(__name__)

# Define the layout
app.layout = html.Div([
    dcc.Graph(id='real-time-audio-chart', style={'height': '95vh'}),
    dcc.Interval(id='interval-component', interval=25, n_intervals=0)
])

# Define the callback to update the chart
@app.callback(Output('real-time-audio-chart', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_chart(n):
    # Read audio data from the stream
    audio_data = np.frombuffer(stream.read(1024), dtype=np.int16)

    # Generate the graph
    figure = {
        'data': [
            {'y': audio_data, 'type': 'line', 'name': 'Real-time Audio', 'line': {'color': 'green'}}
        ],
        'layout': {
            'title': 'Real-time Audio Waveform',
            'showlegend': False,
            'paper_bgcolor': 'black',
            'plot_bgcolor': 'black'
        }
    }

    return figure

if __name__ == '__main__':
    app.run_server(debug=True)
