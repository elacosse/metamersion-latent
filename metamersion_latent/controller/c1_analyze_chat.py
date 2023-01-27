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
from metamersion_latent.utils.translation import translate
import os
import re
import argparse

parser = argparse.ArgumentParser(description="c1_analyze_chat")
parser.add_argument("--automatic_mode", type=bool, default=False)
args = parser.parse_args()

while True:
    # Select the folder
    load_dotenv(find_dotenv(), verbose=False) 
    dp_base = os.getenv("DIR_SUBJ_DATA") # to .env add  DIR_SUBJ_DATA='/Volumes/LXS/test_sessions/'
    list_dns = os.listdir(dp_base)
    list_dns = [l for l in list_dns if l[0]=="2"]
    list_dns = [l for l in list_dns if os.path.isfile(os.path.join(dp_base, l, 'chat_history.yaml'))]
    list_dns = [l for l in list_dns if not os.path.isfile(os.path.join(dp_base, l, 'chat_analysis.yaml'))]
    list_dns.sort(reverse=True)
    list_dns = list_dns[0:10]
    
    if not args.automatic_mode:
        dn = user_choice(list_dns, sort=False, suggestion=list_dns[0])
    else:
        if len(list_dns) == 0:
            time.sleep(10)
            continue
        else:
            dn = list_dns[0]
    
    # Load the chat
    dp_session = f'{dp_base}/{dn}'
    fp_chat = os.path.join(dp_session, 'chat_history.yaml')
    config = Config.fromfile("../configs/chat/ls1_version_4.py")
    dict_meta = load_yaml(fp_chat)
    username = dict_meta['username']
    chat_history = dict_meta['chat_history']
    
    # Perform analysis
    print(f"STARTING ANALYSIS FOR {dn}")
    dict_analysis = perform_analysis(chat_history, config, verbose=True)
    
    # Merge the dicts
    dict_meta.update(dict_analysis)
    
    # Saving
    save_to_yaml(dict_meta, 'chat_analysis', dp_session)
    
    print(f"ALL DONE. SAVED TO: {dp_session}")
    
    if not args.automatic_mode:
        break
    
    