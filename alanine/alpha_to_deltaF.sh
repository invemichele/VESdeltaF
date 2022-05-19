#!/bin/bash

out=deltaF.data

for f in `ls */Alpha.0.data`
do
  echo -en " ${f}   \r"
  awk 'BEGIN{print "#time deltaF"}NR>1{if ($1%10000==0) print $1*1,-$2}' $f > ${f%/*}/$out
done
