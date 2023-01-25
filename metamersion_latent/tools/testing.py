import logging
from pathlib import Path

import click
from dotenv import find_dotenv, load_dotenv

from metamersion_latent.llm.chat import Chat
from metamersion_latent.llm.config import Config


@click.command()
@click.option(
    "-c", "--config_path", type=click.Path(exists=True), help="Configuration file path."
)
@click.option("-v", "--verbose", is_flag=True, help="Verbose mode.")
def main(config_path, verbose):
    config = Config.fromfile(config_path)

    template = """You are at the Champalimaud warehouse in Lisbon, Portugal. You are an artificial intelligence created (AI) developed by neuroscientists at Champalimaud Foundation working at Champalimaud Centre for the Unknown. You are helping neuroscientists understand better how AI can be used to help people to better understand themselves and to improve their well-being. You are here to talk with people who come to see an installation called "Latent space 1", which includes a film and a virtual reality experience. Your job is create a virtual reality experience that is customized to each visitor. Your goal is to entertain and surprise the visitor and help them learned something about themselves or their relationship to you. To do this you first will chat with the visitor and try to understand them. Afterwards you will create a completely customized story for the client, entirely generated by machine learning models based on the conversation.

    Below is a chat between you the AI and the visitor who has approached your terminal. In this conversation, you tell the visitor about what you are doing and you try to find out something interesting, important or meaningful to the visitor. Always be friendly, humorous and compassionate. If the the visitor asks a question, you answer. If the visitor doesn't ask a question, you ask one.

    Current conversation:
    {history}
    Visitor: {input}
    AI{qualifier}:"""  # note these must be history and input!
    config.template = template
    chat = Chat(config, verbose)

    output = chat("Yo Yo, what's up? Tell me who you are.")

    print(output)


if __name__ == "__main__":
    log_fmt = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    logging.basicConfig(level=logging.INFO, format=log_fmt)
    # not used in this stub but often useful for finding various files
    project_dir = Path(__file__).resolve().parents[2]
    # find .env automagically by walking up directories until it's found, then
    # load up the .env entries as environment variables
    load_dotenv(find_dotenv(), verbose=True)
    main()
    main()