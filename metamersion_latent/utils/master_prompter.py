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
    # Get sentences as list of strings from numbered summary
    split_text = analysis_summary.split("\n")
    list_summary = []
    for text in split_text:
        if len(text) > 30:  # stupid heuristic
            # get rid of everything behind the colon
            text = text.split(":")[-1]
            # get rid of leading space
            text = text[1:]
            list_summary.append(text)
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


def prompts_to_txt_file(prompts: list, filepath: str):
    """Save prompts to a txt file.
    Args:
        prompts (list): A list of prompts.
        filename (str): The filename to save the prompts to.
    """

    # make a directory if it doesn't exist
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, "w") as f:
        for prompt in prompts:
            f.write(prompt + "\n")
