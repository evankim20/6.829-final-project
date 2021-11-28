TODO: flesh this out more

## VirtualEnv:
TODO this will all be cleaned up using a shell script
If virtual environment isn't set up:
```
virtualenv venv -p python3
```

Then run:
```
source ./source/bin/activate
pip3 install numpy
pip3 install cryptography
...
```

## Usage:
```
python3 simulator.py --type [pos, pow, c] --nodes [int] --schedule [filename in schedules/]
```