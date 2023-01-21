from langchain.llms.loading import load_llm_from_config


def prompt(prompt: str, config: dict) -> str:
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
