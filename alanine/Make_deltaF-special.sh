#! /bin/bash

min_line=39
zero_line=94

min_line=$[min_line+5]
zero_line=$[zero_line+5]
out=deltaF.data

bck.meup.sh -i $out
echo -e "#time  deltaF\n0 0" > $out
t=0
for file in `ls -v fes*`
do 
  t=$[t+1]
  awk -v t=${t} -v l=$min_line -v z=$zero_line '{if (NR==l) min=$2; if (NR==z) zero=$2}END{print t*10000,min-zero}' $file >> $out
done
