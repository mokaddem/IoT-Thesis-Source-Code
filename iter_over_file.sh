#!/bin/bash

#Iter over files specified in DIR
# decompress it on disk
# process it with the python script
# delete the decompressed file

DATASET=blackhole27
FORMAT=ymd
DIR=~/dataset/archive/


ITERDIR=$DIR*/

rm all_files.log

for YEARDIR in $ITERDIR
do
    for MONTHDIR in $YEARDIR*/
    do
        for DAYDIR in $MONTHDIR*/
        do
            for filename in $DAYDIR*.gz
            do
                #gzip -f -k -d $filename
                #curFile=$(echo $filename  | cut -d '.' -f1,2) 
                #./put_in_redis.py -d $DATASET -f $FORMAT -s $filename
                #echo "$count: $filename"
                #echo "$count: $filename" >> processed-file.log
                echo "$filename" >> all_files.log
            done
        done
    done
done
