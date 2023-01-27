# FewShot GPT-3 - is it a goodbye?

openai_model = "text-ada-001"

model = {
    "model_name": openai_model,
    "temperature": 0.7,
    "max_tokens": 1024,
    "top_p": 1.0,
    "frequency_penalty": 0.5,
    "presence_penalty": 0.5,
    "n": 1,
    "best_of": 1,
    "request_timeout": None,
    "_type": "openai",
}

goodbye_examples = [
    "Bye",
    "Goodbye",
    "See you later",
    "Catch you later",
    "OK Ciao",
    "See you soon",
]

examples = [
    {"statement": "Goodbye!", "answer": "True"},
    {"statment": "See you later!", "answer": "True"},
    {"statment": "No", "answer": "False"},
    {"question": "Yes", "answer": "No"},
]
