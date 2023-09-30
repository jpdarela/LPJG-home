#!/bin/sh

echo "compressing & archiving files"

cd /home/jpdarela/guess

# name the backup
FNAME=guess_backup_$(date +%F_%H_%M_%S).tar.gz


OLD_BACKUP=$(cat last_backup.txt)
echo $OLD_BACKUP

echo $FNAME > last_backup.txt

tar -cf - ./guess4.1_hydraulics ./env ./grd ./ins ./msk ./res ./msk *.sh *.tsv *.py | pigz -9 -p 16 > $FNAME
mv $FNAME ../darel/OneDrive/Desktop/GUESS_data/backup
rm -rf ../darel/OneDrive/Desktop/GUESS_data/backup/$OLD_BACKUP
