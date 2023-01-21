#! /bin/bash
# supply as first argument the IP of the remote server
dp_remote="/home/ubuntu/"
user=ubuntu
scp run_remote_server.py $user@$1:/$dp_remote/
scp install_dependencies.sh $user@$1:/$dp_remote/

echo "scp'd everything."
