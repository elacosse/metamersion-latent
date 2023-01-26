import re

# from langchain.chains import ConversationChain, LLMChain
from langchain.chains import LLMChain
from langchain.chains.conversation.memory import (
    ConversationBufferMemory,
    ConversationSummaryMemory,
)
from langchain.llms.loading import load_llm_from_config
from langchain.prompts.prompt import PromptTemplate

from metamersion_latent.llm.config import Config
from metamersion_latent.utils import get_p, select_dict_key_by_probability


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


def _chat_output_check(output: str) -> bool:
    """Returns true if it's a valid output from GPT-3.
    Args:
        output (str): The output from GPT-3.
    Returns:
        bool: True if it's a valid output from GPT-3.
    """
    for char in output:
        if char.isalpha():
            return True


class Chat:
    """Initialize a chat to experiment with

    Args:
        config: Config
        verbose (bool): prints out buffer text highlighted
    """

    def __init__(self, config: Config, verbose: bool = False):

        self.verbose = verbose
        self.config = config

        self.template = self.config.template
        self.llm = load_llm_from_config(config.model)
        qualifier_dict = self.config.qualifier_dict
        # Get p values for each qualifier and set them in the config
        pvals = get_p(list(qualifier_dict.values()))
        for i, key in enumerate(qualifier_dict):
            qualifier_dict[key] = pvals[i]
        self.config.qualifier_dict = qualifier_dict

        # keep a list of all input and outputs this handled
        self.inputs = []
        self.outputs = []

        # Initialize memory to selected type
        if self.config.memory_type == "Buffer":
            self.memory = ConversationBufferMemory(
                memory_key="history",
                human_prefix=self.config.human_prefix,
                ai_prefix=self.config.ai_prefix,
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
            input_variables=["history", "input", "qualifier"],
            template=self.template,
        )
        self.conversation = LLMChain(
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
        qualifier = select_dict_key_by_probability(self.config.qualifier_dict)

        iterations = 0
        while True or iterations > 3:
            try:
                # TODO make sure output is at least something!
                output = self.conversation.predict(
                    input=user_message,
                    qualifier=qualifier,
                    stop=self.config.conversation_stop_list,
                )
                # remove double spaces or other hacks...
                self.memory.buffer = re.sub(" +", " ", self.memory.buffer)
                self.memory.buffer = self.memory.buffer.replace(
                    f"{self.config.ai_prefix}: \n\n", f"{self.config.ai_prefix}:"
                )
            except Exception:
                output = "Oops, something went wrong. I'm sorry. What did you say?"
            if _chat_output_check(output):
                break
            iterations += 1
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
