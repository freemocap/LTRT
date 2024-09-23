import time
import numpy as np
import plotly.graph_objs as go
from plotly.subplots import make_subplots

fig = go.FigureWidget(data=[go.Scatter3d(x=[], y=[], z=[], mode='markers')])

def update_data(new_x, new_y, new_z):
    fig.data[0].x += new_x
    fig.data[0].y += new_y
    fig.data[0].z += new_z

data = np.load("/Users/philipqueen/freemocap_data/recording_sessions/freemocap_sample_data/freemocap_sample_data_frame_name_xyz.npy")

fig.show()

# for i in range(data.shape[0]):
for i in range(5):
    update_data(data[i, :, 0], data[i, :, 1], data[i, :, 2])
    time.sleep(5)
