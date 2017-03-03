from functools import lru_cache

import pandas as pd
import sqlite3

from bokeh.io import curdoc
from bokeh.layouts import row, column, widgetbox
from bokeh.models import ColumnDataSource
from bokeh.models.widgets import PreText, Select, Button, TextInput, Div
from bokeh.plotting import figure

conn = sqlite3.connect("/Users/semyeong/data/cms.db")

@lru_cache()
def get_group(group_id):
    query = "select * from star where star.group_id == {}".format(group_id)
    df = pd.read_sql(query, conn)
    df['color'] = df.tgas_gmag - df.tmass_jmag
    df['gMag'] = df.tgas_gmag + 5*(pd.np.log10(df.tgas_parallax*1e-3)+1)
    return df

query = """
select pair_run.tgas_row1, pair_run.tgas_row
from star
left join star
"""

source = ColumnDataSource(data=dict(
    ra=[], dec=[], color=[], gMag=[]
    ))


group_id = 0

divInfo = Div(text="""
<h1>Group {}</h1>
""".format(group_id),)


def callback(attr, old, new):
    global group_id
    group_id = int(new)
    plot_group(group_id)
group_id_input = TextInput(value="0", placeholder='group id')
group_id_input.on_change("value", callback)

def go_next():
    global group_id
    group_id += 1
    group_id_input.value="{}".format(group_id)
    plot_group(group_id)
def go_prev():
    global group_id
    group_id -= 1
    group_id_input.value="{}".format(group_id)
    plot_group(group_id)

def plot_group(group_id):
    divInfo.text = "<h1>Group {}</h1>".format(group_id)
    source.data = source.from_df(
        get_group(group_id)[['tgas_ra','tgas_dec','color','gMag']])

button_next = Button(label='next')
button_next.on_click(go_next)
button_prev = Button(label='prev')
button_prev.on_click(go_prev)



TOOLS='pan,hover,box_select,lasso_select,reset'
 
geom = figure(plot_width=400, plot_height=400, tools=TOOLS)
geom.circle('tgas_ra', 'tgas_dec', source=source)

cmd = figure(plot_width=400, plot_height=400, x_range=(-1,2), y_range=(10,-2),
        tools=TOOLS)
cmd.circle('color', 'gMag', source=source)

birdseye = figure(plot_width=250, plot_height=250)

select_x = Select(value="ra", options=["ra", "gx", "gy", "gz"])
select_y = Select(value="ra", options=["ra", "gx", "gy", "gz"])
# select_x.on_change(update_x)
# select_x.on_change(update_x)

layout = column(
        row(divInfo,),
        row(geom, cmd,
            column(
                widgetbox(
                    button_prev, button_next, group_id_input), birdseye)
            ),
        row(widgetbox(select_x, select_y))
        )


plot_group(group_id)
# update()
curdoc().add_root(layout)

