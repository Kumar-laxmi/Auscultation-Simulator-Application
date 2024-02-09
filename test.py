import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd
import numpy as np

# Dummy data generation function
def generate_dummy_data(num_points=100):
    np.random.seed(42)
    x = np.linspace(0, 1, num_points)
    y = np.random.rand(num_points)
    df = pd.DataFrame({'X': x, 'Y': y})
    return df

# Initial dummy data
initial_data = generate_dummy_data()

# Initialize the Dash app
app = dash.Dash(__name__)

# App layout
app.layout = html.Div([
    html.H1("Dummy Data Plot"),
    
    # Graph component for plotting
    dcc.Graph(id='scatter-plot'),
    
    # Button to refresh the plot
    html.Button('Refresh Plot', id='refresh-button', n_clicks=0)
])

# Callback to update the plot on button click
@app.callback(
    Output('scatter-plot', 'figure'),
    [Input('refresh-button', 'n_clicks')]
)
def update_plot(n_clicks):
    # Generate new dummy data on button click
    dummy_data = generate_dummy_data()
    
    # Create a scatter plot using Plotly Express
    fig = px.scatter(dummy_data, x='X', y='Y', title='Dummy Data Plot')
    
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True)
