import pandas as pd
import sqlite3

from bokeh.io import curdoc
from bokeh.layouts import row, column, widgetbox
from bokeh.models import ColumnDataSource, Circle
from bokeh.models.widgets import PreText, Select, Button, TextInput, Div
from bokeh.plotting import figure

from astropy import coordinates as coords
import astropy.units as u

conn = sqlite3.connect("/Users/semyeong/data/cms.db")

df = pd.read_sql("""
select star.tgas_ra, star.tgas_dec, star.tgas_distance, star.group_id, star.group_size,
  tgas.pmra, tgas.pmdec
from star
left join tgas on
  star.tgas_row = tgas.[index]
where star.group_size>2
""", conn)
cg = \
    coords.SkyCoord(df['tgas_ra'], df['tgas_dec'], df['tgas_distance'], unit='deg')\
        .transform_to(coords.Galactic)
df['glon'] = cg.l.value
df['gx'], df['gy'], df['gz'] = cg.cartesian.xyz.value


df['vra'] = (df.pmra.values*u.mas/u.yr * df['tgas_distance'].values*u.pc) \
    .to(u.km/u.s, u.dimensionless_angles()).value
df['vdec'] = (df.pmdec.values*u.mas/u.yr * df['tgas_distance'].values*u.pc) \
    .to(u.km/u.s, u.dimensionless_angles()).value

source = ColumnDataSource(df)
TOOLS='pan,hover,box_select,lasso_select,reset,box_zoom'

renderer = []

p = figure(plot_width=600, plot_height=400, tools=TOOLS,
        x_axis_label='RA', y_axis_label='Dec')
renderer.append(
    p.circle('tgas_ra', 'tgas_dec', color='group_size', source=source,
        nonselection_fill_alpha=0.2, selection_fill_color='firebrick')
    )

pg = figure(plot_width=600, plot_height=400, x_range=(-300,300), y_range=(-300,300),
            tools=TOOLS,
            x_axis_label='gx', y_axis_label='gy')
renderer.append(
    pg.circle('gx', 'gy', color='group_size', source=source,
        nonselection_fill_alpha=0.2, selection_fill_color='firebrick')
    )

pl = figure(plot_width=600, plot_height=400, tools=TOOLS,
        x_axis_label='GLon', y_axis_label='gz')
renderer.append(
    pl.circle('glon', 'gz', color='group_size', source=source,
        nonselection_fill_alpha=0.2, selection_fill_color='firebrick')
    )

pv = figure(plot_width=600, plot_height=400, tools=TOOLS,
        x_axis_label='vra', y_axis_label='vdec')
renderer.append(
    pv.circle('vra', 'vdec', source=source,
        nonselection_fill_alpha=0.2, selection_fill_color='firebrick')
    )

for r in renderer:
    r.selection_glyph = Circle(fill_color='firebrick', line_color=None, radius=20)
    r.nonselection_glyph = Circle(fill_color='#1f77b4', fill_alpha=0.1, line_color=None)

layout = column(row(p, pg), row(pl, pv))
curdoc().add_root(layout)
