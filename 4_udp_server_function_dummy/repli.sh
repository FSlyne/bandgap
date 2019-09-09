DEST=~/ecoc2019_tcd_ub/
cp test_db.py $DEST
cp run_remote_function.sh $DEST
cp udp_server_function.py $DEST
cd $DEST
git add --all
git commit -m "updating"
git push
