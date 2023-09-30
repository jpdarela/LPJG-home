#!/bin/sh

echo "Moving files"

tar -cf - ./env ./grd ./res ./ins ./msk | pigz -9 -p 8 > aux_folders.tar.gz
tar -cf - *.tsv *.py | pigz -9 -p 8 > files.tar.gz

# Move data to a win dir where we can analyze that. There is a ps1 script there to untar this shit
mv aux_folders.tar.gz files.tar.gz ../darel/OneDrive/Desktop/GUESS_data/guess_runs
