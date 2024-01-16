import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
from pydub import AudioSegment
import numpy as np
import time

# Create Dash app
app = dash.Dash(__name__)

# Load and process audio file
audio_path = 'app/static/audio/heart/normal_heart/A/combined_audio.wav'  # Replace with the path to your WAV audio file
audio = AudioSegment.from_file(audio_path)
audio_data = np.array(audio.get_array_of_samples())
audio_duration = len(audio_data) / audio.frame_rate

target_duration = 10
num_repeats = int(np.ceil(target_duration / audio_duration))
audio_data = np.tile(audio_data, num_repeats)
sample_rate = 44100
duration = len(audio_data) / sample_rate

# Layout of the app
app.layout = html.Div([
    dcc.Graph(id='animated-audio-chart'),
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
        var linePosition = Math.floor((elapsedTime % audioDuration) * audioArray.length / audioDuration);

        // Define the chunk size to avoid maximum call stack size exceeded
        var chunkSize = 1000;
        var subsetAudioArray = audioArray.slice(linePosition, linePosition + chunkSize);

        // Create the figure
        var figure = {
            data: [
                {y: subsetAudioArray, type: 'line', name: 'HBR Signal', line: {color: 'green'}},
                {x: [0, 0], y: [Math.min.apply(null, subsetAudioArray), Math.max.apply(null, subsetAudioArray)], mode: 'lines', line: {color: 'black', width: 10}}
            ],
            layout: {
                title: 'Animated Audio with Vertical Line',
                xaxis: {title: 'Sample'},
                yaxis: {title: 'Amplitude'},
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

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
