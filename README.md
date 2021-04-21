[![codecov](https://codecov.io/gh/yaboroda/dzshuffled/branch/master/graph/badge.svg)](https://codecov.io/gh/yaboroda/dzshuffled)

this project is abandoned

# dzshuffled

This script will create playlist in your Deezer library consisting of shuffled tracks from your other playlists. I write it to overcome track number limit for playlist. I have playlists for work work 1, work 2, work 3. And script select random 1000 tracks from all of them and make with it new playlist.  

This script writing on linux and for linux, but it works on windows too.

#### requirements:  
 - python3
 - python module [requests](http://docs.python-requests.org/en/master/user/install/)

#### install on linux
you can just download current version of script
```sh
$ wget -O dzshuffled-master.zip https://github.com/yaboroda/dzshuffled/archive/master.zip;
$ unzip dzshuffled-master.zip;
$ cd dzshuffled-master;
```

or you can clone git repo
```sh
$ git clone https://github.com/yaboroda/dzshuffled;
$ cd dzshuffled/;
```

then make symlink
```sh
$ sudo ln -s $(pwd)/dzshuffled /usr/bin/dzshuffled
```

#### install and use on windows
Chapter in development. Write me if you need it and i will do it ASAP. Now it isn't my priority.

#### register Deezer app
To run this script you must register your own Deezer app and write Application ID and Secret Key in config.
 - go [here](https://developers.deezer.com/myapps)
 - click Create a new Application button
 - Application domain: localhost
 - Redirect URL after authentication: http://localhost:8090/dzshuffled-auth  
 (where 8090 is port number that you write in config)
 - Link to your Terms of Use: https://raw.githubusercontent.com/yaboroda/dzshuffled/master/LICENSE
 - Other fields fill as you like
 
#### config
Config by default in ~/.config/dzshuffled/config.ini but you can reassign
it with DZSHUFFLED_CONFIG_PATH environment variable

Fill app_id and secret, token will be fetched by script  
Web-server will be started on port from config to receive Deezer answer to authentication  

pl_example section is scenario to make playlist named 'Example shuffled playlist' with tracks of playlists from source option.  

you can write as many scenarios as you like, but sections names must begin with pl_ 

playlists in source options should be separated with comma and space 

```ini
[system]
port = 8090
editor = vim
browser = chrome

[auth]
token = 
app_id = 
secret = 

[pl_example]
title = Example shuffled playlist
type = shuffled
source = playlist 1, playlist 2
limit = 1000
```

#### usage
edit config file in Vim, you can specify editor in config
```sh
$ dzshuffled -e
```

show list of scenarios in config file
```sh
$ dzshuffled -l
```

show list of scenarios in config file with more info about them
```sh
$ dzshuffled -lv
```

show info about scenario number 0
```sh
$ dzshuffled -i 0
```

show info about scenario with name pl_example
```sh
$ dzshuffled -i pl_example
```

run scenario with name pl_example
```sh
$ dzshuffled pl_example
```

to show help message run script without parameters
```sh
$ dzshuffled

usage: dzshuffled [-h] [-l] [-v] [-i] [-e] [--editor EDITOR] [-d] [--version]
                  [SCENARIO]

This script will create playlist in your Deezer library consisting of shuffled
tracks from your other playlists. Pass scenario name or number to create
playlist from it. Pass -l or -lv to see all scenarios. Scenarios sets up in
config wich by default in ~/.config/dzshuffled/config.ini but you can reassign
it with DZSHUFFLED_CONFIG_PATH environment variable.

positional arguments:
  SCENARIO         name or number of scenario. Pass -l argument to see full
                   list

optional arguments:
  -h, --help       show this help message and exit
  -l, --list       show full list of scenarios to create playlist from, pass
                   -v param to show info about them
  -v, --verbous    if called with argument -l, show info about listed
                   scenarios
  -i, --info       show info about selected scenario but not do anithing
  -e, --edit       edit config file vith editor specified in config, by
                   default it is Vim
  --editor EDITOR  edit config with passed program instead of editor from
                   config
  -d, --debug      debug mode for output full trace of exceptions
  --version        show script version

```

#### unit tests
[tests info](/tests.md)
