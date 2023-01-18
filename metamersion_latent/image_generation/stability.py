import io
import os
import warnings

import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
from PIL import Image
from stability_sdk import client


def generate_images_from_prompts(prompts: list, config: dict) -> list:
    """Generate images from prompts.
    Args:
        prompts (list): A list of prompts.
    Returns:
        list: A list of images.
    """
    stability_api = client.StabilityInference(
        key=os.environ["STABILITY_KEY"],
        engine=config["engine"],
        verbose=True,
    )

    images = []
    for i, prompt in enumerate(prompts):
        # the object returned is a python generator
        answers = stability_api.generate(
            prompt=prompt,
            seed=config["seed"],
            steps=config["steps"],
            cfg_scale=config["cfg_scale"],
            width=config["width"],
            height=config["height"],
            sampler=config["sampler"],
            guidance_preset=config["guidance_preset"],
            safety=config["safety"],
        )
        # iterating over the generator produces the api response
        for j, resp in enumerate(answers):
            for k, artifact in enumerate(resp.artifacts):
                if artifact.finish_reason == generation.FILTER:
                    warnings.warn(
                        "Your request activated the API's safety filters and could not be processed."
                        "Please modify the prompt and try again."
                    )
                if artifact.type == generation.ARTIFACT_IMAGE:
                    img = Image.open(io.BytesIO(artifact.binary))
                    images.append(img)
    return images


def create_collage(images: list) -> Image:
    """
    Create a collage from a list of images and captions.
    Args:
        images (list): List of images.
        captions (list): List of captions.

    Returns:
        PIL.Image: Collage image.
    """
    widths, heights = zip(*(i.size for i in images))

    total_width = sum(widths)
    max_height = max(heights)

    collage = Image.new("RGB", (total_width, max_height))

    # Add each image to the collage
    x_offset = 0
    for i, img in enumerate(images):
        collage.paste(img, (x_offset, 0))
        x_offset += img.size[0]
    return collage
