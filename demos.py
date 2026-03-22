
from parser import read_html
import plotly.graph_objects as go
import polars as pl
from sys import argv
from time import time

# python demos.py <archive> <demo>
#
# archive: path to exported archive (include extension)
# demo: display, post_count


def display(df):

    print(df.shape)
    print(df)


def post_count(df):

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
    ).sort('date')

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

    pass



def run(path, demo):

    t0 = time()

    demos = {
        'display': display,
        'post_count': post_count
    }
    
    pl.Config.set_tbl_rows(-1)
    pl.Config.set_tbl_cols(-1)

    # if csv doesn't exist, create dataframe from html archive and 
    # write it to disk for next run
    
    fn = path.split('.')
    suffix = fn[-1]

    if suffix == 'html':
        
        df = read_html(path)
        df.write_csv()

    else:

        df = pl.read_csv(path, try_parse_dates = True)

    demos[demo](df)

    print(f'{time() - t0:0.2f}s')


if __name__ == '__main__':

    path = argv[1]
    demo = argv[2]
    
    run(path, demo)
    