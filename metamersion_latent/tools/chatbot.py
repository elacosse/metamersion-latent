import logging
import os
import signal
import time
from pathlib import Path

import click
from dotenv import find_dotenv, load_dotenv

from metamersion_latent.llm.chat import Chat
from metamersion_latent.llm.config import Config
from metamersion_latent.utils import save_to_yaml
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


def format_special_template(config):
    Exhibit_background = config.Exhibit_background
    LSI_background = config.LSI_background
    AI_name = config.AI_name
    AI_background = config.AI_background
    AI_personality = config.AI_personality
    Opening_AI_question = config.Opening_AI_question
    AI_introduction = config.AI_introduction
    First_chat_directions = config.First_chat_directions
    initial_bot_message = config.initial_bot_message

    # Format the template
    AI_background = AI_background.format(AI_name=AI_name)
    AI_personality = AI_personality.format(AI_name=AI_name)
    AI_introduction = AI_introduction.format(AI_name=AI_name)
    First_chat_directions = First_chat_directions.format(
        AI_name=AI_name, Opening_AI_question=Opening_AI_question
    )

    template = config.template.format(
        Exhibit_background=Exhibit_background,
        LSI_background=LSI_background,
        AI_background=AI_background,
        First_chat_directions=First_chat_directions,
        initial_bot_message=initial_bot_message,
        history="{history}",  # !
        input="{input}",  # !
        qualifier="{qualifier}",  # !
    )
    return template


@click.command()
@click.option(
    "-c", "--config_path", type=click.Path(exists=True), help="Configuration file path."
)
@click.option("-v", "--verbose", is_flag=True, help="Verbose mode.")
@click.option(
    "-t", "--time_limit", is_flag=True, help="Run bot with time limits on chat."
)
@click.option(
    "-s", "--save_to_example", is_flag=True, help="Save example as username.py."
)
def main(config_path, verbose, time_limit, save_to_example):
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
        text = translate(config.initialization_message, "PT")
        print(text)
    else:
        print(config.initialization_message)
    #######################################################################################################################
    # Perform chat
    #######################################################################################################################
    start_time = time.time()
    # Format the template with the initial message

    # Format the template
    config.template = format_special_template(config)
    print(config.template)
    # config.template = config.template.format(
    #     initial_bot_message=config.initial_bot_message,
    #     history="{history}",
    #     qualifier="{qualifier}",
    #     input="{input}",
    # )

    chat = Chat(config, verbose)
    if bool_translate:
        human_input = input(translate(config.initial_bot_message, "PT") + "\n")
        # human_input = translate(human_input, "EN")
        output = chat(human_input)
        print(translate(output, "PT"))
    else:
        human_input = input(config.initial_bot_message + "\n")
        output = chat(human_input)
        print(output)
    username = human_input
    # Start chat loop
    while True:
        signal.signal(signal.SIGALRM, timeout_handler)
        signal.alarm(60)
        try:
            human_input = input("Visitor: ")
            if bool_translate:
                human_input = translate(human_input, "EN")
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

    # Format chat history properly and save to yaml
    chat_history = (
        config.ai_prefix + ": " + config.initial_bot_message + chat.get_history()
    )

    example_dict = {
        "chat_history": chat_history,
        "username": username,
        "configuration": os.path.basename(config_path),
        "language": language_selection,
    }
    if save_to_example:
        example_path = project_dir / "metamersion_latent" / "examples/chats"
        save_to_yaml(example_dict, username, example_path)


if __name__ == "__main__":
    log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_fmt)
    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]
    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv(), verbose=True)
    main()
