from bs4 import BeautifulSoup as bs
import os
from parser import get_df
import plotly.graph_objects as go
import polars as pl
from sys import argv
from time import time


# python demos.py <archive> <demo>
#
# archive: path to exported archive, without suffix. archive file's suffix must be .html
# demo: display, post_count


def display(df):

    print(df.shape)
    print(df)


def post_count(df):

    pass


def run(archive, demo):

    t0 = time()

    demos = {
        'display': display,
        'post_count': post_count
    }
    
    pl.Config.set_tbl_rows(-1)
    pl.Config.set_tbl_cols(-1)

    # if csv doesn't exist, create dataframe from html archive and 
    # write it to disk for next run
    
    if not os.path.exists(f'{archive}.csv'):

        root = bs(open(f'{archive}.html').read(), 'lxml')
        df = get_df(root)
        df.write_csv(f'{archive}.csv')

    else:

        df = pl.read_csv(f'{archive}.csv')

    demos[demo](df)

    print(f'{time() - t0:0.2f}s')


if __name__ == '__main__':

    archive = argv[1]
    demo = argv[2]
    
    run(archive, demo)
    