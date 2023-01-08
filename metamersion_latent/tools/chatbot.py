import os

import click
from dotenv import find_dotenv, load_dotenv

from metamersion_latent.llm.chat import Chat
from metamersion_latent.llm.config import Config
from metamersion_latent.utils.master_prompter import (
    beautify_concepts_to_stable_diffusion_prompts,
    extract_concepts_from_analysis,
)
from metamersion_latent.utils.oh_sheet import google_sheet_to_dataframe

GOOGLE_SHEET_EMAIL_COLUMN_NAME = (
    "{{field:01GNJ5JY9J262RCFX0D0CPJAEF}}, please provide your email."
)


def fetch_row_from_dataframe_from_sheet(user_email: str) -> str:
    """Check if user email is valid.

    Args:
        user_email (str): User email.

    Returns:
        str: Username.
    """
    # if fails, return None
    # ToDo: Implement this function
    # lookup in google sheets from typeform
    spreadsheet_id = os.getenv("GOOGLE_SHEET_ID")

    df = google_sheet_to_dataframe(spreadsheet_id, "A1:Z")
    # get row of user email
    try:
        row = df.loc[df[GOOGLE_SHEET_EMAIL_COLUMN_NAME] == user_email]
    except Exception as e:
        return None

    return row


@click.command()
@click.option(
    "-c", "--config", type=click.Path(exists=True), help="Configuration file path."
)
@click.option("-v", "--verbose", is_flag=True, help="Verbose mode.")
def main(config, verbose):
    load_dotenv(find_dotenv(), verbose=False)  # load environment variables
    config_path = config
    config = Config.fromfile(config_path)

    # display initial message
    print(config.initialization_message)
    # Check if user input is valid and get name
    while True:
        user_email = input("Email: ")
        df_form = fetch_row_from_dataframe_from_sheet(user_email)
        username = df_form["Hello, what's your name?"].values[0]
        if username is not None:
            config.template = config.template.format(
                form_item_0=username, history="{history}", input="{input}"
            )
            break
        print(
            "Invalid email address. If you are a new user, please register first or try giving me your email again."
        )
    # Display welcome message
    print(f"Welcome {username}! And welcome to Metamersion!\n")
    chat = Chat(config, verbose)
    # Generate first interaction and messasge
    output = chat(config.first_message)
    print(output)
    ########################################

    while True:
        human_input = input("User: ")
        if human_input == "goodbye":
            break
        elif human_input == "":
            human_input = "I don't know what to say."
            continue
        output = chat(human_input)
        print(output)

    # Analyze the conversation
    print("Analyzing the conversation...\n")
    while True:
        try:
            analysis_output = chat.analyze_buffer()
        except Exception as e:
            pass
        if output is not None:
            break
    print(analysis_output)

    print("Extracting concepts from analysis summary...\n")
    concepts = extract_concepts_from_analysis(analysis_output, config)
    print("Generating prompts...\n")
    stability_prompts = beautify_concepts_to_stable_diffusion_prompts(concepts)
    for i, prompt in enumerate(stability_prompts):
        print(i, prompt)
    from metamersion_latent.image_generation.stability import (
        generate_images_from_prompts_and_save,
        prompts_to_txt_file,
    )

    prompts_to_txt_file
    generate_images_from_prompts_and_save(stability_prompts)


if __name__ == "__main__":
    main()
