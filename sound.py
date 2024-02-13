import dash
from dash import dcc, html, Input, Output, State
import plotly.subplots as sp
import plotly.graph_objs as go
import wave
import numpy as np

app = dash.Dash(__name__, suppress_callback_exceptions=True)

# Initial position of the vertical line
current_position = 0

# Initial file path
file_path = 'app/static/audio/heart/acute_myocardial_infarction/A/combined_audio.wav'

# Layout with interval component
app.layout = html.Div([
    dcc.Graph(id='waveform-plot'),
    dcc.Input(id='file-path-input', type='text', value=file_path, style={'width': '50%'}),
    dcc.Store(id='file-path-store', data=file_path),
    dcc.Interval(
        id='interval-component',
        interval=100,  # Update every 100 milliseconds
        n_intervals=0
    ),
])

# JavaScript callback to update the file path in the Store
update_file_path_callback = '''
function updateFilePath() {
    var updatedFilePath = document.getElementById('file-path-input').value;
    return updatedFilePath;
}
'''

# Callback to update the file path in the Store
app.clientside_callback(
    update_file_path_callback,
    Output('file-path-store', 'data'),
    Input('interval-component', 'n_intervals'),
    prevent_initial_call=True
)

# Callback to update waveform plot
@app.callback(
    Output('waveform-plot', 'figure'),
    [Input('file-path-store', 'data')],
    [State('interval-component', 'n_intervals')]
)
def update_waveform_plot(updated_file_path, n_intervals):
    global current_position

    # Create a subplot for the selected file
    fig = sp.make_subplots(rows=1, cols=1, shared_xaxes=True)

    # Read audio file
    with wave.open(updated_file_path, 'rb') as audio_file:
        signal = np.frombuffer(audio_file.readframes(-1), dtype=np.int16)
        sample_rate = audio_file.getframerate()

    # Create time array
    duration = len(signal) / sample_rate
    time = np.linspace(0., duration, len(signal))

    # Add trace for waveform
    trace = go.Scatter(x=time, y=signal, mode='lines', line=dict(color='green'))

    # Add a vertical line at the current position
    trace_vertical_line = go.Scatter(
        x=[current_position, current_position],
        y=[np.min(signal), np.max(signal)],
        mode='lines',
        line=dict(color='black', width=10),  # Adjust line color and width
        showlegend=False  # Remove the legend for the vertical line
    )

    fig.add_trace(trace)
    fig.add_trace(trace_vertical_line)

    # Set layout options
    fig.update_layout(
        title=None,  # Set title to None to remove it
        plot_bgcolor='black',  # Set the background color to black
        paper_bgcolor='black',  # Set the paper background color to black
        showlegend=False,  # Remove legends
        height=400,
        xaxis=dict(showgrid=False),  # Hide x-axis grid
        yaxis=dict(showgrid=False),  # Hide y-axis grid
    )

    # Update the current position for the next interval
    current_position += 0.01  # You can adjust the speed of the movement

    # If the current position exceeds the rightmost end, reset to the left
    if current_position >= duration:
        current_position = 0

    return fig

if __name__ == '__main__':
    app.run_server(debug=True)
