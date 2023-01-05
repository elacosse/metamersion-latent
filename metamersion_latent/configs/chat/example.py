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
memory_type = "Summary"  # "Buffer" "BufferWindow" "Summary"
window_size = 3
initialization_message = """
    Please provide the email address you signed up for the event with.
"""
template = """The following is a friendly conversation between a human and an AI. The AI is talkative and provides lots of specific details from its context. If the AI does not know the answer to a question, it truthfully says it does not know.
Current conversation:
{history}
Human: {input}
AI: """  # note these must be history and input!
human_prefix = "Human: "
ai_prefix = "AI: "
first_message = """What would you like to talk about with me?"""
