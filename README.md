# dzshuffled

This script will create playlist in your Deezer library consisting of shuffled tracks from your other playlists. I write it to overcome track number limit for playlist. I have playlists for work work 1, work 2, work 3. And script select random 1000 tracks from all of them and make with it new playlist.

#### requirements:  
 - linux
 - python3
 - python module [requests](http://docs.python-requests.org/en/master/user/install/){:target="_blank"}

#### install 
you can just download current version of script
```sh
$ wget https://raw.githubusercontent.com/yaboroda/dzshuffled/master/dzshuffled;
$ chmod +x dzshuffled;
$ sudo chown root:root dzshuffled;
$ sudo mv dzshuffled /usr/bin/dzshuffled;
```

or you can clone git repo and make symlink
```sh
$ git clone https://github.com/yaboroda/dzshuffled;
$ cd dzshuffled/;
$ sudo ln -s $(pwd)/dzshuffled /usr/bin/dzshuffled
```


#### usage
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

#### default config file
Fill app_id and secret, token will be fetched by script  
Web-server will be started on port from config to receive Deezer answer to authentication  

pl_example section is scenario to make playlist named 'Example shuffled playlist' with tracks of playlists from source option.  

you can write as many scenarios as you like, but sections names must begin with pl_ 

playlists in source options should be separated with comma and space 

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

#### register Deezer app
To run this script you must register your own Deezer app and write Application ID and Secret Key in config.
 - go [here](https://developers.deezer.com/myapps){:target="_blank"}
 - click Create a new Application button
 - Application domain: localhost
 - Redirect URL after authentication: http://localhost:8090/dzshuffled-auth  
 (where 8090 is port number that you write in config)
 - Link to your Terms of Use: any link
 - Other fields fill as you like
