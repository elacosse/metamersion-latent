import io
import os

import stability_sdk.interfaces.gooseai.generation.generation_pb2 as generation
from dotenv import find_dotenv, load_dotenv
from PIL import Image
from stability_sdk import client

EXAMPLE = [
    "A man standing on a beach at sunset, the waves crashing against the shore, a feeling of freedom and peace in the air, By Makoto Shinkai, Stanley Artgerm Lau, WLOP, Rossdraws, James Jean, Andr",
    " a cozy cafe filled with laughter, conversations, and warm smiles, as Eric takes in the sense of community and connection he feels with the people around him, artwork by artgerm, Donato Giancola, Craig Mullins and Alena ",
    "a majestic mountain peak, surrounded by lush forests and rolling hills, with a view of the horizon and a peaceful feeling of tranquility and serenity, digital painting, concept art, very cozy, fantasy, 4K, character design sheet, paintin",
    "a classroom full of students, all eyes on Eric as he speaks about the power of creativity and how it can be used to express oneself, artwork by artgerm, centered subject, wide angle, full frame, simple, solid shapes, texture",
    " is today,a man standing on a stage with a microphone, delivering a powerful speech to a large audience dressed in shades and a gold crown | greg rutkowski, sung choi, mitchell mohrhauser, maciej ",
]


def generate_images_from_prompts_and_save(prompts: list) -> list:
    """Generate images from prompts.
    Args:
        prompts (list): A list of prompts.
    Returns:
        list: A list of images.
    """
    stability_api = client.StabilityInference(
        key=os.environ["STABILITY_KEY"],
        verbose=True,
    )

    # create a new directory in data/
    os.makedirs(os.path.join("data", "stability"), exist_ok=True)

    for i, prompt in enumerate(prompts):
        # the object returned is a python generator
        answers = stability_api.generate(
            prompt=prompt,
            seed=420,  # if provided, specifying a random seed makes results deterministic
            steps=20,  # defaults to 30 if not specified
            safety=False,  # defaults to True if not specified
        )

        # iterating over the generator produces the api response
        for j, resp in enumerate(answers):
            for k, artifact in enumerate(resp.artifacts):
                # if artifact.finish_reason == generation.FILTER:
                #     warnings.warn(
                #         "Your request activated the API's safety filters and could not be processed."
                #         "Please modify the prompt and try again."
                #     )
                if artifact.type == generation.ARTIFACT_IMAGE:
                    img = Image.open(io.BytesIO(artifact.binary))
                    img.save(
                        "data/stability/image_{i}_{j}_{k}.png".format(i=i, j=j, k=k)
                    )


def main():
    load_dotenv(find_dotenv(), verbose=False)  # load environment variables
    generate_images_from_prompts_and_save(EXAMPLE)


if __name__ == "__main__":
    main()
