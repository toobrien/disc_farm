from bs4 import BeautifulSoup as bs
import os
from parser import get_df
import plotly.graph_objects as go
import polars as pl
from sys import argv
from time import time


# demo: print and save archive (in working dir) as csv
#       exclude .html from archive name

def run(archive):

    t0 = time()
    
    pl.Config.set_tbl_rows(-1)
    pl.Config.set_tbl_cols(-1)

    if not os.path.exists(f'{archive}.csv'):

        root = bs(open(f'{archive}.html').read(), 'lxml')
        df = get_df(root)
        df.write_csv(f'{archive}.csv')

    else:

        df = pl.read_csv(f'{archive}.csv')

    print(df.shape)
    print(df)
    print(f'{time() - t0:0.2f}s')


if __name__ == '__main__':

    run(argv[1])
    