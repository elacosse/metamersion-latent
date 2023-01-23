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


def perform_analysis(chat_history: str, config: Config) -> dict:
    # Short analysis
    personal_analysis = "1." + prompt(
        config.short_analysis_template.format(chat_history=chat_history),
        config.short_analysis_model,
    )

    # Story analysis
    amusing_story = "1:" + prompt(
        config.story_analysis_template.format(
            chat_history=chat_history,
            personal_analysis=personal_analysis,
            N_story_steps=config.N_story_steps,
        ),
        config.story_analysis_model,
    )

    # Scene analysis
    story_scenes = "1:" + prompt(
        config.scene_analysis_template.format(
            N_story_steps=config.N_story_steps, amusing_story=amusing_story
        ),
        config.scene_analysis_model,
    )

    # Landscape analysis
    created_landscapes = "1:" + prompt(
        config.landscape_analysis_template.format(story_scenes=story_scenes),
        config.landscape_analysis_model,
    )

    # Object analysis
    created_objects = "1:" + prompt(
        config.object_analysis_template.format(
            story_scenes=story_scenes, N_story_steps=config.N_story_steps
        ),
        config.object_analysis_model,
    )

    # Objects in landscape analysis
    surreal_landscapes = "1:" + prompt(
        config.object_in_landscape_analysis_template.format(
            created_landscapes=created_landscapes, created_objects=created_objects
        ),
        config.object_in_landscape_analysis_model,
    )

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

    analysis_dict = dict(
        personal_analysis=personal_analysis,
        amusing_story=amusing_story,
        story_scenes=story_scenes,
        created_landscapes=created_landscapes,
        created_objects=created_objects,
        surreal_landscapes=surreal_landscapes,
        poem=poem,
    )

    return analysis_dict
