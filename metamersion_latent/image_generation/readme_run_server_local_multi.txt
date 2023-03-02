1: open tmux
2: split the panes: ctrl+b and "
3: go to upper pane: ctrl+b and cursur-up
4: activate the env, e.g. conda activate bobobubu. 
5: naviate to directory: metamersion-latent/metamersion_latent/image_generation
5: go to lower pane: ctrl+b and cursur-down
6: activate the env in lower pane as well and go to metamersion-latent/metamersion_latent/image_generation
7: CUDA_VISIBLE_DEVICES=0 python run_local_server.py --fp_chat_analysis=/tmp/chat_analysis.yaml --out_dir=/tmp/test_multi --mode=only_sound
8: CUDA_VISIBLE_DEVICES=1 python run_local_server.py --fp_chat_analysis=/tmp/chat_analysis.yaml --out_dir=/tmp/test_multi --mode=only_video
9: your video file is then in xxx/current.mp4. open with mpv or vlc


