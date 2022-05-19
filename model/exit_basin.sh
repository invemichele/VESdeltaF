#!/bin/bash

bck=''
#bck='bck.0.'
outfes=fesA
logfile=log.exit
bck.meup.sh $logfile
sum_options="--mintozero --bin 300 --min -3 --max 3"
for i in `seq 0 4`;
do
  nline=`awk 'NR>1{if ($2>1) {print NR+1; exit}}' ${bck}Colvar.${i}.data` #for precaution the 1 points before are not taken
  [ -z $nline ] && echo "--no transition found in ${bck}Colvar.${i}.data" && nline=`cat ${bck}Colvar.${i}.data |wc -l`
  hillf=Hills.${i}.data
  head -$nline ${bck}$hillf > cutted-$hillf
  echo -en " summing ${bck}$hillf ...\r"
  plumed sum_hills --hills cutted-$hillf ${sum_options} --outfile ${outfes}.${i}.data &>> $logfile
done
bck.meup.sh useful-Hills.data
cat cutted-Hills* > useful-Hills.data
plumed sum_hills --hills useful-Hills.data ${sum_options} --outfile ${outfes}.data &>> $logfile
awk -v n=5 '{if ($1!="#!" && $1!="") {$2/=n; $3/=n} print $0}' ${outfes}.data > average_${outfes}.data
mv average_${outfes}.data ${outfes}.data
