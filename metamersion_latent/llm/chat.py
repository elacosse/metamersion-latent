import re

from langchain.chains import ConversationChain, LLMChain
from langchain.chains.conversation.memory import (
    ConversationBufferMemory,
    ConversationSummaryMemory,
)
from langchain.llms.loading import load_llm_from_config
from langchain.prompts.prompt import PromptTemplate

from metamersion_latent.llm.config import Config
import os
from dotenv import find_dotenv, load_dotenv

def gpt_vanilla_call(prompt: str, config: dict) -> str:
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


class Chat:
    """Initialize a chat to experiment with

    Args:
        config: Config
        verbose (bool): prints out buffer text highlighted
    """

    def __init__(
        self, config: Config, verbose: bool = False, exit_conversation: bool = False
    ):

        self.verbose = verbose
        self.config = config
        load_dotenv(find_dotenv(), verbose=False) 
        self.llm = load_llm_from_config(config.model)
        self.template = self.config.template
        if exit_conversation:
            self.template = self.config.exit_conversation_template

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
            input_variables=["history", "input"], template=self.template
        )
        self.conversation = ConversationChain(
            prompt=self.prompt, llm=self.llm, verbose=self.verbose, memory=self.memory
        )

    def __call__(self, user_message: str) -> str:
        """This is the main function that is called to handle a user message.
        It returns the AI's response.
        Args:
            user_message (str): The user's message.
        Returns:
            str: The AI's response.
        """
        self.inputs.append(user_message)
        try:
            output = self.conversation.predict(input=user_message)
            # remove double spaces
            self.memory.buffer = re.sub(" +", " ", self.memory.buffer)
        except Exception:
            output = "Oops, something went wrong. I'm sorry. What did you say?"
        self.outputs.append(output)
        return output

    def get_history(self) -> str:
        """Get the chat history."""
        return self.memory.buffer

    def analyze_conversation_buffer(self):
        """Generate a summary of the conversation for later analysis."""
        llm = load_llm_from_config(self.config.conversation_model)
        chain = LLMChain(llm=llm, prompt=self.conversation_summary_prompt)
        # Run the chain only specifying the input variable.
        history = self.memory.buffer
        try:
            output = chain.run(history=history)
        except Exception:
            return None
        self.conversation_summary = output

    def analyze_conversation_summary(self):
        """Generate a summary of the conversation for later analysis."""
        llm = load_llm_from_config(self.config.analysis_model)
        chain = LLMChain(llm=llm, prompt=self.analysis_prompt)
        # Run the chain only specifying the input variable.
        history = self.memory.buffer
        try:
            output = chain.run(history=history)
        except Exception:
            return None
        self.conversation_summary_analysis = output
