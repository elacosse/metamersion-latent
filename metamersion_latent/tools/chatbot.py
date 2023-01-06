import click

from metamersion_latent.llm.chat import Chat
from metamersion_latent.llm.config import Config


def fetch_username_from_email(user_email: str) -> str:
    """Check if user email is valid.

    Args:
        user_email (str): User email.

    Returns:
        str: Username.
    """
    # if fails, return None
    # ToDo: Implement this function
    # lookup in google sheets from typeform

    return "John Doe"


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
        username = fetch_username_from_email(user_email)
        if username is not None:
            break
        print("Invalid email address. Please contact appropriate personel.")
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
