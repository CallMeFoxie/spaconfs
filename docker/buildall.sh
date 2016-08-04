#!/bin/bash

for i in `ls`; do
  (
    cd $i
    sudo docker build -t $i .
  )
done
