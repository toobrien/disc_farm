from argparse import ArgumentParser
from json import dump, load, JSONDecodeError
from os import path
from subprocess import run
from sys import argv


CONFIG_PATH = path.join('.', 'config.json')
DATA_PATH = path.join('.', 'data')
FMT = {
    'csv': 'Csv',
    'json': 'Json',
    'html': 'HtmlDark'
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
    

def set_config(args):

    config = get_config() if path.exists(CONFIG_PATH) else { "channels": {} }

    if args.token:

        config['token'] = args.token
        print(f'set token: {args.token[0:5]}...{args.token[-5:]}')

    if args.cli_path:

        config['cli_path'] = args.cli_path
        print(f'set cli path: {args.cli_path}')

    with open(CONFIG_PATH, 'w') as fd:
        
        dump(config, fd)
        print(f'config written to {CONFIG_PATH}')

    pass


def create_channel(args):

    config = get_config()
    channels = config['channels']

    if args.name in channels:

        print(f'[ERROR] channel {args.channel} already exists')
        exit(1)
    
    if 'token' not in config:

        print(f'[ERROR] no token in config; run `set-config -t ...` to set the token')
        exit(1)

    if 'cli_path' not in config:

        print(f'[ERROR] cli_path not in config; run `set-config -p ...` to set the exporter path')
        exit(1)

    exporter_args = [
        config['cli_path'], 'export',
        '-t', config['token'],
        '-c', args.id,
        '-f', FMT[args.format],
        '-o', path.join(DATA_PATH, f'{args.name}.{args.format}'),
    ]

    if (args.start):

        exporter_args.append('--after')
        exporter_args.append(args.start)
    
    run(exporter_args)

    pass


def update_channel(args):

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
    create_parser.add_argument('--format', '-f', choices = fmts, default = 'html')
    create_parser.add_argument('--start', '-s')
    create_parser.set_defaults(func = create_channel)
    
    update_parser = parsers.add_parser('update-channel')
    update_parser.add_argument('--channel-name', '-n', required = True)
    update_parser.set_defaults(func = update_channel)

    args = parser.parse_args(argv[1:])
    args.func(args)

    pass