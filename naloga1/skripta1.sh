#!/bin/bash

function append {
	if [ $1 -eq 200 ]; then
		exit 0
	fi
	echo "$1 $2" >> zaporedje.dat
}

n=0
while true; do
	i=0
	while [ $i -ne 10 ]; do
		append $n $i
                i=$[$i+1]
                n=$[$n+1]
	done

	i=8
	while [ $i -ne 0 ]; do
		append $n $i
                i=$[$i-1]
                n=$[$n+1]
	done
done
