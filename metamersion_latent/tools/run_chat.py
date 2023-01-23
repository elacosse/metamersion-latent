import logging
import uuid
from pathlib import Path

import click
from dotenv import find_dotenv, load_dotenv

from metamersion_latent.llm.analysis import prompt
from metamersion_latent.llm.config import Config
from metamersion_latent.utils import save_to_yaml


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
    token = str(uuid.uuid4())
    logger.info("Chat token: %s", token)
    logger.info("Saving to %s", output_path)

    chat_history = example.chat_history

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
    if verbose:
        print("Poem:\n" + poem)

    analysis_dict = dict(
        personal_analysis=personal_analysis,
        amusing_story=amusing_story,
        story_scenes=story_scenes,
        created_landscapes=created_landscapes,
        created_objects=created_objects,
        surreal_landscapes=surreal_landscapes,
        poem=poem,
    )
    #######################################################################################################################

    draft_prompts = surreal_landscapes
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
    # TTS

    # Latent Blending


if __name__ == "__main__":
    log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_fmt)
    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]
    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv(), verbose=True)
    main()
