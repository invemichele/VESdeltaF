#!/bin/bash

bck=''
#bck='bck.0.'
logfile=log.exit
bck.meup.sh $logfile
outfes=fesA
sum_options="--mintozero --bin 300,300 --min 1.5,-5 --max 4,4 --kt 2.910062"
for i in `seq 0 9`;
do
  hillf=Hills.${i}.data
  nline=`awk -v safe=2 '{if ($1!="#!" && $2>2.8) {print NR-safe; exit}}' ${bck}$hillf` #for precaution the 2 points before are not taken
  head -$nline ${bck}$hillf > cutted-$hillf
  echo -en " summing ${bck}$hillf ...\r"
  plumed sum_hills --hills cutted-$hillf ${sum_options} --outfile ${outfes}.${i}.data &>> $logfile
done
cat cutted-Hills* > useful-Hills.data
plumed sum_hills --hills useful-Hills.data ${sum_options} --outfile ${outfes}.data &>> $logfile
awk -v n=10 '{if ($1!="#!" && $1!="") {$3/=n; $4/=n; $5/=n} print $0}' ${outfes}.data > average_${outfes}.data
mv average_${outfes}.data ${outfes}.data
