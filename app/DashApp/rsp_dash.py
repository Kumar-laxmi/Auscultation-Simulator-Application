import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import neurokit2 as nk
from django_plotly_dash import DjangoDash

# Example data (a circle).
resolution = 1000
rsp = nk.rsp_simulate(duration=10, respiratory_rate=15, sampling_rate=1000)[:5000]
max_height, min_height = max(rsp), min(rsp)
time = list(range(5001))

# Example app.
figure = dict(
    data=[{'x': time, 'y': rsp, 'line': {'color': 'blue'}}],
    layout=dict(
        xaxis=dict(range=[0, 5000]),
        yaxis=dict(range=[min_height, max_height]),
        plot_bgcolor='black',  # Set background color to black
        paper_bgcolor='black',  # Set paper color to black
        font=dict(color='white'),  # Set font color to white
    )
)

app = DjangoDash('rspDash')

app.layout = html.Div([
    dcc.Graph(id='graph', figure=dict(figure), style={'height': '90vh'}),
    dcc.Interval(id="interval", interval=20),
    dcc.Store(id='offset', data=0),
    dcc.Store(id='store', data=dict(x=time, y=rsp, resolution=resolution)),
])

app.clientside_callback(
    """
    function (n_intervals, data, offset) {
        offset = offset % data.x.length;
        const end = Math.min((offset + 10), data.x.length);
        const xSubset = data.x.slice(offset, end);
        const ySubset = data.y.slice(offset, end);

        // Remove the last point only if not reaching the end of the data
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

if __name__ == '__main__':
    app.run_server()
