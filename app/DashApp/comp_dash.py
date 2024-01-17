import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
from pydub import AudioSegment
from django_plotly_dash import DjangoDash
import numpy as np
import time

# Create Dash app
app = DjangoDash('compDash')

# Load and process audio file
audio_path = 'app/static/audio/lungs/amphoric_respiration/LLB/combined_audio.wav'  # Replace with the path to your WAV audio file
audio = AudioSegment.from_file(audio_path)
audio_data = np.array(audio.get_array_of_samples())
audio_duration = len(audio_data) / audio.frame_rate
subsampling_factor = 57
audio_data = audio_data[::subsampling_factor]

# Layout of the app
app.layout = html.Div([
    dcc.Graph(id='animated-audio-chart', style={'height': '95vh'}),
    dcc.Store(id='audio-data-store', data={'audio_data': audio_data.tolist(), 'audio_duration': audio_duration}),
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
    function(n, audioData, startTime) {
        // Get the audio data and duration from the stored data
        var audioArray = audioData['audio_data'];
        var audioDuration = audioData['audio_duration'];

        // Calculate the time passed since the start
        var currentTime = new Date().getTime() / 1000;  // Convert milliseconds to seconds
        var elapsedTime = currentTime - startTime;

        // Calculate the position of the vertical line
        var linePosition = Math.floor((elapsedTime % 5) * audioArray.length / 5);

        // Create the figure
        var figure = {
            data: [
                {y: audioArray, type: 'line', name: 'Lungs Signal', line: {color: 'green'}},
                {x: [linePosition, linePosition], y: [Math.min.apply(null, audioArray), Math.max.apply(null, audioArray)], mode: 'lines', line: {color: 'black', width: 10}}
            ],
            layout: {
                title: 'Lungs Amphoric Respiration (LLB)',
                showlegend: false,
                paper_bgcolor: 'black',  // Set background color to black
                plot_bgcolor: 'black'    // Set plot background color to black
            }
        };
        
        // Return the updated figure and startTime
        return [figure, startTime];
    }
    """,
    Output('animated-audio-chart', 'figure'),
    Output('interval-store', 'data'),
    Input('interval-component', 'n_intervals'),
    State('audio-data-store', 'data'),
    State('interval-store', 'data')
)