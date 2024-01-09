import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output, State
import neurokit2 as nk

# Example data (a circle).
resolution = 1000
ecg = nk.ecg_simulate(duration=10, heart_rate=70)[:2000]
time = list(range(2001))

# Example app.
figure = dict(
    data=[{'x': time, 'y': ecg, 'line': {'color': 'green'}}],
    layout=dict(
        xaxis=dict(range=[0, 2000]),
        yaxis=dict(range=[-1, 2]),
        plot_bgcolor='black',  # Set background color to black
        paper_bgcolor='black',  # Set paper color to black
        font=dict(color='white'),  # Set font color to white
    )
)

app = dash.Dash(__name__, update_title=None)  # remove "Updating..." from title
app.layout = html.Div([
    dcc.Graph(id='graph', figure=dict(figure)),
    dcc.Interval(id="interval", interval=25),
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

        return [[{x: [xSubset], y: [ySubset]}, [0], 1000], end]
    }
    """,
    [Output('graph', 'extendData'), Output('offset', 'data')],
    [Input('interval', 'n_intervals')], [State('store', 'data'), State('offset', 'data')]
)

if __name__ == '__main__':
    app.run_server()
