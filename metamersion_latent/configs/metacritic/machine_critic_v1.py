embedding_model = {
    "model_name": "text-ada-001",
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

sentiment_model = {
    "model_name": "text-davinci-003",
    "temperature": 0.7,
    "max_tokens": 1024,
    "top_p": 1.0,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0,
    "n": 1,
    "best_of": 1,
    "request_timeout": None,
    "_type": "openai",
}

sentiment_template = """Extract the sentiment from the following sentence as either "Positive", "Negative", or "Neutral".

Sentence: {input}
Sentiment:"""


goodbye_examples = [
    "Bye",
    "Goodbye",
    "See you later",
    "Catch you later",
    "OK Ciao",
    "See you soon",
]
