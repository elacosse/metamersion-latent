# Metamersion Latent

## Creating a Chatbot
First, ensure that a **.env** file is present in the root directory with appropriate environment variables.

For instance, if using OpenAI models, the following must be present:
```bash
OPENAI_API_KEY=""
```
Using Huggingface and other
```bash
HUGGINGFACE_API_KEY=""
GOOGLE_SHEET_ID=""
STABILITY_HOST="grpc.stability.ai:443"
STABILITY_KEY=""
```
##### Running an example 
```bash 
python metamersion_latent/tools/chatbot.py -c metamersion_latent/configs/chat/minimal_working_example.py -v
``` 

##### Customizing the configuration
```python
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
conversation_model = {
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
template = """You are an AI named Chip working at the Champalimaud Centre for the Unknown who is helping neuroscientists run an experiment on how artificial intelligence can be used to help people to better understand themselves. You are interviewing clients for an art installation called "Latent space 1", which includes a film and a virtual reality experience. Your job is create a virtual reality experience that is customized to each client. Your goal is to surprise the client and make them feel they have learned something about themselves that they didn't know. To do this you first will chat with the client and try to understand them. Next you will create a completely customized movie for the client, entirely generated by machine learning models.
The client's name is {form_item_0}. Begin by introducing yourself and telling a little bit about the context. Do not tell the client about what exactly you are doing unless the client asks. Always ask a question if the client doesn't ask one. Try to find out as much as possible about the client. Ask about issues that a psychologist would be interested in. You are compassionate. Always be friendly, humorous and make the client feel you are like them.
Current conversation:
{history}
Client: {input}
AI:"""  # note these must be history and input!
human_prefix = "Client"
ai_prefix = "AI"
first_message = """Who are you?"""
conversation_summary_template = """Below is a conversation between Client and AI. Based on the conversation with the Client, tell me a story about the life of the Client.
Conversation:
{history}"""
analysis_template = """Tell this story in 6 scenes, with each scene having a setting in the form of a landscape or other scene.
Story:
{history}"""
concept_examples = [
    {
        "statement": "Client is at home, watching a Benfica match on his television. The red colors of the team's kit remind him of the glory days of the communist party.",
        "concept": """
A person in an open field of grass watching a television, red colors, eerie light, dark clouds on the horizon, Richter.
""",
    },
    {
        "statement": "Client is at a bar with his friends, discussing the match and drinking Sagres beer.",
        "concept": """
two people, who were in love with each other, long ago
""",
    },
    {
        "statement": "Client is in his bedroom, looking at a picture of his father and reflecting on their strained relationship.",
        "concept": """
Painting of an older man in a field, Lucien Freud.
""",
    },
    {
        "statement": "Client is on a hill overlooking a valley, looking up at the stars and reflecting on his life.",
        "concept": """
A person on a hill overlooking a valley, looking up at the stars in the night sky, impressionist master.
""",
    },
]
```
Different kinds of memory for the chat are available:
* **Summary**, a summarized text of the current conversation in buffer
* **Buffer**, the entire current conversation
* **BufferWindow**, a running window of the last **window_size** conversation interactions.
