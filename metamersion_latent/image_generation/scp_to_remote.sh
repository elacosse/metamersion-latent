#! /bin/bash

dp_remote="/home/ubuntu/"
user=ubuntu


scp run_remote_server.py $user@150.136.117.84:/$dp_remote/
scp install_dependencies.sh $user@150.136.117.84:/$dp_remote/
scp first_run.py $user@150.136.117.84:/$dp_remote/
scp latent_blending_segment.py $user@150.136.117.84:/$dp_remote/

scp run_remote_server.py $user@129.213.150.221:/$dp_remote/
scp install_dependencies.sh $user@129.213.150.221:/$dp_remote/
scp first_run.py $user@129.213.150.221:/$dp_remote/
scp latent_blending_segment.py $user@129.213.150.221:/$dp_remote/

scp run_remote_server.py $user@150.136.65.91:/$dp_remote/
scp install_dependencies.sh $user@150.136.65.91:/$dp_remote/
scp first_run.py $user@150.136.65.91:/$dp_remote/
scp latent_blending_segment.py $user@150.136.65.91:/$dp_remote/


echo "scp'd everything."

