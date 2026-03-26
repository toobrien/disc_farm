get exporter [here](https://github.com/Tyrrrz/DiscordChatExporter/releases/latest)

1. get set config:

 ```bash
$ python farm-cli.py set-config -t <token>  -p <path to exporter>
``` 

2. create channel:

```bash
$ python farm-cli.py create-channel -n <name> -i <channel id> -f [html|json|csv] -s [start date] -o parsed-only
```

3. update channel (get new messages):

```bash
$ python farm-cli.py update-channel -n <name>
 ```


regarding `create-channel`:

`-o`: 

- `sources-only`: retain only the exporter outputs
- `parsed-only`: retain only the csv (identical to `sources-only` for `-f csv`) 
- `all`: keep both source and csv

`-f`:

- `html`: default format, medium size
- `json`: not yet supported, large size
- `csv` fastest, no parsing, small size

`-s`: optional, set start date of initial download

`-n`: pick whatever name you want for the channel

for help with the token, run the exporter's guide command:

```bash
$ ./DiscordChatExporter.Cli guide
```