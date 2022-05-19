#!/bin/bash


#for dir in ves-p ttmetad ves metad
for dir in new-ves
do
  echo -en " $dir\r"
  if [ ! -z `ls -d 0_$dir 2> /dev/null` ] 
  then
    paste *_$dir/deltaF.data |\
      awk 'BEGIN{print "#average std_dev"}
           NR>1{
             av=0; av2=0; 
             for (i=2; i<=NF; i+=2) {av+=$i; av2+=$i^2;};
             av*=2./NF; av2*=2./NF; 
             print $1,av,sqrt(av2-av^2)
           }' > stats_${dir}.data
    paste *_$dir/FES_rew-2deltaF.data |\
      awk 'BEGIN{print "#average std_dev"}
           NR>1{
             av=0; av2=0; 
             for (i=2; i<=NF; i+=2) {av+=$i; av2+=$i^2;};
             av*=2./NF; av2*=2./NF; 
             print $1,av,sqrt(av2-av^2)
           }' > stats_rew_${dir}.data
  fi
done
