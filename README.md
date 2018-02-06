# dzshuffled

script is working on linux  
install nesessery libs for python and run script without parameters for help message  
example of scenario will be in config file  

proper readme will be written later  

```sh
$ ./dzshuffled

usage: dzshuffled [-h] [-l] [-v] [-i] [--version] [SCENARIO]

This script will create playlist in your Deezer library consisting of shuffled
tracks from your other playlists. Pass scenario name or number to create
playlist from it. Pass -l or -lv to see all scenarios. Scenarios sets up in
config wich by default in ~/.config/dzshuffled/config.ini but you can reassign
it with DZSHUFFLED_CONFIG_PATH environment variable.

positional arguments:
  SCENARIO       name or number of scenario. Pass -l argument to see full list

optional arguments:
  -h, --help     show this help message and exit
  -l, --list     show full list of scenarios to create playlist from, pass -v
                 param to show info about them
  -v, --verbous  if called with argument -l, show info about listed scenarios
  -i, --info     show info about selected scenario but not do anithing
  --version      show script version
```

####default config file
Fill app_id and secret, token will be fetched by script  
Web-server will be started on port from config to receive Deezer answer to authentication  

pl_example section is scenario to make playlist named 'Example shuffled playlist' with tracks of playlists from source option.  

you can write as many scenarios as you like, but sections names must begin with pl_  

```ini
[auth]
app_id = 
secret = 
port = 8090

[token]
token = 

[pl_example]
title = Example shuffled playlist
type = shuffled
source = playlist 1, playlist 2
limit = 1000
```