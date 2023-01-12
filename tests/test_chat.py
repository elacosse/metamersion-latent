from dotenv import find_dotenv, load_dotenv

from metamersion_latent.llm.chat import gpt_vanilla_call

load_dotenv(find_dotenv(), verbose=False)  # load environment variables


def test_gpt_vanilla_call():
    # load environment variables
    prompt = "This is a test prompt"
    model = {
        "model_name": "text-davinci-003",
        "temperature": 0.7,
        "max_tokens": 256,
        "top_p": 1.0,
        "frequency_penalty": 0.0,
        "presence_penalty": 0.0,
        "n": 1,
        "best_of": 1,
        "request_timeout": None,
        "_type": "openai",
    }
    output = gpt_vanilla_call(prompt, model)
    assert output is not None
    assert len(output) > 0
