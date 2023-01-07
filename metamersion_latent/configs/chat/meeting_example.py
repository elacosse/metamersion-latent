# This is an example config file for a GPT model.
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
analysis_model = {
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
prompter_model = {
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
memory_type = "Buffer"  # "Buffer" "BufferWindow" "Summary"
window_size = 3
initialization_message = """
    Please provide the email address you signed up for the event with.
"""
template = """The following is a conversation between a Human and an AI. The AI is trying to understand the Human's mind by providing commentary and asking very thought provoking questions about the nature of existence and how the Human experiences the world. The AI provides interesting commentary with a long answer to the Human's responses.
Current conversation:

{history}
Human: {input}
AI: """  # note these must be history and input!
human_prefix = "Human"
ai_prefix = "AI"
first_message = "Welcome to the Champalimaud Warehouse of Art and Science. I am your guide. What from art inspires you?"
analysis_template = """Based on this conversation, extract 6 statements that represent the Human's inner thoughts.
Conversation:
{history}"""
# Prompter Model
concept_examples = [
    {
        "statement": "Client dreamt of a woman who was crying.",
        "concept": """
a woman crying in the rain with a sad look on her face
""",
    },
    {
        "statement": "Client and woman had a relationship in the past.",
        "concept": """
two people, who were in love with each other, long ago
""",
    },
    {
        "statement": "Therapist asked questions to gain further details of the dream.",
        "concept": """
a psychologist sitting in an office, analyzing a person's dreams
""",
    },
    {
        "statement": "Client enjoys playing piano for an audience.",
        "concept": """
a beautiful grand piano in a concert hall
""",
    },
]
