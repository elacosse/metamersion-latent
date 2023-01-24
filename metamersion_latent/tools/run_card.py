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

    # Craft prompts
    draft_prompts = analysis_dict["surreal_landscapes"]
    draft_prompts = [
        line.split(":", 1)[1][1:].replace(". ", "")
        for line in draft_prompts.split("\n")
    ]
    prompts = [
        config.prefix + prompt.rstrip(".") + ", " + config.postfix
        for prompt in draft_prompts
    ]
    prompts_dict = dict()
    for i, p in enumerate(prompts):
        prompts_dict[i] = p
    items = [
        dict(
            example_path=example_path,
            config_path=config_path,
            chat_history=chat_history,
            analysis=analysis_dict,
            prompts=prompts_dict,
        )
    ]

    filepath = save_to_yaml(items, token, output_path)
    logger.info("Saved to %s", filepath)

    #######################################################################################################################
    # Format poem into phrase
    # [phrase[:-1] for phrase in poem.split(":")[1:]]

    # TTS

    # TODO

    ### Get Latent Blending to assemble 6 images

    # assign to list_imgs

    ######### Create cards
    # collage = create_collage(list_imgs)
    # card_output = Path(output_path) / f"{token}.png"
    # write_text_under_image(collage, split_poem)
    # collage = write_text_under_image(collage, split_poem)
    # collage.save(card_output)


if __name__ == "__main__":
    log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_fmt)
    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]
    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv(), verbose=True)
    main()
