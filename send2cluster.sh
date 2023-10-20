#!/bin/sh

echo "compressing & archiving files"

tar -cf - ./guess4.1_hydraulics ./ins ./grd/*.grd ./msk *.tsv *.py | pigz -9 -p 8 > guess2cluster.tar.gz
mv guess2cluster.tar.gz /mnt/c/Users/darel/
