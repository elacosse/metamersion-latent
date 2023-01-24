import re

from langchain.llms.loading import load_llm_from_config

from metamersion_latent.llm.config import Config


def prompt(prompt: str, config: dict) -> str:
    """Call GPT-3 with a prompt and return the output.

    Args:
        prompt (str): The prompt to send to GPT-3.
        config (dict): The config for GPT-3.

    Returns:
        str: The output from GPT-3.
    """
    llm = load_llm_from_config(config)
    output = llm(prompt)
    return output


def perform_analysis(chat_history: str, config: Config, verbose: bool = False) -> dict:

    dict_analysis = {}
    #######################################################################################################################
    # 1. Analyze the chat
    #######################################################################################################################
    if verbose:
        print("\nStarting: 1. Analyze the chat")
    chat_analysis = "1:" + prompt(
        config.analyze_chat_template.format(chat_history=chat_history),
        config.analyze_chat_model,
    )
    if verbose:
        print("\n\nChat analysis:\n" + chat_analysis)
    dict_analysis["chat_analysis"] = chat_analysis

    #######################################################################################################################
    # 2. Generate Story
    #######################################################################################################################
    if verbose:
        print("\nStarting: 2. Generate Story")
    story = "1:" + prompt(
        config.create_story_template.format(
            chat_history=chat_history,
            chat_analysis=chat_analysis,
            N_steps=config.N_steps,
            human_prefix=config.human_prefix,
        ),
        config.create_story_model,
    )
    if verbose:
        print("\n\nThe story:\n" + story)
    dict_analysis["story"] = story
    #######################################################################################################################
    # 2.1 Critique the Story
    #######################################################################################################################
    if verbose:
        print("\nStarting: 2.1 Critique the Story)")
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

    dict_analysis["critique_story"] = critique_story

    #######################################################################################################################
    # 3. Make scenes for the story
    #######################################################################################################################
    if verbose:
        print("\nStarting: 3. Make scenes for the story")
    scenes = "1:" + prompt(
        config.create_scenes_template.format(N_steps=config.N_steps, story=story),
        config.create_scenes_model,
    )
    if verbose:
        print("\n\nScenes:\n" + scenes)

    dict_analysis["scenes"] = scenes

    #######################################################################################################################
    # 4. Create the landscapes
    #######################################################################################################################
    if verbose:
        print("\nStarting: 4. Create the landscapes")
    landscapes = "1:" + prompt(
        config.create_landscapes_template.format(scenes=scenes),
        config.create_landscapes_model,
    )
    if verbose:
        print("\n\nLandscapes:\n" + landscapes)

    dict_analysis["landscapes"] = landscapes

    #######################################################################################################################
    # 5. Create the objects
    #######################################################################################################################
    if verbose:
        print("\nStarting: 5. Create the objects")
    objects = "1:" + prompt(
        config.create_objects_template.format(scenes=scenes, N_steps=config.N_steps),
        config.create_objects_model,
    )
    if verbose:
        print("\n\nObjects:\n" + objects)

    dict_analysis["objects"] = objects

    #######################################################################################################################
    # 6. Create captions
    #######################################################################################################################
    if verbose:
        print("\nStarting: 6. Create captions")
    captions = "1:" + prompt(
        config.create_captions_template.format(landscapes=landscapes, objects=objects),
        config.create_captions_model,
    )
    if verbose:
        print("\n\nCaptions:\n" + captions)

    dict_analysis["captions"] = captions

    #######################################################################################################################
    # 7. Create poem
    #######################################################################################################################
    if verbose:
        print("\nStarting: 7. Create poem")
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
    dict_analysis["poem"] = poem
    # Split poem
    narration_list = re.split(r"\d:", poem, maxsplit=config.N_steps)
    narration_list = [l for l in narration_list if len(l) > 5]
    narration_list = [l.replace("\n", " ") for l in narration_list]
    narration_list = [l.strip() for l in narration_list]

    if verbose:
        print("\n\nPoem:\n")
        for n in narration_list:
            print(n)

    dict_analysis["narration_list"] = narration_list

    #######################################################################################################################
    # 8. Create prompts
    #######################################################################################################################

    #######################################################################################################################
    if verbose:
        print("\nStarting: 8. Create prompts")
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
    dict_analysis["list_prompts"] = prompts

    return dict_analysis
