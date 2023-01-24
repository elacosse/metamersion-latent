import logging
from datetime import datetime
from pathlib import Path

import click
from dotenv import find_dotenv, load_dotenv

from metamersion_latent.llm.analysis import perform_analysis
from metamersion_latent.llm.config import Config
from metamersion_latent.utils import save_to_yaml

# from metamersion_latent.image_generation.stability import create_collage
# from metamersion_latent.image_generation.stability import write_text_under_image


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
def main(config_path, example_path, output_path, verbose):
    logger = logging.getLogger(__name__)
    logger.info("Loading configuration file from %s", config_path)
    config = Config.fromfile(config_path)
    logger.info("Loading example conversation file from %s", example_path)
    example = Config.fromfile(example_path)

    # Format the datetime as a string
    now = datetime.now()
    date = now.strftime("%Y%m%d_%H%M")
    token = f"{date}_{example.username}"

    logger.info("Chat token: %s", token)
    logger.info("Saving to %s", output_path)

    chat_history = example.chat_history

    # Perform Analysis
    logger.info("Performing analysis on chat history...")
    analysis_dict = perform_analysis(chat_history, config)
    items = [
        dict(
            example_path=example_path,
            config_path=config_path,
            chat_history=chat_history,
            analysis=analysis_dict,
        )
    ]
    filepath = save_to_yaml(items, token, output_path)
    logger.info("Saved to %s", filepath)

    #######################################################################################################################
    narration_list = analysis_dict["narration_list"]
    prompts = analysis_dict["list_prompts"]
    from metamersion_latent.controller.c2_generate_movie import Client

    negative_prompt = "ugly, blurry"
    seed = 420
    width = 768
    height = 512
    ip_server = "138.2.229.216"
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

    ######## Create cards
    from metamersion_latent.image_generation.stability import (
        create_collage,
        write_text_under_image,
    )

    collage = create_collage(list_imgs)
    card_output = Path(output_path) / f"{token}.png"
    collage = write_text_under_image(collage, narration_list)
    collage.save(card_output)


if __name__ == "__main__":
    log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_fmt)
    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]
    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv(), verbose=True)
    main()
