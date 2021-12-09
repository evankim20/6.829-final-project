declare -a type=("c" "pos" "pow")

name1=experiment-1
topo1=equadistant
nodes=50
schedule=basic_schedule
name2=experiment-2
topo2=wide-area

name3=node-experiment
declare -a no=("3" "5" "10" "25" "50" "100" "250" "500" "1000")

if ! [ "$1" ]
then
    for t in "${type[@]}"
    do
        python3 simulator.py --topo $topo1 --nodes $nodes --name $name1 --schedule $schedule --type "$t"
    done
    for t in "${type[@]}"
    do
        python3 simulator.py --topo $topo2 --nodes $nodes --name $name2 --schedule $schedule --type "$t"
    done
    for n in "${no[@]}"
    do
        for t in "${type[@]}"
        do
            python3 simulator.py --topo $topo1 --nodes "$n" --name $name3 --schedule $schedule --type "$t"
        done
    done
fi
