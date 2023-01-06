import os

import requests
from dotenv import find_dotenv, load_dotenv
from langchain.chains import LLMChain
from langchain.llms.loading import load_llm_from_config
from langchain.prompts.few_shot import FewShotPromptTemplate
from langchain.prompts.prompt import PromptTemplate

from metamersion_latent.llm.config import Config


def extract_concepts_from_analysis(analysis_summary: str, config: Config) -> list:
    """Extract concepts from a summary of the analysis with numbered sentences.
    Args:
        analysis_summary (str): A summary of the analysis with numbered sentences.
    Returns:
        list: A list of concepts.
    """
    load_dotenv(find_dotenv(), verbose=False)  # load environment variables

    example_prompt = PromptTemplate(
        input_variables=["statement", "concept"],
        template="Statement: {statement}\n{concept}",
    )

    prompt = FewShotPromptTemplate(
        examples=config.concept_examples,
        example_prompt=example_prompt,
        suffix="Statement: {input}",
        input_variables=["input"],
    )

    llm = load_llm_from_config(config.prompter_model)
    chain = LLMChain(llm=llm, prompt=prompt)
    # Get sentences as list of strings
    list_summary = [x[3:] for x in analysis_summary.split("\n") if x != ""]
    # Extract concepts from each sentence
    concepts = []
    for sentence in list_summary:
        output = chain.run(sentence)
        # get rid of any \n
        output = output.replace("\n", "")
        concepts.append(output)
    return concepts


def beautify_concepts_to_stable_diffusion_prompts(concepts: list) -> list:
    """Beautify concepts to stable diffusion prompts.
    Args:
        concepts (list): A list of concepts.
    Returns:
        list: A list of stable diffusion prompts.
    """
    load_dotenv(find_dotenv(), verbose=False)  # load environment variables
    API_TOKEN = os.getenv("HUGGINGFACE_API_KEY")
    API_URL = "https://api-inference.huggingface.co/models/Gustavosta/MagicPrompt-Stable-Diffusion"
    headers = {"Authorization": f"Bearer {API_TOKEN}"}

    def query(payload):
        response = requests.post(API_URL, headers=headers, json=payload)
        return response.json()

    prompts = []
    for concept in concepts:
        # call magic prompter
        output = query(
            {
                "inputs": concept,
            }
        )
        output = output[0]["generated_text"]
        # replace . with , and remove the last comma
        output = output.replace(".", ",")[:-1]
        prompts.append(output)
    return prompts
