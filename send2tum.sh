#!/bin/sh

echo "compressing & archiving files"

tar -cf - ./guess4.1_hydraulics | pigz -9 -p 8 > guess.tar.gz
tar -cf - ./vsc_configs ./env ./grd ./res ./ins ./msk | pigz -9 -p 8 > aux_folders.tar.gz
tar -cf - *.tsv *.py | pigz -9 -p 8 > files.tar.gz
tar -cf - ./FLUXNET2015/ | pigz -9 -p 8 > FLUXNET2015.tar.gz


# Move to windows home dir. THere is a ps1 script that will scp this to tum
mv guess.tar.gz aux_folders.tar.gz files.tar.gz FLUXNET2015.tar.gz /mnt/c/Users/darel/

