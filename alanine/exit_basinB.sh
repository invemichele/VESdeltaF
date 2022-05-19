#!/bin/bash

logfile=log.out
bck.meup.sh $logfile
for i in `seq 0 9`;
do
  nline=`awk 'NR>5{if ($2>0.5 && $2<2) {print int(NR*1./5)+4-1; exit}}' Colvar.${i}.data`
  hillf=Hills.${i}.data
  head -$nline $hillf > cutted-$hillf
  plumed sum_hills --hills cutted-$hillf --mintozero --bin 300 --kt 2.494339 --outfile fesB.${i}.data >> $logfile
done
cat cutted-Hills* > useful-Hills.data
plumed sum_hills --hills useful-Hills.data --mintozero --bin 300 --kt 2.494339 --outfile fesB.data >> $logfile
awk -v n=10 '{if ($1!="#!") {$2/=n; $3/=n;} print $0}' fesB.data > average_fesB.data
mv average_fesB.data fesB.data
