import dash
from dash import dcc, html
from dash.dependencies import Input, Output, State
from pydub import AudioSegment
import numpy as np
import time

# Create Dash app
app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Layout of the app
audio_path = 'app/static/audio/heart/acute_myocardial_infarction/A/combined_audio.wav'
audio = AudioSegment.from_file(audio_path)
audio_data = np.array(audio.get_array_of_samples())
audio_duration = len(audio_data) / audio.frame_rate
subsampling_factor = 1
audio_data = audio_data[::subsampling_factor]

target_duration = 0.877
num_repeats = 1
audio_data = np.tile(audio_data, num_repeats)
sample_rate = 44100
duration = len(audio_data) / sample_rate

heartRate = 60

# Layout of the app
app.layout = html.Div([
    dcc.Graph(id='animated-audio-chart', style={'height': '95vh'}, config={'responsive': True}),
    dcc.Store(id='audio-data-store', data={'audio_data': audio_data.tolist(), 'audio_duration': audio_duration}),
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
                title: 'Normal Heart sound (Mitral valve)',
                showlegend: false,
                paper_bgcolor: 'black',  // Set background color to black
                plot_bgcolor: 'black'    // Set plot background color to black
            }
        };
        
        // Return the updated figure, startTime, and heartRate
        return [figure, startTime];
    }
    """,
    Output('animated-audio-chart', 'figure'),
    Output('interval-store', 'data'),
    Input('interval-component', 'n_intervals'),
    State('audio-data-store', 'data'),
    State('interval-store', 'data'),
    prevent_initial_call=True
)

if __name__ == '__main__':
    app.run_server(debug=True)
