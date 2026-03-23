from argparse import ArgumentParser
from sys import argv


def set_config(args):

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