
import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
from pydub import AudioSegment
from django_plotly_dash import DjangoDash
import numpy as np
import time

# Create Dash app
app = DjangoDash('borborygmus_dash')

# Define a function to load audio data and duration
def loadAudioData(audioPath):
    try:
        audio = AudioSegment.from_file(audioPath)
        audio_data = np.array(audio.get_array_of_samples())
        audio_duration = len(audio_data) / audio.frame_rate
        subsampling_factor = 100
        audio_data = audio_data[::subsampling_factor]

        target_duration = 0.877
        num_repeats = 1
        audio_data = np.tile(audio_data, num_repeats)
        sample_rate = 44100
        duration = len(audio_data) / sample_rate

        return {'audio_data': audio_data.tolist(), 'audio_duration': duration}
    except:
        duration = 0.877
        sample_rate = 44100
        return {'audio_data': [0] * int(duration * sample_rate), 'audio_duration': duration}  # Assuming a small duration with zero values

# Layout of the app
app.layout = html.Div([
    dcc.Input(id='audio-path-input',type='text',placeholder='Enter audio path...',style={'display':'none'}),
    dcc.Graph(id='animated-audio-chart', style={'height': '95vh'}, config={'responsive': True}),
    dcc.Store(id='audio-data-store', data={'audio_data': [], 'audio_duration': 0}),
    dcc.Store(id='interval-store', data=time.time()),  # Store the start time and set default heart rate to 60
    dcc.Interval(id='interval-component', interval=25, n_intervals=0) # Interval in milliseconds
])

# Clientside callback to update the graph
app.clientside_callback(
    """
    function(n, audioData, startTime) {
        // Get the audio data and duration from the stored data
        var audioArray = audioData['audio_data'];
        var audioDuration = audioData['audio_duration'];
        var heartRate = 60

        // Calculate the time passed since the start
        var currentTime = new Date().getTime() / 1000;  // Convert milliseconds to seconds
        var elapsedTime = currentTime - startTime;

        // Calculate the position of the vertical line
        var timePerBeat = 60 / heartRate;
        var linePosition = Math.floor((elapsedTime % timePerBeat) * audioArray.length / timePerBeat);

        // Create the figure
        var figure = {
            data: [
                {y: audioArray, type: 'line', name: 'HBR Signal', line: {color: 'green'}},
                {x: [linePosition, linePosition], y: [Math.min.apply(null, audioArray), Math.max.apply(null, audioArray)], mode: 'lines', line: {color: 'black', width: 10}}
            ],
            layout: {
                showlegend: false,
                paper_bgcolor: 'black',  // Set background color to black
                plot_bgcolor: 'black'    // Set plot background color to black
            }
        };
        
        // Return the updated figure, startTime, and heartRate
        return [figure, startTime];
    """,
    Output('animated-audio-chart', 'figure'),
    Output('interval-store', 'data'),
    Input('interval-component', 'n_intervals'),
    State('audio-data-store', 'data'),
    State('interval-store', 'data'),
    prevent_initial_call=True
)

# Callback to load audio data when the input changes
@app.callback(
    Output('audio-data-store', 'data'),
    Input('audio-path-input', 'value')
)
def update_audio_data(audioPath):
    #audioPath = 'app/static/audio/abdomen/borborygmus.wav'
    audioPath = 'app/static/audio/heart/acute_pericarditis/A/combined_audio.wav'
    return loadAudioData(audioPath)
