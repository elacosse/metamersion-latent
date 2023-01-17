#! /bin/bash

echo $1

dp_remote="/home/ubuntu/"

scp setup_remote.sh $1:/$dp_remote/
scp run_remote_server.py $1:/$dp_remote/

echo "scp'd everything."
