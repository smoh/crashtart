from flask import Flask, render_template

import json
import plotly

import pandas as pd
import numpy as np
import sqlite3
from astropy import coordinates as coords
from astropy import units as u

app = Flask(__name__)
app.debug = True

conn = sqlite3.connect("/Users/semyeong/data/cms.db")
query = "select * from star where star.group_size>5"
df = pd.read_sql(query, conn)

c = coords.SkyCoord(df['tgas_ra'], df['tgas_dec'], df['tgas_distance'], unit=u.deg)
cg = c.transform_to(coords.Galactic)
df['gx'], df['gy'], df['gz'] = cg.cartesian.xyz.value


@app.route('/')
def index():

    graphs = [
        dict(
            data=[
                dict(
                    x=df.tgas_ra,
                    y=df.tgas_dec,
                    type='scatter',
                    mode="markers",
                    marker=dict(
                        color=df.group_id
                        ),
                ),
            ],
            layout=dict(
                title='first graph'
            ),
            id="graph-0"
        ),
    ]

    # Add "ids" to each of the graphs to pass up to the client
    # for templating
    ids = ['graph-{}'.format(i) for i, _ in enumerate(graphs)]

    # Convert the figures to JSON
    # PlotlyJSONEncoder appropriately converts pandas, datetime, etc
    # objects to their JSON equivalents
    graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('layouts/index.html',
                           ids=ids,
                           graphJSON=graphJSON)


@app.route('/3d')
def threed():

    graphs = [
        # dict(
        #     data=[
        #         dict(
        #             x=df.tgas_ra,
        #             y=df.tgas_dec,
        #             type='scatter',
        #             mode="markers",
        #             marker=dict(
        #                 color=df.group_id
        #                 ),
        #         ),
        #     ],
        #     layout=dict(
        #         title='first graph'
        #     ),
        #     id="graph-0"
        # ),
        dict(
            data=[
                dict(
                    x=df.gx,
                    y=df.gy,
                    z=df.gz,
                    type='scatter3d',
                    mode="markers",
                    marker=dict(
                        color=df.group_id,
                        size=2,
                        colorscale='Jet'
                        ),
                ),
            ],
            layout=dict(
                autosize=True,
                height=800,
                title='first graph',
                scene=dict(
                    aspectratio=dict(x=1,y=1,z=1),
                    camera=dict(
                        center=dict(x=0,y=0,z=0),
                        eye=dict(x=1.25,y=1.25,z=1.25),
                        up=dict(x=0,y=0,z=1)
                        ),
                    xaxis=dict(
                        type='linear',
                        ),
                    yaxis=dict(
                        type='linear',
                        ),
                    zaxis=dict(
                        type='linear',
                        )
                    )
                ),
            id="graph-1"
        ),
    ]

    # Add "ids" to each of the graphs to pass up to the client
    # for templating
    ids = ['graph-{}'.format(i) for i, _ in enumerate(graphs)]

    # Convert the figures to JSON
    # PlotlyJSONEncoder appropriately converts pandas, datetime, etc
    # objects to their JSON equivalents
    graphJSON = json.dumps(graphs, cls=plotly.utils.PlotlyJSONEncoder)

    return render_template('layouts/index.html',
                           ids=ids,
                           graphJSON=graphJSON)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=9999)
