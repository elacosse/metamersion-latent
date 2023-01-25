import logging
import os
from datetime import datetime
from pathlib import Path

import click
from dotenv import find_dotenv, load_dotenv

from metamersion_latent.image_generation.stability import (
    create_collage,
    write_text_under_image,
)
from metamersion_latent.llm.analysis import perform_analysis
from metamersion_latent.llm.config import Config
from metamersion_latent.utils import load_yaml, save_to_yaml


@click.command()
@click.option(
    "-c", "--config_path", type=click.Path(exists=True), help="Configuration file path."
)
@click.option(
    "-e",
    "--example_path",
    type=click.Path(exists=True),
    help="Filepath with example conversation",
)
@click.option(
    "-o",
    "--output_path",
    type=click.Path(exists=True),
    help="Output directory",
)
@click.option("-v", "--verbose", is_flag=True, help="Verbose mode.")
@click.option(
    "-p",
    "--police_config",
    is_flag=True,
    help="Checks if configuration file was the same for the chatbot",
)
def main(config_path, example_path, output_path, verbose, police_config):
    logger = logging.getLogger(__name__)
    logger.info("Loading configuration file from %s", config_path)
    config = Config.fromfile(config_path)
    logger.info("Loading example conversation file from %s", example_path)
    # read yaml
    example = load_yaml(example_path)
    chat_history = example["chat_history"]
    username = example["username"]
    example["language"]

    # check if config file is the same as the one used in the chatbot
    if police_config:
        config_filename = os.path.basename(config_path)
        if config_filename != example["configuration"]:
            logger.error(
                "Configuration file used in the chatbot is different from the one used in the analysis."
            )
            return

    # Format the datetime as a string
    now = datetime.now()
    date = now.strftime("%Y%m%d_%H%M")
    token = f"{date}_{username}"

    logger.info("Chat token: %s", token)
    logger.info("Saving to %s", output_path)

    # Perform Analysis
    logger.info("Performing analysis on chat history...")
    analysis_dict = perform_analysis(chat_history, config)
    items = [
        dict(
            username=username,
            example_path=example_path,
            config_path=config_path,
            chat_history=chat_history,
            analysis=analysis_dict,
        )
    ]
    filepath = save_to_yaml(items, token, output_path)
    logger.info("Saved to %s", filepath)

    #######################################################################################################################
    analysis_dict["narration_list"]
    prompts = analysis_dict["list_prompts"]
    from metamersion_latent.controller.c2_generate_movie import Client

    negative_prompt = config.negative_prompt
    seed = config.seed
    width = config.width
    height = config.height
    ip_server = config.ip_server
    zmq_client = Client(ip_server, 7555, 7556, (width, height), verbose=True)
    from tqdm import tqdm

    list_imgs = []
    for prompt_item in tqdm(prompts):
        dict_meta = {}
        dict_meta["prompt"] = prompt_item
        dict_meta["neg_prompt"] = negative_prompt
        dict_meta["seed"] = seed
        dict_meta["width"] = width
        dict_meta["height"] = height
        img = zmq_client.run_image(dict_meta)
        list_imgs.append(img)

    poem = analysis_dict["poem"]
    split_poem = [phrase[:-1] for phrase in poem.split(":")[1:]]
    collage = create_collage(list_imgs)
    card_output = Path(output_path) / f"{token}.png"
    collage = write_text_under_image(collage, split_poem)
    collage.save(card_output)

    # kill process because of thread issues from zmq client
    # TODO: fix this
    os.system("kill %d" % os.getpid())


if __name__ == "__main__":
    log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_fmt)
    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]
    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv(), verbose=True)
    main()
