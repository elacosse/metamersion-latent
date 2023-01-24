import io
import os
import warnings
from pathlib import Path

import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
from PIL import Image, ImageDraw, ImageFont
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


def write_text_under_image(image, text_list):
    # Get the width and height of the image
    width, height = image.size
    # Create a new image with the same width and double the height
    new_image = Image.new("RGB", (width, int(height * 1.5)), "white")
    # Paste the original image on top of the new image
    new_image.paste(image, (0, 0))
    # Create a draw object to draw on the new image
    draw = ImageDraw.Draw(new_image)
    # Define the font to use for the text
    font_resource_path = (
        Path(__file__).resolve().parents[1] / "frontend" / "kongtext.ttf"
    )
    font = ImageFont.truetype(str(font_resource_path), 12)
    # Calculate the vertical spacing between each phrase
    spacing = width / len(text_list)
    # Draw the text on the new image
    for i in range(len(text_list)):
        draw.text(
            (0 + spacing * i, height + 10), text_list[i], font=font, fill=(0, 0, 0)
        )
    return new_image
