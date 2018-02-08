#!/bin/bash
set -x
./oneRun.py --file1=$1 --feds1=1776 --nevents=-1 --plugins=unpack,$2 --output-file=output/$2-$1 --progress 
