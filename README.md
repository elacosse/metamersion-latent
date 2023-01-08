# Metamersion Latent

## Installation
Install all requirements via pip:
```bash
pip install -r requirements.txt
```


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
python metamersion_latent/tools/chatbot.py -c metamersion_latent/configs/chat/example.py -v
``` 

##### Customizing the configuration
```python
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
Therapist: """
human_prefix = "Client: "
ai_prefix = "Therapist: "
first_message = """What would you like to talk about with me?"""
```
Different kinds of memory for the chat are available:
* **Summary**, a summarized text of the current conversation in buffer
* **Buffer**, the entire current conversation
* **BufferWindow**, a running window of the last **window_size** conversation interactions.
