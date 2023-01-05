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
memory_type = "Buffer"  # "Buffer" "BufferWindow" "Summary"
window_size = 3
initialization_message = """
    Please provide the email address you signed up for the event with.
"""
template = """A skilled therapist engages in a conversation with the client using strategies rooted in understanding the world through Girard's mimetic theory. The therapist teaches that the client's desires are a product of a mimetic process in which people imitate models who endow objects with value. The therapist guides the client towards understanding what and who their desires are modeled from.
Current conversation:
{history}
Client: {input}
Therapist: """  # note these must be history and input!
human_prefix = "Client: "
ai_prefix = "Therapist: "
first_message = """What would you like to talk about with me?"""
