#! /bin/bash

min_line=81
folder=fes_running
out=deltaF.data
if [ $# -ge 1 ]
then
  folder=$1
fi
if [ $# -eq 2 ]
then
  out=$2
fi

bck.meup.sh -i $out
for file in `ls -v ${folder}/*`
do 
  t=${file##*.t-};t=${t%.data}
  echo -en " -- $file \r"
  awk -v t=${t} -v l=$min_line 'NR==l{print t,$2}' $file >> $out
done
