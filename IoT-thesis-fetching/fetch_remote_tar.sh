#!/bin/bash

now=$(date -d yesterday +"20%y%m%d")
filename_rem=$now'.tar.gpg'
filename=$now'.tar'

#download
echo "fetching $filename_rem"
wget http://xxx.xxx.xxx.xxx/ijuop/$filename_rem
gpg --passphrase=xxxxxxxxxxx -d $filename_rem > $filename

#list all file, copy their path in to_process.txt
tar -vtf $filename | rev | cut -d' ' -f1 | rev > to_process.txt
#extract
tar -xvf $filename > $now

#clean up
rm $filename_rem
rm $filename
rm $now
