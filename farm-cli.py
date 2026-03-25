from argparse import ArgumentParser
from json import dump, load, JSONDecodeError
from os import path, remove
from polars import read_csv
from subprocess import run
from parser import read_html, read_json
from sys import argv


CONFIG_PATH = path.join('.', 'config.json')
DATA_PATH = path.join('.', 'data')
FMT = {
    'csv': 'Csv',
    'json': 'Json',
    'html': 'HtmlDark'
}
OUT_OPTS = [ 'source-only', 'parsed-only', 'all' ]
PARSERS = {
    'csv': read_csv,
    'json': read_json,
    'html': read_html
}


def get_config():

    try:

        with open(CONFIG_PATH) as fd:

            try:
                        
                return load(fd)

            except JSONDecodeError as e:

                print(f'[ERROR] {CONFIG_PATH} is malformatted: {e}')
                exit(1)
    
    except FileNotFoundError:

        print(f'[ERROR] config not found; run `set-config` command to set token and exporter cli path')
        exit(1)
    

def export(config, channel_id, format, outfile, start = None):

    exporter_args = [
        config['cli_path'], 'export',
        '-t', config['token'],
        '-c', channel_id,
        '-f', FMT[format],
        '-o', outfile,
    ]

    if (start):

        exporter_args.append('--after')
        exporter_args.append(start)
    
    proc = run(exporter_args)

    if (proc.returncode != 0):

        print(f'[ERROR] unable to download channel; config not updated')
        
        try:

            remove(outfile)
        
        except Exception as e:

            print(f'unable to remove {outfile}: {e}')
        
        exit(1)


def merge(fmt, tmpfile, outfile):

    if fmt == 'html':

        pass

    elif fmt == 'json':

        # TODO
        
        pass

    pass


def set_config(args):

    config = get_config() if path.exists(CONFIG_PATH) else { "channels": {} }

    if args.token:

        config['token'] = args.token
        print(f'set token: {args.token[0:5]}...{args.token[-5:]}')

    if args.cli_path:

        config['cli_path'] = args.cli_path
        print(f'set cli path: {args.cli_path}')

    with open(CONFIG_PATH, 'w') as fd:
        
        dump(config, fd, indent = 4)
        print(f'config written to {CONFIG_PATH}')

    pass


def create_channel(args):

    config = get_config()
    channels = config['channels']

    if args.name in channels:

        print(f'[ERROR] channel {args.name} already exists')
        exit(1)
    
    if 'token' not in config:

        print(f'[ERROR] no token in config; run `set-config -t ...` to set the token')
        exit(1)

    if 'cli_path' not in config:

        print(f'[ERROR] cli_path not in config; run `set-config -p ...` to set the exporter path')
        exit(1)

    outfile = path.join(DATA_PATH, f'{args.name}.{args.input_format}')
    start = args.start if args.start else None
    
    export(config, args.id, FMT[args.input_format], outfile, start)

    channels[args.name] = {
        'id': args.id,
        'input-format': args.input_format,
        'outputs': args.outputs
    }

    parser = PARSERS[args.input_format]
    df = parser(outfile)

    if args.outputs != 'source-only':
    
        df.write_csv(path.join(DATA_PATH, f'{args.name}.csv'))

    channels[args.name]['latest'] = df[-1]['ts'].dt.to_string()[0] if args.input_format != 'csv' else df[-1]['Date'][0]
    
    if args.outputs == 'parsed-only' and args.input_format != 'csv':

        remove(outfile)

    with open(CONFIG_PATH, "w") as fd:

        try:
            
            dump(config, fd, indent = 4)
        
        except Exception as e:

            print(f'[ERROR] unable to write config to {CONFIG_PATH}: {e}')      

    pass


def update_channel(args):

    config = get_config()

    if args.name not in config['channels']:

        print(f'[ERROR] {args.name} not in channels; run `create-channel` first')
        exit(1)
    
    channel = config['channels'][args.name]
    id_ = channel['id']
    fmt = channel['input-format']
    outputs = channel['outputs']
    start = channel['latest']
    tmpfile = path.join(DATA_PATH, f'{args.name}_tmp.{fmt}')
    outfile = tmpfile.replace('_tmp', '')

    export(config, id_, fmt, tmpfile, start)
    
    df = PARSERS[fmt](tmpfile)

    if outputs != 'parsed-only' and fmt != 'csv':

        try:
        
            merge(fmt, tmpfile, outfile)
        
        except Exception as e:

            print(f'[ERROR] unable to update {outfile}: {e}')
            remove(tmpfile)
            exit(1)

    if outputs != 'source-only':
    
        try:

            csvfile = path.join(DATA_PATH, f'{args.name}.csv')
            df = read_csv(csvfile).vstack(df[1:])
            df.write_csv(csvfile)

        except Exception as e:

            print(f'[ERROR] unable to update {csvfile}: {e}')
            exit(1)

    with open(CONFIG_PATH) as fd:

        try:
            
            channel['latest'] = df[-1]['ts'].dt.to_string()[0] if args.input_format != 'csv' else df[-1]['Date'][0]
            dump(fd, config)

        except Exception as e:

            print(f'[ERROR] unable to write config: {e}')
            exit(1)
        
    pass


if __name__ == "__main__":

    parser = ArgumentParser()
    parsers = parser.add_subparsers()

    fmts = ( 'json', 'html', 'csv' )

    config_parser = parsers.add_parser('set-config')
    config_parser.add_argument('--cli-path', '-p')
    config_parser.add_argument('--token', '-t')
    config_parser.set_defaults(func = set_config)
    
    create_parser = parsers.add_parser('create-channel')
    create_parser.add_argument('--name', '-n', required = True)
    create_parser.add_argument('--id', '-i', required = True)
    create_parser.add_argument('--input-format', '-f', choices = fmts, default = 'html')
    create_parser.add_argument('--outputs', '-o', choices = OUT_OPTS, default = 'source-only')
    create_parser.add_argument('--start', '-s')
    create_parser.set_defaults(func = create_channel)
    
    update_parser = parsers.add_parser('update-channel')
    update_parser.add_argument('--name', '-n', required = True)
    update_parser.set_defaults(func = update_channel)

    args = parser.parse_args(argv[1:])
    args.func(args)

    pass