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
from metamersion_latent.utils import create_output_directory_with_identifier, save_to_yaml, load_yaml, user_choice
from metamersion_latent.utils.translation import translate
import os
import re

load_dotenv(find_dotenv(), verbose=False) 
dp_base = os.getenv("DIR_SUBJ_DATA") # to .env add  DIR_SUBJ_DATA='/Volumes/LXS/test_sessions/'
list_dns = os.listdir(dp_base)
list_dns = [l for l in list_dns if l[0]=="2"]
list_dns.sort(reverse=True)


dn = user_choice(list_dns, sort=False, suggestion=list_dns[0])
dp_session = f'{dp_base}/{dn}'
fp_chat = os.path.join(dp_session, 'chat_history.yaml')
config = Config.fromfile("../configs/chat/ls1_version_4.py")
dict_meta = load_yaml(fp_chat)
username = dict_meta['username']
chat_history = dict_meta['chat_history']

#######################################################################################################################
#
#Analyze Chat and Generate Story
#
#######################################################################################################################

#######################################################################################################################
# 1. Analyze the chat
#######################################################################################################################

chat_analysis = "1:" + prompt(
    config.analyze_chat_template.format(chat_history=chat_history),
    config.analyze_chat_model,
)
if verbose:
    print("\n\nChat analysis:\n" + chat_analysis)

#######################################################################################################################
# 2. Generate Story
#######################################################################################################################
story = "1:" + prompt(
    config.create_story_template.format(
        chat_history=chat_history,
        chat_analysis=chat_analysis,
        N_steps=config.N_steps,
        human_prefix=config.human_prefix
    ),
    config.create_story_model,
)
if verbose:
    print("\n\nThe story:\n" + story)

#######################################################################################################################
# 2.1 Critique the Story
#######################################################################################################################

critique_story = "1:" + prompt(
    config.critique_story_template.format(
        N_steps=config.N_steps,
        story=story,
        chat_analysis=chat_analysis,
    ),
    config.critique_story_model,
)
if verbose:
    print("\n\nStory critique:\n" + critique_story)

#######################################################################################################################
# 3. Make scenes for the story
#######################################################################################################################

scenes = "1:" + prompt(
    config.create_scenes_template.format(
        N_steps=config.N_steps,
        story=story
    ),
    config.create_scenes_model,
)
if verbose:
    print("\n\nScenes:\n" + scenes)


#######################################################################################################################
# 4. Create the landscapes
#######################################################################################################################

landscapes = "1:" + prompt(
    config.create_landscapes_template.format(
        scenes=scenes
    ),
    config.create_landscapes_model,
)
if verbose:
    print("\n\nLandscapes:\n" + landscapes)


#######################################################################################################################
# 5. Create the objects
#######################################################################################################################
  
objects = "1:" + prompt(
    config.create_objects_template.format(
        scenes=scenes,
        N_steps=config.N_steps
    ),
    config.create_objects_model,
)
if verbose:
    print("\n\nObjects:\n" + objects)


#######################################################################################################################
# 6. Create captions
#######################################################################################################################

captions = "1:" + prompt(
    config.create_captions_template.format(
        landscapes=landscapes,
        objects=objects
    ),
    config.create_captions_model,
)
if verbose:
    print("\n\nCaptions:\n" + captions)


#######################################################################################################################
# 7. Create poem
#######################################################################################################################

poem = "1:" + prompt(
    config.create_poem_template.format(
        N_steps=config.N_steps,
        scenes=scenes,
        objects=objects,
        poem_style=config.poem_style,
        verse_length=config.verse_length,
    ),
    config.create_poem_model,
)
# Split poem
narration_list = re.split(r"\d:", poem, maxsplit=config.N_steps)
narration_list = [l for l in narration_list if len(l) > 5]
narration_list = [l.replace('\n', ' ') for l in narration_list]
narration_list = [l.strip() for l in narration_list]

if verbose:
    print("\n\nPoem:\n")
    for n in narration_list:
        print(n)


#######################################################################################################################
# 8. Create captions
#######################################################################################################################

#######################################################################################################################
draft_prompts = captions

### Put this into a function!
draft_prompts = [
    line.split(":", 1)[1][1:].replace(". ", "")
    for line in draft_prompts.split("\n")
]
# draft_prompts = [line.split(":", 1)[1][1:] for line in draft_prompts.split("\n")]

prompts = [
    config.prefix + prompt.rstrip(".") + ", " + config.postfix
    for prompt in draft_prompts
]
if verbose:
    print("\n\nPrompts:\n")
    for p in prompts:
        print(p)


dict_meta['list_prompts'] = prompts
dict_meta['narration_list'] = narration_list
save_to_yaml(dict_meta, 'chat_analysis', dp_session)
