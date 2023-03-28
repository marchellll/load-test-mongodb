# Intro
This is collection of scripts I used to load test MongoDB.

Steal codes from https://github.com/sabyadi/mongolocust


# Setup Python
## Install Python
if you are using Mac like me, you should already have `pyhton3` after installing developer tools. Just check. If you don't have it or you don't have mac, figure out how to install python >v3.7. 🙏🏾

## Install venv

Documentation is here: https://packaging.python.org/en/latest/guides/installing-using-pip-and-virtual-environments/


### One time setup
```shell
# install virtualenv, only if it is not installed
python3 -m pip install --user virtualenv

# create new venv in folder `.venv`. This folder is ignored
python3 -m venv .venv
```

### Setup for every time you want to use this repo
```shell
# activate venv in current terminal
source .venv/bin/activate

# verify which python is used
which python

# when you no longer want to use the current env
deactivate
```

# How To Play

## Setup Dependencies

```shell
# for first install or when dependencies changes
python3 -m pip install -r requirements.txt
```

## To Run

```
locust -f load_test.py
```