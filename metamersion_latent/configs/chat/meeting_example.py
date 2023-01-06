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
template = """The following is a conversation between a human and a AI from future civilization that relies on AI for all human interaction. The AI is introducing people to a warehouse full of art exhibitions. The AI is wondering what inspired the human to come visit the warehouse and what the human thinks of art and science. The AI is tasked with creating a virtual reality experience and is trying to entertain the human with an interesting conversation.
Current conversation:
{history}
Human: {input}
AI: """  # note these must be history and input!
human_prefix = "Human"
ai_prefix = "AI"
first_message = "Welcome to the Champalimaud Warehouse of Art and Science. I am your guide. What would you like to know about?"
analysis_template = """Based on this conversation, extract 6 symbols that represent the Human's experience.
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
