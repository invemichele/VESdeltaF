#! /bin/bash

min_line=36
zero_line=65
folder=fes_running
out=deltaF.data
if [ $# -ge 1 ]
then
  folder=$1
  out=$folder/../$out
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
#  awk -v t=${t} -v l=$min_line 'NR==l{printf t,$2}' $file >> $out
#  awk -v t=${t} -v l=$min_line -v z=$zero_line '{if (NR==l) min=$2; if (NR==z) zero=$2}END{print t,min-zero}' $file >> $out
  awk -v t=${t} -v l=$min_line -v z=$zero_line \
    '{if (NR==l) min=$2; else {if (NR==z) {zero=$2; print t,min-zero; exit;}} }' $file >> $out
done
