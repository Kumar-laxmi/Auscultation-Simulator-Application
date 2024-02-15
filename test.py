import dash
from dash import dcc, html, Input, Output, State
import plotly.graph_objs as go
from pydub import AudioSegment
import numpy as np

app = dash.Dash(__name__)

app.layout = html.Div([
    html.H1("Audio Waveform Generator"),
    dcc.Input(id='audio-path-input', type='text', value='', placeholder='Enter audio path...'),
    dcc.Graph(id='audio-waveform-plot'),
    dcc.Interval(id='interval-component', interval=100, n_intervals=0)  # Update interval in milliseconds
])

@app.callback(
    Output('audio-waveform-plot', 'figure'),
    [Input('interval-component', 'n_intervals')],
    [State('audio-path-input', 'value')]
)
def update_waveform(n_intervals, audio_path):
    ctx = dash.callback_context

    if not ctx.triggered_id:
        # Initial load, no triggering input
        return dash.no_update

    triggering_input = ctx.triggered_id.split('.')[0]

    if triggering_input == 'audio-path-input':
        # Input triggered by client-side callback, do nothing for now
        return dash.no_update

    # Server-side callback, update waveform plot
    if not audio_path:
        # If no audio path is provided, show a horizontal line at 0
        layout = go.Layout(
            title='Audio Waveform',
            xaxis=dict(title='Time (s)'),
            yaxis=dict(title='Amplitude'),
        )
        waveform_trace = go.Scatter(x=[0, 1], y=[0, 0], mode='lines', name='Waveform')
        vertical_line = go.Scatter(x=[0, 0], y=[-1, 1], mode='lines', line=dict(color='red'), name='Vertical Line')
    else:
        # Load audio file
        audio = AudioSegment.from_file(audio_path)

        # Convert audio data to numpy array
        audio_array = np.array(audio.get_array_of_samples())

        # Create time axis
        time_axis = np.linspace(0, len(audio_array) / audio.frame_rate, len(audio_array))

        # Calculate the current position of the vertical line based on the actual audio timestamp
        audio_duration = len(audio_array) / audio.frame_rate
        audio_timestamp = n_intervals * 0.1  # Update interval is 100 milliseconds

        # Use modulo operator to achieve infinite looping
        vertical_line_position = audio_timestamp % audio_duration

        # Create waveform plot
        waveform_trace = go.Scatter(x=time_axis, y=audio_array, mode='lines', name='Waveform')

        # Create moving vertical line
        vertical_line = go.Scatter(x=[vertical_line_position, vertical_line_position],
                                   y=[min(audio_array), max(audio_array)],
                                   mode='lines',
                                   line=dict(color='red'),
                                   name='Vertical Line')

        layout = go.Layout(
            title='Audio Waveform',
            xaxis=dict(title='Time (s)'),
            yaxis=dict(title='Amplitude'),
        )

    return {'data': [waveform_trace, vertical_line], 'layout': layout}

# Dummy backend string that updates over time
backend_string = "app/static/audio/heart/acute_myocardial_infarction/A/combined_audio.wav"

@app.callback(
    Output('audio-path-input', 'value'),
    [Input('interval-component', 'n_intervals')]
)
def update_text_box(_):
    global backend_string
    # Simulate updating backend string
    return backend_string

if __name__ == '__main__':
    app.run_server(debug=True)
