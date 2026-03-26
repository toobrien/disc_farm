get exporter [here](https://github.com/Tyrrrz/DiscordChatExporter/releases/latest)

1. get set config:

 ```bash
$ python farm-cli.py set-config "-t" <token>  -p <path to exporter>
``` 

2. create channel:

```bash
$ python farm-cli.py create-channel -n <friendly name> -i <channel id> -f [html|json|csv] -s [start date] -o parsed-only
```

set `sources-only`, `parsed-only`, or `all` to retain sources (html, json, exporter csv), parsed dataframe output (csv), or both

for `-f`:

- `html`: default format, medium size
- `json`: not yet supported, large size
- `csv` fastest, no parsing, small size

3. update channel:

```bash
$ python farm-cli.py update-channel -n <friendly name>
 ```
