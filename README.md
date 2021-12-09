TODO: flesh this out more

## Setup:
Run the following command to get the virtual environment set up and dependencies downloaded
```
source setup.sh
```

After finishing running experiments, to deactivate the virtualenv run:
```
deactivate
```

## Usage:
```
python3 simulator.py --type [pos, pow, c] --nodes [int] --schedule [filename in schedules/] --topo [wide-area, equadistant] --name [name of results dir]
```

Add new schedules in `/schedules`, topologies can be implemented in the `simulator.py` file.  

To create graphs, run:
```
python3 gen_graphs.py --name [name of experiment in results dir] --topo [name of topology used for experiment] --nodes [int] 
```
