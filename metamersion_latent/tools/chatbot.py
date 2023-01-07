import os

import click

from metamersion_latent.llm.chat import Chat
from metamersion_latent.llm.config import Config
from metamersion_latent.utils.oh_sheet import google_sheet_to_dataframe


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
    df = google_sheet_to_dataframe(os.getenv("GOOGLE_SHEET_ID"), "A1:Z")
    # get row of user email
    try:
        row = df.loc[
            df["{{field:01GNJ5JY9J262RCFX0D0CPJAEF}}, please provide your email."]
            == user_email
        ]
    except Exception as e:
        return None

    return row


@click.command()
@click.option(
    "-c", "--config", type=click.Path(exists=True), help="Configuration file path."
)
@click.option("-v", "--verbose", is_flag=True, help="Verbose mode.")
def main(config, verbose):
    config_path = config
    config = Config.fromfile(config_path)
    chat = Chat(config, verbose)

    # display initial message
    print(chat.initialization_message)
    # Get user input

    # Check if user input is valid and get name
    while True:
        user_email = input("Email: ")
        # df = fetch_row_from_dataframe_from_sheet(user_email)
        # username = df["Hello, what's your name?"].values[0]
        username = "test"
        if username is not None:
            break
        print(
            "Invalid email address. If you are a new user, please register first or try giving me your email again."
        )
    # Display welcome message
    print(f"Welcome {username}! And welcome to Metamersion!")
    print(chat.first_message)
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
    print("Analyzing the conversation...")
    while True:
        try:
            analysis_output = chat.analyze_buffer()
        except Exception as e:
            pass
        if output is not None:
            break
    print(analysis_output)

    print("Extracting concepts from analysis summary...")
    from metamersion_latent.utils.master_prompter import extract_concepts_from_analysis

    concepts = extract_concepts_from_analysis(analysis_output, config)
    print(concepts)


if __name__ == "__main__":
    main()
