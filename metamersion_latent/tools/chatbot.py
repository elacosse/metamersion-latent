import time

import click
from dotenv import find_dotenv, load_dotenv

from metamersion_latent.llm.analysis import prompt
from metamersion_latent.llm.chat import Chat
from metamersion_latent.llm.config import Config
from metamersion_latent.utils.translation import translate


def select_language() -> int:
    while True:
        user_input = input(
            "Please select language - Por favor, seleccione a língua \n1: English/Inglês \n2: Portuguese/Português\nNumber/Número: "
        )
        if user_input in ["1", "2"]:
            break
        else:
            print(
                "Invalid input - Entrada inválida.\n1: Portuguese/Português\n2: English/Inglês\n"
            )
    return int(user_input)


def timeout_handler(signum, frame):
    raise TimeoutError("Timeout")


@click.command()
@click.option(
    "-c", "--config", type=click.Path(exists=True), help="Configuration file path."
)
@click.option("-v", "--verbose", is_flag=True, help="Verbose mode.")
@click.option(
    "-t", "--time_limit", is_flag=True, help="Run bot with time limits on chat."
)
def main(config, verbose, time_limit):
    load_dotenv(find_dotenv(), verbose=False)  # load environment variables
    config_path = config
    config = Config.fromfile(config_path)
    #######################################################################################################################
    # Select Language
    #######################################################################################################################
    language_selection = select_language()
    if language_selection == 2:
        bool_translate = True
    else:
        bool_translate = False
    #######################################################################################################################
    # Display initialization message
    #######################################################################################################################
    if bool_translate:
        text = translate(config.initialization_message)
        print(text)
    else:
        print(config.initialization_message)
    #######################################################################################################################
    # Perform chat
    #######################################################################################################################
    start_time = time.time()
    # Format the template with the initial message
    config.template = config.template.format(
        initial_bot_message=config.initial_bot_message,
        history="{history}",
        input="{input}",
    )
    chat = Chat(config, verbose)
    if bool_translate:
        human_input = input(translate(config.initial_bot_message, "pt") + "\n")
        human_input = translate(human_input, "en")
        output = chat(human_input)
        print(translate(output, "pt"))
    else:
        human_input = input(config.initial_bot_message + "\n")
        output = chat(human_input)
        print(output)
    # Start chat loop
    while True:
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(60)
        try:
            human_input = input("Visitor: ")
            if bool_translate:
                human_input = translate(human_input, "en")
            signal.alarm(0)
        except TimeoutError:
            human_input = "bye"
        if human_input == "":  # Maybe place also other checks
            human_input = config.default_chat_input
            continue
        elif time_limit and time.time() - start_time > config.initial_chat_time_limit:
            if bool_translate:
                print(config.default_time_limit_message)
            else:
                print(config.default_time_limit_message)
            break
        output = chat(human_input)
        print(output)

        if human_input == "bye":
            break

    #######################################################################################################################
    # Perform Analysis
    #######################################################################################################################
    # Format chat history properly
    chat_history = (
        config.ai_prefix + ": " + config.initial_bot_message + chat.get_history()
    )
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
    if verbose:
        print("Poem:\n" + poem)
    #######################################################################################################################
    draft_prompts = surreal_landscapes

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

    # ToDo

    # TTS

    # Latent-blending


if __name__ == "__main__":
    main()
if __name__ == "__main__":
    main()
    main()
    main()
