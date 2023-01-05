from dotenv import find_dotenv, load_dotenv
from langchain.chains import ConversationChain
from langchain.chains.conversation.memory import (
    ConversationBufferMemory,
    ConversationSummaryMemory,
)
from langchain.llms.loading import load_llm_from_config
from langchain.prompts.prompt import PromptTemplate

from metamersion_latent.llm.config import Config


class Chat:
    """Initialize a chat to experiment with

    Args:
        config: Config
        verbose (bool): prints out buffer text highlighted
    """

    def __init__(self, config: Config, verbose: bool = False):
        load_dotenv(find_dotenv(), verbose=False)  # load environment variables
        self.config = config
        self.llm = load_llm_from_config(config.model)
        self.initialization_message = self.config.initialization_message
        self.first_message = self.config.first_message

        # keep a list of all input and outputs this handled
        self.inputs = []
        self.outputs = []

        # Initialize memory to selected type
        if self.config.memory_type == "Buffer":
            self.memory = ConversationBufferMemory(
                human_prefix=self.config.human_prefix, ai_prefix=self.config.ai_prefix
            )
        elif self.config.memory_type == "BufferWindow":
            self.memory = ConversationBufferMemory(
                human_prefix=self.config.human_prefix,
                ai_prefix=self.config.ai_prefix,
                k=self.config.window_size,
            )
        elif self.config.memory_type == "Summary":
            self.memory = ConversationSummaryMemory(
                llm=self.llm,
                human_prefix=self.config.human_prefix,
                ai_prefix=self.config.ai_prefix,
            )

        self.prompt = PromptTemplate(
            input_variables=["history", "input"], template=self.config.template
        )
        self.conversation = ConversationChain(
            prompt=self.prompt, llm=self.llm, verbose=verbose, memory=self.memory
        )

    def __call__(self, user_message: str):
        """This is the main function that is called to handle a user message.
        It returns the AI's response.
        Args:
            user_message (str): The user's message.
        Returns:
            str: The AI's response.
        """
        self.inputs.append(user_message)
        output = self.conversation.predict(input=user_message)
        self.outputs.append(output)
        return output
