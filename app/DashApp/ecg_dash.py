from dash import dcc, html
from dash.dependencies import Input, Output, State
import neurokit2 as nk
from django_plotly_dash import DjangoDash
import sys

sys.path.append('../../app')

hr_show = 60

resolution = 1000
ecg = nk.ecg_simulate(duration=10, heart_rate=hr_show, sampling_rate=1000)[:5000]
max_height, min_height = max(ecg), min(ecg)
time = list(range(5001))

# Example app.
figure = dict(
    data=[{'x': time, 'y': ecg, 'line': {'color': 'red'}}],
    layout=dict(
        xaxis=dict(range=[0, 5000]),
        yaxis=dict(range=[min_height, max_height]),
        plot_bgcolor='black',  # Set background color to black
        paper_bgcolor='black',  # Set paper color to black
        font=dict(color='white'),  # Set font color to white
    )
)

app = DjangoDash('ecgDash')

app.layout = html.Div([
    dcc.Graph(id='graph', figure=dict(figure), style={'height': '90vh'}),
    dcc.Interval(id="interval", interval=20),
    dcc.Store(id='offset', data=0),
    dcc.Store(id='store', data=dict(x=time, y=ecg, resolution=resolution)),
])

app.clientside_callback(
    """
    function (n_intervals, data, offset) {
        offset = offset % data.x.length;
        const end = Math.min((offset + 10), data.x.length);
        const xSubset = data.x.slice(offset, end);
        const ySubset = data.y.slice(offset, end);

        // Remove the last point to prevent connecting to the first point
        if (end < data.x.length) {
            xSubset.push(null);
            ySubset.push(null);
        }

        return [[{x: [xSubset], y: [ySubset]}, [0], 4950], end]
    }
    """,
    [Output('graph', 'extendData'), Output('offset', 'data')],
    [Input('interval', 'n_intervals')], [State('store', 'data'), State('offset', 'data')]
)