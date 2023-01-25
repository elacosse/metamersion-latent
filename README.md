# ⚠️ Metamersion Latent

## Installation
Create your virtual environment easily with **poetry**.
```bash
poetry install
```

## Creating a Chatbot
First, ensure that a **.env** file is present in the root directory with appropriate environment variables.

For instance, if using OpenAI models, the following must be present:
```bash
OPENAI_API_KEY=""
```
Any additional Huggingface and other keys might be needed
```bash
HUGGINGFACE_API_KEY=""
GOOGLE_SHEET_ID=""
STABILITY_HOST="grpc.stability.ai:443"
STABILITY_KEY=""
```

##### Run the chatbot with a configuration file and save the conversation to examples in repository
Configuration file (required): ```-c  metamersion_latent/configs/chat/ls1_version_5.py```
Verbose mode flag: ```-v```
Save to example flag: ```metamersion_latent/examples/chats/{user-name}.py```
To run chatbot with these flags, run
```bash 
python metamersion_latent/tools/chatbot.py -c metamersion_latent/configs/chat/ls1_version_5.py -v -s
```

##### Customizing the chatbot configurations
To customize your chatbot, refer to example configuration files in
```bash
metamersion_latent/configs/chat
```
Different kinds of memory for the chat are available:
* **Summary**, a summarized text of the current conversation in buffer
* **Buffer**, the entire current conversation
* **BufferWindow**, a running window of the last **window_size** conversation interactions.

## Running testing utilities
If we want to run through a battery of __all__ chats in ```metamersion_latent/examples/chats/``` we have a utility for such experiments.

A script ```run_cards.sh``` is available to create an experiment

```bash
./metamersion_latent/tools/run_cards.sh metamersion_latent/examples/chats/ metamersion_latent/configs/chat/ls1_version_4.py data/ls1_version_4
```
There's an extra option to run only on examples from the same configurations that generated them.
To do that, add the ```-p`` flag.



