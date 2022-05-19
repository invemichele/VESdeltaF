#!/bin/bash

walkers=1
runs=100

for i in `seq 0 $[runs-1]`
do
  mkdir ${i}_ves-p
  cd ${i}_ves-p
  cp ../queue_gromax.sh ../plumed.dat .
  cp ../${i}_ves/input.* .
#  echo "#walker_n  tpr_inputs" > INPUTS.info
#  iter=0
#  for rand in `shuf -i 0-400 -n $walkers`
#  do
#    cp ../../tpr_inputs/input.${rand}.tpr input.${iter}.tpr
#    [ $walkers -eq 1 ] && mv input.0.tpr input.tpr
#    echo "${iter}  ${rand}" >> INPUTS.info
#    iter=$[iter+1]
#  done
  ./queue_gromax.sh
  cd ..
done
