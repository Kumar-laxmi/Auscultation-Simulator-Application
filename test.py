import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import numpy as np
import pyaudio
import wave
import threading
import time

# Set up PyAudio
p = pyaudio.PyAudio()

# Set up Dash app
app = dash.Dash(__name__)

# Initialize audio stream
wf = wave.open("app/static/audio/abdomen/borborygmus.wav", 'rb')
audio_stream = p.open(format=p.get_format_from_width(wf.getsampwidth()),
                      channels=wf.getnchannels(),
                      rate=wf.getframerate(),
                      output=True)

# Initialize Dash layout
app.layout = html.Div([
    dcc.Graph(id='real-time-audio-chart', style={'height': '95vh'}),
    dcc.Interval(id='interval-component', interval=25, n_intervals=0)
])

# Initialize audio data and time variables
audio_data = np.array([])
start_time = time.time()

# Callback to update the chart
@app.callback(Output('real-time-audio-chart', 'figure'),
              Input('interval-component', 'n_intervals'))
def update_chart(n):
    global audio_data, start_time

    # Read audio data from the stream
    chunk = 1024
    data = wf.readframes(chunk)
    audio_array = np.frombuffer(data, dtype=np.int16)

    # Play audio
    audio_stream.write(data)

    # Append new audio data to the existing array
    audio_data = np.append(audio_data, audio_array)

    # Calculate elapsed time
    elapsed_time = time.time() - start_time

    # Generate the graph
    figure = {
        'data': [
            {'y': audio_data, 'type': 'line', 'name': 'Real-time Audio', 'line': {'color': 'green'}}
        ],
        'layout': {
            'title': 'Real-time Audio Waveform',
            'showlegend': False,
            'paper_bgcolor': 'black',
            'plot_bgcolor': 'black',
            'xaxis': {'range': [0, elapsed_time * wf.getframerate()]}  # Adjust x-axis range based on elapsed time
        }
    }

    return figure

if __name__ == '__main__':
    threading.Thread(target=lambda: app.run_server(debug=True, use_reloader=False)).start()
    app_thread = threading.Thread(target=app.run_server, kwargs={'debug': True, 'use_reloader': False})
    app_thread.start()

    # Wait for the Dash app to start
    time.sleep(2)

    app_thread.join()
    p.terminate()
    wf.close()
