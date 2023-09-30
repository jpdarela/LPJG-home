#!/bin/sh

echo "compressing & archiving DATA files"

cd /home/jpdarela/guess

# name the backup
FNAME=guess_backup_DATA$(date +%F_%H_%M_%S).tar.gz


OLD_BACKUP=$(cat last_DATA_backup.txt)
echo $OLD_BACKUP

echo $FNAME > last_DATA_backup.txt

tar -cf - ./GLDAS ./FLUXNET2015 ./ISIMIP_SA ./benchmark ./GIT/*.sh ./GIT/*.patch ./GIT/test_model | pigz -9 -p 16 > $FNAME
mv $FNAME ../darel/OneDrive/Desktop/GUESS_data/backup
rm -rf ../darel/OneDrive/Desktop/GUESS_data/backup/$OLD_BACKUP
