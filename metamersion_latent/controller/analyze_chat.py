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
from metamersion_latent.utils import create_output_directory_with_identifier, save_to_yaml, load_yaml
from metamersion_latent.utils.translation import translate
import os
import re

load_dotenv(find_dotenv(), verbose=False)  # load environment variables
verbose = True

dp_session = '/mnt/ls1_data/test_sessions/230123_202646_NONE/'
fp_chat = os.path.join(dp_session, 'chat_history.yaml')
config = Config.fromfile("../configs/chat/ls1_jz1.py")
dict_out = load_yaml(fp_chat)
chat_history = dict_out['chat_history']

#######################################################################################################################
# Perform Analysis
#######################################################################################################################
# Short analysis
personal_analysis = "1." + prompt(
    config.short_analysis_template.format(chat_history=chat_history),
    config.short_analysis_model,
)
if verbose:
    print("Personal analysis:\n" + personal_analysis)
# Story analysis
amusing_story = "1:" + prompt(
    config.story_analysis_template.format(
        chat_history=chat_history,
        personal_analysis=personal_analysis,
        N_story_steps=config.N_story_steps,
    ),
    config.story_analysis_model,
)
if verbose:
    print("Amusing story:\n" + amusing_story)
# Scene analysis
story_scenes = "1:" + prompt(
    config.scene_analysis_template.format(
        N_story_steps=config.N_story_steps, amusing_story=amusing_story
    ),
    config.scene_analysis_model,
)
if verbose:
    print("Story scenes:\n" + story_scenes)
# Landscape analysis
created_landscapes = "1:" + prompt(
    config.landscape_analysis_template.format(story_scenes=story_scenes),
    config.landscape_analysis_model,
)
if verbose:
    print("Created landscapes:\n" + created_landscapes)
# Object analysis
created_objects = "1:" + prompt(
    config.object_analysis_template.format(
        story_scenes=story_scenes, N_story_steps=config.N_story_steps
    ),
    config.object_analysis_model,
)
if verbose:
    print("Created objects:\n" + created_objects)
# Objects in landscape analysis
surreal_landscapes = "1:" + prompt(
    config.object_in_landscape_analysis_template.format(
        created_landscapes=created_landscapes, created_objects=created_objects
    ),
    config.object_in_landscape_analysis_model,
)
if verbose:
    print("Surreal landscapes:\n" + surreal_landscapes)
# Poem analysis
poem = "1:" + prompt(
    config.poem_analysis_template.format(
        N_story_steps=config.N_story_steps,
        story_scenes=story_scenes,
        created_objects=created_objects,
        poem_style=config.poem_style,
        verse_length=config.verse_length,
    ),
    config.poem_analysis_model,
)
# Split poem
narration_list = re.split(r"\d:", poem, maxsplit=config.N_story_steps)
narration_list = [l for l in narration_list if len(l) > 5]
narration_list = [l.replace('\n', ' ') for l in narration_list]
narration_list = [l.strip() for l in narration_list]

if verbose:
    print("Poem:\n" + poem)
#######################################################################################################################
draft_prompts = surreal_landscapes

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


dict_out['list_prompts'] = prompts
dict_out['narration_list'] = narration_list
save_to_yaml(dict_out, 'chat_analysis', dp_session)
