#!/bin/bash

walkers=1
min_line=38
zero_line=94

min_line=$[min_line+1]
zero_line=$[zero_line+1]
out=full-FES_rew-2deltaF.data

echo "#time deltaF" > $out
for file in `ls -v FES_rew-2/*`
do 
  echo -en "-- $file       \r"
  t=${file##*.t-};t=${t%.data}
  awk -v t=${t} -v l=$min_line -v z=$zero_line '{if (NR==l) min=$2; if (NR==z) zero=$2}END{print t,min-zero}' $file >> $out
done
