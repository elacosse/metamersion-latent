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

load_dotenv(find_dotenv(), verbose=False)  # load environment variables
verbose = True

dp_base = '/mnt/ls1_data/test_sessions/'
list_dns = os.listdir(dp_base)
list_dns.sort(reverse=True)

dn = user_choice(list_dns, sort=False, suggestion=list_dns[0])
dp_session = f'/mnt/ls1_data/test_sessions/{dn}'
fp_chat = os.path.join(dp_session, 'chat_history.yaml')
config = Config.fromfile("../configs/chat/ls1_jz1.py")
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

personal_analysis = "1:" + prompt(
    config.personal_analysis_template.format(chat_history=chat_history),
    config.personal_analysis_model,
)
if verbose:
    print("Personal analysis:\n" + personal_analysis)

#######################################################################################################################
# 2. Generate Story
#######################################################################################################################
amusing_story = "1:" + prompt(
    config.amusing_story_template.format(
        chat_history=chat_history,
        personal_analysis=personal_analysis,
        N_story_steps=config.N_story_steps,
        human_prefix=config.human_prefix
    ),
    config.story_analysis_model,
)
if verbose:
    print("Amusing story:\n" + amusing_story)

#######################################################################################################################
# 2.1 Critique the Story
#######################################################################################################################

critique_story = "1:" + prompt(
    config.critique_story_template.format(
        N_story_steps=config.N_story_steps,
        amusing_story=amusing_story,
        personal_analysis=personal_analysis,
    ),
    config.critique_story_model,
)
if verbose:
    print("Story critique:\n" + critique_story)

#######################################################################################################################
# 3. Make scenes for the story
#######################################################################################################################

story_scenes = "1:" + prompt(
    config.story_scenes_template.format(
        N_story_steps=config.N_story_steps,
        amusing_story=amusing_story
    ),
    config.story_scenes_model,
)
if verbose:
    print("Story scenes:\n" + story_scenes)


#######################################################################################################################
# 4. Create the landscapes
#######################################################################################################################

created_landscapes = "1:" + prompt(
    config.create_landscapes_template.format(story_scenes=story_scenes),
    config.create_landscapes_model,
)
if verbose:
    print("Created landscapes:\n" + created_landscapes)


#######################################################################################################################
# 5. Create the objects
#######################################################################################################################
  
created_objects = "1:" + prompt(
    config.object_analysis_template.format(
        story_scenes=story_scenes,
        N_story_steps=config.N_story_steps
    ),
    config.create_object_model,
)
if verbose:
    print("Created objects:\n" + created_objects)


#######################################################################################################################
# 6. Create captions
#######################################################################################################################

captions = "1:" + prompt(
    config.captions_template.format(
        created_landscapes=created_landscapes,
        created_objects=created_objects
    ),
    config.captions_model,
)
if verbose:
    print("Captions:\n" + captions)


#######################################################################################################################
# 7. Create poem
#######################################################################################################################

poem = "1:" + prompt(
    config.create_poem_template.format(
        N_story_steps=config.N_story_steps,
        story_scenes=story_scenes,
        created_objects=created_objects,
        poem_style=config.poem_style,
        verse_length=config.verse_length,
    ),
    config.create_poem_model,
)
# Split poem
narration_list = re.split(r"\d:", poem, maxsplit=config.N_story_steps)
narration_list = [l for l in narration_list if len(l) > 5]
narration_list = [l.replace('\n', ' ') for l in narration_list]
narration_list = [l.strip() for l in narration_list]

if verbose:
    print("Poem:\n" + poem)


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
for p in prompts:
    print(p)


dict_meta['list_prompts'] = prompts
dict_meta['narration_list'] = narration_list
save_to_yaml(dict_meta, 'chat_analysis', dp_session)
