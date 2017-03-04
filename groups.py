import pandas as pd
import sqlite3
import itertools
import palettable

from bokeh.io import curdoc
from bokeh.layouts import row, column, widgetbox
from bokeh.models import ColumnDataSource, Circle, HoverTool
from bokeh.models.widgets import PreText, Select, Button, TextInput, Div,\
                                 DataTable, TableColumn
from bokeh.plotting import figure

from astropy import coordinates as coords
import astropy.units as u

curdoc().title = 'Groups'

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
colorcycle = itertools.cycle(palettable.tableau.Tableau_20.hex_colors)
colorlist = [next(colorcycle) for i in range(df['group_id'].max()+1)]
print(len(colorlist), df['group_id'].max())
df['group_color'] = [colorlist[i] for i in df['group_id']]


df_mwsc = pd.read_sql("""
select mwsc.Name, mwsc.GLON, mwsc.GLAT, mwsc.d
from mwsc
where mwsc.d < {}
""".format(df['tgas_distance'].max()), conn)
cg_mwsc = coords.SkyCoord(df_mwsc['GLON'], df_mwsc['GLAT'], df_mwsc['d'], unit='deg',
                          frame=coords.Galactic)
c_mwsc = cg_mwsc.transform_to(coords.ICRS)
df_mwsc['gx'], df_mwsc['gy'], df_mwsc['gz'] = cg_mwsc.cartesian.xyz.value
df_mwsc['ra'], df_mwsc['dec'] = c_mwsc.ra.value, c_mwsc.dec.value
source_mwsc = ColumnDataSource(df_mwsc)


df['vra'] = (df.pmra.values*u.mas/u.yr * df['tgas_distance'].values*u.pc) \
    .to(u.km/u.s, u.dimensionless_angles()).value
df['vdec'] = (df.pmdec.values*u.mas/u.yr * df['tgas_distance'].values*u.pc) \
    .to(u.km/u.s, u.dimensionless_angles()).value

source = ColumnDataSource(df)
TOOLS='pan,box_select,lasso_select,reset,box_zoom,tap'

renderer = []


p = figure(plot_width=600, plot_height=400, tools=TOOLS,
        x_axis_label='RA', y_axis_label='Dec')
c_mwsc = p.circle('ra', 'dec', color='gray', source=source_mwsc, size=15, fill_alpha=0.3)
p.add_tools(HoverTool(renderers=[c_mwsc], tooltips={"Name":"@Name"}))
c1 = p.circle('tgas_ra', 'tgas_dec', source=source,
        color='group_color', alpha=0.5, size=5,)
p.add_tools(HoverTool(renderers=[c1], tooltips={"Group id":"@group_id"}))
# you just end up with multiple hover icon on toolbar...
renderer.append(c1)

pg = figure(plot_width=600, plot_height=400, x_range=(-300,300), y_range=(-300,300),
            tools=TOOLS,
            x_axis_label='gx', y_axis_label='gy')
pg.circle('gx', 'gy', color='gray', source=source_mwsc, size=15, alpha=0.3)
renderer.append(
    pg.circle('gx', 'gy', source=source,
        color='group_color', alpha=0.3, size=5)
    )

pl = figure(plot_width=600, plot_height=400, tools=TOOLS,
        x_axis_label='GLon', y_axis_label='gz')
pl.circle('GLON', 'gz', color='gray', source=source_mwsc, size=15, alpha=0.3)
renderer.append(
    pl.circle('glon', 'gz', source=source,
        color='group_color', alpha=0.3, size=5)
    )

pv = figure(plot_width=600, plot_height=400, tools=TOOLS,
        x_axis_label='vra', y_axis_label='vdec')
renderer.append(
    pv.circle('vra', 'vdec', source=source,
        color='group_color', alpha=0.3, size=5)
    )

for r in renderer:
    r.selection_glyph = Circle(fill_color='firebrick', size=20)
    r.nonselection_glyph = Circle(fill_color='#1f77b4', fill_alpha=0.1, line_color=None)

layout = column(row(p, pg), row(pl, pv))
curdoc().add_root(layout)
