import signal
import time

import click
from dotenv import find_dotenv, load_dotenv
import sys
sys.path.append("../..")
sys.path.append("..")
from metamersion_latent.llm.analysis import prompt
from metamersion_latent.llm.chat import Chat
from metamersion_latent.llm.config import Config
from metamersion_latent.llm.analysis import perform_analysis
from metamersion_latent.utils import create_output_directory_with_identifier, save_to_yaml, load_yaml, user_choice
import os
import re
import argparse

def txt_save(fp_txt, list_blabla, append=False):
    if append:
        mode = "a+"
    else:
        mode = "w"
    with open(fp_txt, mode) as fa:
        for item in list_blabla:
            fa.write("%s\n" % item)

dp_base = os.getenv("DIR_SUBJ_DATA") # to .env add  DIR_SUBJ_DATA='/Volumes/LXS/test_sessions/'
list_dns = os.listdir(dp_base)
list_dns = [l for l in list_dns if l[0]=="2"]
list_dns = [l for l in list_dns if os.path.isfile(os.path.join(dp_base, l, 'chat_history.yaml'))]
   

dp_save = os.path.join(dp_base, "all_chats")
for dn in list_dns:
    fp_chat = os.path.join(dp_base, dn, 'chat_history.yaml')
    data = load_yaml(fp_chat)['chat_history']
    data_split = data.split("\n")
    fp_chat = os.path.join(dp_save, f"{dn}.txt")
    txt_save(fp_chat, data_split)
    
    
    
