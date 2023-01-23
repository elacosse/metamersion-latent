#! /bin/bash

# VARIANT A: INSTALL WITH TRANSFORMERS AND MANUAL
# pip install open-clip-torch
# pip install omegaconf
# pip install fastcore -U
# pip install Pillow
# pip install ffmpeg-python
# pip install einops
# pip install gradio

# # Xformers
# pip install --extra-index-url https://download.pytorch.org/whl/cu113 torch torchvision==0.13.1+cu113
# pip install triton==2.0.0.dev20220701
# pip install -q https://github.com/camenduru/stable-diffusion-webui-colab/releases/download/0.0.15/xformers-0.0.15.dev0+4c06c79.d20221205-cp38-cp38-linux_x86_64.whl

# pip install pytorch_lightning
# pip install transformers

# general setup
mkdir movies

# Get latent blending
git clone https://github.com/lunarring/latentblending.git
cd latentblending

# VARIANT B: AUTO INSTALL
pip install -r requirements.txt
pip install numpy==1.21
pip install PyYAML

# TTS installs
pip install TTS
sudo apt-get -y install espeak-ng

# Music
pip install pydub
pip install wget

# Vimeo
pip install PyVimeo

# Get diffusion weights
#wget https://huggingface.co/stabilityai/stable-diffusion-2-1-base/resolve/main/v2-1_512-ema-pruned.ckpt v2-1_512-ema-pruned.ckpt
wget https://huggingface.co/stabilityai/stable-diffusion-2-1/resolve/main/v2-1_768-ema-pruned.ckpt v2-1_768-ema-pruned.ckpt 


python first_run.py
