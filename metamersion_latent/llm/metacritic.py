import re

import numpy as np
from langchain.chains import LLMChain
from langchain.embeddings import OpenAIEmbeddings
from langchain.llms.loading import load_llm_from_config
from langchain.prompts import PromptTemplate

from metamersion_latent.llm.config import Config


class Critic:
    """A critic to evaluate the chatbot's responses.

    Args:
        config: Config
        verbose (bool): prints out buffer text highlighted
    """

    def __init__(self, config: Config, verbose: bool = False):
        self.verbose = verbose
        self.config = config

        # keep a list of all input and outputs this handled
        self.inputs = []
        self.outputs = []

        self.embeddings = OpenAIEmbeddings()

        self.llm_sentiment = load_llm_from_config(self.config.sentiment_model)

        self.sentiment_prompt = PromptTemplate(
            input_variables=["input"],
            template=self.config.sentiment_template,
        )

        self.goodbye_examples = config.goodbye_examples

        self.dict_result = dict()

    def _normalize_text(self, s: str, sep_token: str = " \n ") -> str:
        """Normalize text for embedding distance calculation
        Args:
            s (str): The text to normalize.
            sep_token (str): The token to use to separate sentences.
        Returns:
            str: The normalized text.
        """
        s = re.sub(r"\s+", " ", s).strip()
        s = re.sub(r". ,", "", s)
        # remove all instances of multiple spaces
        s = s.replace("..", ".")
        s = s.replace(". .", ".")
        s = s.replace("\n", "")
        s = s.strip()
        return s

    def _check_if_question_mark_present(self, text: str) -> bool:
        """Check if a question mark is present in the text.
        Args:
            text (str): The text to check.
        Returns:
            bool: True if a question mark is present.
        """
        return "?" in text

    def _get_embedding_distance_between_texts(self, text_a: str, text_b: str) -> float:
        """Get the embedding distance between two texts.
        Args:
            text_a (str): The first text.
            text_b (str): The second text.
            embedding: The embedding to use.
        Returns:
            float: The embedding distance between the two texts.
        """
        norm_text_a = self._normalize_text(text_a)
        norm_text_b = self._normalize_text(text_b)

        array_a_result = np.array(self.embeddings.embed_query(norm_text_a))
        array_b_result = np.array(self.embeddings.embed_query(norm_text_b))
        distance = np.linalg.norm(array_a_result - array_b_result)
        return distance

    def _get_sentiment_label_of_text(self, text: str) -> str:
        """Get the sentiment of a text.
        Args:
            text (str): The text to check.
        Returns:
            str: The sentiment of the text as label
        """
        chain = LLMChain(llm=self.llm_sentiment, prompt=self.sentiment_prompt)
        output = chain.run(text)
        return output

    def _get_metric_goodbye(self, message: str) -> float:
        """Get a measure that the user is saying goodbye.
        Args:
            message (str): The user's message.
        Returns:
            float: measure that the user is saying goodbye.
        """
        metric_goodbye = 0.0
        for goodbye_example in self.goodbye_examples:
            metric_goodbye += self._get_embedding_distance_between_texts(
                message, goodbye_example
            )
        metric_goodbye = metric_goodbye / len(self.goodbye_examples)
        return metric_goodbye


class MachineCritic(Critic):
    """A machine critic to evaluate the chatbot's responses.

    Args:
        config: Config
        verbose (bool): prints out buffer text highlighted
    """

    def __call__(self, message: str) -> str:
        """This is the main function that is called to handle a user message and perform an metacritic analysis
        It return a dictionary of values.
        Args:
            ai_message (str): The user's message.
        Returns:
            dict: A dictionary of values.
        """

        self.inputs.append(message)
        self.dict_result["message"] = message

        # Check if question mark is present
        self.dict_result["is_question"] = self._check_if_question_mark_present(message)

        return self.dict_result


class HumanCritic(Critic):
    """A critic to evaluate the human responses.

    Args:
        config: Config
        verbose (bool): prints out buffer text highlighted
    """

    def __call__(self, message: str) -> str:
        """This is the main function that is called to handle a user message and perform an metacritic analysis
        It return a dictionary of values.
        Args:
            ai_message (str): The user's message.
        Returns:
            dict: A dictionary of values.
        """

        self.inputs.append(message)
        self.dict_result["message"] = message

        # Check if question mark is present
        self.dict_result["is_question"] = self._check_if_question_mark_present(message)

        # Check if the user is saying goodbye
        self.dict_result["metric_goodbye"] = self._get_metric_goodbye(message)

        # Determine sentiment of the user's message
        self.dict_result["sentiment"] = self._get_sentiment_label_of_text(message)

        return self.dict_result
