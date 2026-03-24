from argparse import ArgumentParser
from json import dump, load, JSONDecodeError
from os import path
from sys import argv


CONFIG_PATH = path.join('.', 'config.json')


def set_config(args):
        
    if path.exists(CONFIG_PATH):

        with open(CONFIG_PATH, "r") as fd:

            try:
                
                config = load(fd)

            except JSONDecodeError:

                config = {}
    
    else:

        config = {}

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
    create_parser.add_argument('--start-date', '-s')
    create_parser.set_defaults(func = create_channel)
    
    update_parser = parsers.add_parser('update-channel')
    update_parser.add_argument('--channel-name', '-n', required = True)
    update_parser.set_defaults(func = update_channel)

    args = parser.parse_args(argv[1:])
    args.func(args)

    pass