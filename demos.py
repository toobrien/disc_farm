
from os import path
from parser import read_html
import plotly.graph_objects as go
import polars as pl
from sys import argv
from time import time

# python demos.py <archive> <demo> [ demo params ... ]
#
# archive: path to exported archive (include extension)
# demo parameters: 
#       display: username 
#       post_count: daily


def display(df, params):

    if params:

        df = df.filter(pl.col('username') == params[0])

    print(df.shape)
    print(df)


def post_count(df, params):

    if params and params[0] == 'daily':
    
        df = df.with_columns(
            pl.col('ts').dt.date().alias('date')
        )

    else:

        # monthly post count 

        df = df.with_columns(
            pl.date(
                pl.col('ts').dt.year(),
                pl.col('ts').dt.month(),
                1
            ).alias('date')
        )

    p_counts = df.group_by(
        pl.col('date'),
        pl.col('username')
    ).agg(
        pl.len().alias('post_count')
    )
    
    per_user = p_counts.group_by('username', maintain_order = True)
    total = p_counts.group_by('date').agg(pl.col('post_count').sum())

    fig = go.Figure()

    trace_data = [
        ( 
            u[0][0],
            u[1]['date'].to_list(),
            u[1]['post_count'].to_list()
        )
        for u in per_user
    ]

    trace_data.append(
        ( 
            'total', 
            total['date'].to_list(), 
            total['post_count'].to_list()
        )
    )

    trace_data = sorted(trace_data, key = lambda t: t[0])

    for t in trace_data:

        fig.add_trace(
            go.Bar({
                'name': t[0],
                'x': t[1],
                'y': t[2],
            })
        )

    fig.show()


def run(name, demo, params):

    t0 = time()

    demos = {
        'display': display,
        'post_count': post_count
    }
    
    pl.Config.set_tbl_rows(-1)
    pl.Config.set_tbl_cols(-1)

    df = pl.read_csv(path.join('.', 'data', f'{name}.csv'), try_parse_dates = True)

    demos[demo](df, params)

    print(f'{time() - t0:0.2f}s')


if __name__ == '__main__':

    name = argv[1]
    demo = argv[2]
    
    run(name, demo, argv[3:])
    