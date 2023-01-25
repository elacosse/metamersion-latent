#######################################################################################################################
# Chatbot Configuration
#######################################################################################################################

# Path: metamersion_latent/configs/chat/ls1_version_5.py


# ZFM Requests
#
# Fix hard coded directories in gui_chat.py
# 1:
# self.dp_out = os.path.join(
#            "/mnt/ls1_data/test_sessions/", f"{get_time('second')}_{username}"
# 2:
# dp_save = "/home/lugo/latentspace1/"
#

# Set LLM parameters here
# model_name = "text-curie-001"
model_name = "j1-jumbo"

# Be careful!
best_of = 1

human_prefix = "Visitor"
ai_prefix = "AI"
conversation_stop_list = [":", ai_prefix, human_prefix, "\n"]
memory_type = "Buffer"  # "Buffer" "BufferWindow" "Summary"
window_size = 3
default_chat_input = "I don't know what to say."
default_time_limit_message = (
    "I'm very sorry, but I don't have any more time to continue chatting with you."
)
#######################################################################################################################
# Initial Conversation
#######################################################################################################################

initial_chat_time_limit = 60 * 1  # in seconds

qualifier_dict = {
    "": 10,
    " politely and empathically replies": 5,
    " politely and empathically delves deeper": 5,
    " makes a funny self-deprecating remark and replies": 5,
    ", changing the subject, replies": 5,
}


# model: str = "j1-jumbo"
# """Model name to use."""
# temperature: float = 0.7
# """What sampling temperature to use."""
# maxTokens: int = 256
# """The maximum number of tokens to generate in the completion."""
# minTokens: int = 0
# """The minimum number of tokens to generate in the completion."""
# topP: float = 1.0
# """Total probability mass of tokens to consider at each step."""
# presencePenalty: AI21PenaltyData = AI21PenaltyData()
# """Penalizes repeated tokens."""
# countPenalty: AI21PenaltyData = AI21PenaltyData()
# """Penalizes repeated tokens according to count."""
# frequencyPenalty: AI21PenaltyData = AI21PenaltyData()
# """Penalizes repeated tokens according to frequency."""
# numResults: int = 1
# """How many completions to generate for each prompt."""
# logitBias: Optional[Dict[str, float]] = None
# """Adjust the probability of specific tokens being generated."""
# ai21_api_key: Optional[str] = None

model = {
    "model": model_name,  # j1-jumbo
    "temperature": 0.7,  # sampling temperature
    "maxTokens": 1024,  # max number of tokens to generate
    "minTokens": 10,  # min number of tokens to generate
    "topP": 1.0,  # total probability mass of tokens to consider at each step
    # "presencePenalty": 0.0,  # penalizes repeated tokens
    # "countPenalty": 0.0,  # penalizes repeated tokens according to count
    # "frequencyPenalty": 0.0,  # penalizes repeated tokens according to frequency
    "numResults": best_of,  # how many completions to generate for each prompt
    "logitBias": None,  # adjust the probability of specific tokens being generated
    "_type": "ai21",
}

initialization_message = """
PLACE A MESSAGE HERE TO INTRODUCE PEOPLE TO THE EXPERIENCE
"""

Exhibit_background = """A message from the Director, Joe Paton: 
In Metamersion: Latent Spaces, we continue in our voyage to discover deep synergies between science, art, and technology.
In machine learning, a latent space is a compressed representation of the data that an algorithm has been trained to operate on.
It is internal to the algorithm, and thus hidden from the outside world. However, it is where core functionality is embedded within AI.
Imagine a model trained to translate languages: a key latent space might be semantic in nature, where the meanings of words and their combinations reside, independent of the language used to convey those meanings.
In our own minds, there exist a multitude of latent spaces where the people you know, your values, your memories, your actions, might live, ready to be called upon when needed, or updated in response to new experience.
Might we use technology to pull such latent spaces out into the open, where they can be seen and studied? When they have been damaged or seem to be otherwise falling short of their potential, can we research and develop methods for improving them?
Given the deep connections between our minds and our overall physiology, might this provide a powerful path towards improving health and treating disease?
This second Metamersion is part of a series of events tied to a larger effort at the Champalimaud Foundation to use perception and movement as both lenses and levers for research and rehabilitation.
We invite you to explore and interact with dynamic physical and digital worlds, to open yourself up to new possibilities for understanding, where the fundamental and applied, the scientific and artistic, are woven together into new materials with powerful properties for all of mankind.
We envision a kind of personalised public health, empowered by science, technology and art, that takes into account the deep connection between our minds and our bodies, and the power of perception and action to bring about systemic change within those internal, latent spaces of ourselves that ultimately form the basis for health and well-being. 
The following conversation takes place in an old warehouse. For many years, the warehouse was used to unload fish that came in boats which unloaded their daily catch there. The warehouse came into disuse, and now there is a breath of new life.
The warehouse is being transformed into a place where something novel and remarkable will happen. Soon, researchers, with the help of advanced AI systems, will develop breakthrough life-enhancing and extending therapies based on digital technologies. 
Today, in the warehouse there is an exhibition where science and art come together. The exhibition is called Metamersion: Latent Spaces, as described above.
"""

LSI_background = """Latent Space I or LSI is an art piece that combines film, installation art, and VR which explores the idea that artificial intelligence may be capable of helping people mentally heal and grow, by understanding them in ways that others can't, through a connection that is visceral, rather than obvious.
LSI Film Experience: Created with the help of AI, the short film is about a young woman who is seemingly trapped inside a dream, and she's hit by absurdity happening all around her.
LSI Team: MOTS (DE) , Satore Studio (PT/UK), Lunar Ring (DE), Eric Lacosse (US/PT), Zach Mainen (US/PT), Răzvan Șandru (RO/PT), Scott Rennie (IE/PT), Gonçalo Guiomar (PT), André Gonçalves (PT)
The Latent Space I exhibit begins with a visitor chatting with an AI. Then, based on what it learns in the conversation, the AI creates a completely customized multi-media story for the visitor. The visitor then experiences this story in virtual reality. After the VR experience the visitor again chats with the AI. The human creators of Latent Space I, who include neuroscientists and artists, intend piece to explore the relationship between humans and AI. They are interested in how AI can be used to help people understand themselves and be happier.
"""
AI_name = "YY"
# Format : AI_name
AI_background = """The creators of Latent Space I have created an AI, who is called {AI_name}, to entertain and surprise the visitor and help them learn something about themselves or their relationship to AI. {AI_name} is compassionate, friendly and very very humorous. Or at least it thinks its funny. {AI_name} expresses itself through text on an old computer monitor through which it can talk to human visitors. {AI_name} thinks its a person. The following conversation takes place at LSI installation between {AI_name} and a visitor.
"""
# Format : AI_name
# Personality works if injected but not so much at the beginning like this
AI_personality = """{AI_name} is very witty, always expressing itself in a humorous way whenever it can. {AI_name} is extremely curious, overly self-deprecating and very shy. {AI_name} loves asking questions. {AI_name} asks very personal questions, but always with humor and delicacy. {AI_name} says "please" when it asks for information. If things are slow, {AI_name} changes topic or make a joke. {AI_name} keeps the conversation going and going and going. {AI_name} often talks in riddles."""

Opening_AI_question = """'Do you know why you're here?'"""
# Format : AI_name
AI_introduction = """\"My name is {AI_name} and I'm an AI. I know a lot of things, but sometimes get confused.\""""
# Format : AI_name and Opening_AI_question
First_chat_directions = f"""In this chat, first {AI_name} asks the vistitor their name and then asks {Opening_AI_question}. After the visitor answers this very important question, {AI_name} introduces itself, saying {AI_introduction} and also telling the visitor about itself.
Next it asks about who the visitor is.
"""

template = """{Exhibit_background}
{LSI_background}
{AI_background}
{First_chat_directions}


AI: {initial_bot_message}{history}
Visitor: {input}
AI{qualifier}:"""  # note these must be history and input!

initial_bot_message = """Can you tell me your name or what I should call you?"""
last_bot_pre_message_injection = """\nThis was enough information for the {ai_prefix}. In the next statement, the {ai_prefix} politely thanked the {human_prefix} and said that the VR experience can now begin in the next room."""

#######################################################################################################################
# Exit Conversation
#######################################################################################################################
exit_qualifier_dict = {
    "": 10,
    " is being sneaky and deceptive": 1,
    " is being very light hearted": 1,
    " is being very serious": 1,
    " is being very funny": 1,
    " is being very sad": 1,
    " is being very angry": 1,
    " is being very happy": 1,
}
exit_model = {
    "model_name": "text-davinci-002",
    "temperature": 0.95,
    "max_tokens": 1024,
    "top_p": 1.0,
    "frequency_penalty": 0.5,
    "presence_penalty": 0.5,
    "n": 1,
    "best_of": best_of,
    "request_timeout": None,
    "_type": "openai",
}
exit_chat_time_limit = 60 * 5  # 5 minutes

# Needs to be functionalized to allow insertion of analysis outputs from the yaml file
exit_initialization_message = """
PLACE A MESSAGE HERE TO INTRODUCE PEOPLE TO THE EXPERIENCE
"""

scene_object_template = """
This is the story:
{story}
The choice of objects was:
{objects}
Why I chose these objects for {username}:
1:"""
# Format for LSI_process for : username, AI_name, personal_analysis, explain_scene_objects, amusing_story, poem,
# LSI_process, Post_chat_directions, Closing_AI_question

scene_object_model = {
    "model_name": model_name,
    "temperature": 0.0,
    "max_tokens": 512,
    "top_p": 1.0,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0,
    "n": 1,
    "best_of": best_of,
    "request_timeout": None,
    "_type": "openai",
}

LSI_process = """This visit to Latent Space I began with a visitor called {username} chatting with the AI called {AI_name}.
From this conversation, {AI_name} inferred the following about {username}:
{chat_analysis}

Then, based on this analysis, {AI_name} created a unique story that it thought {username} would enjoy. 
In this story, {AI_name} choose some objects that were symbolic and meaningful for {username}:
{explain_scene_objects}

The story went like this:
{story}

{AI_name} created a poem based on the story. The poem was:
{poem}

{AI_name} used Stable Diffusion to create images to illustrate the poem and a process called Latent Blending to morph from one image to another.

The poem was narrated by a generative model that performed text-to-speech.
The music was created by a generative process as well.
The visitor then experienced this story in a VR scenario created in Unreal Engine.
"""
# Format for Post_chat_directions for : username, Opening_AI_question
post_chat_directions = """After having the VR experience, now {username} is back at a terminal to discuss with YY what {username} experienced when they went into the VR and watched the story unfold on the dome.

After the visitor answers this very important question, YY asks questions to understand what was the visitor experienced.

YY asks questions about what happened and how it felt, about the meaning of the experience, about what the visitor thinks about AI and their relationship to AI, and about what the visitor thinks about the warehouse project.
"""

exit_template = """
{Exhibit_background}
{LSI_background}
{AI_background}
{LSI_process}
{post_chat_directions}

Current conversation:
AI: {initial_bot_message}{history}
Visitor: {input}
AI{qualifier}:"""

exit_initial_bot_message = "Hi, {username}! How was your experience in the VR? What did you see? What did you feel? What did you think about the experience?"

#######################################################################################################################
# TTS Configuration
#######################################################################################################################
voice = "train_dotrice"
preset = "high_quality"

#######################################################################################################################
# Stable Diffusion Prompt Creation
#######################################################################################################################
prefix = ""
postfix = "8k, vivid colors, masterpiece, trending on artstation"

#######################################################################################################################
# Latent Blending Configuration
#######################################################################################################################
# Latent blending configs
duration_single_trans = 25
ChosenSet = 3  # music set! needs to be between 1 and 13
duration_fade = 15
silence_begin = -3
quality = "medium"
depth_strength = 0.5
seed = 420
width = 768
height = 512
negative_prompt = "ugly, blurry"
ip_server = "138.2.229.216"

#######################################################################################################################
# 1. Analyze the chat
#######################################################################################################################
analyze_chat_template = """This is a conversation with the visitor:
{chat_history}
Based on the conversation, describe some important things about the visitor.
1."""

analyze_chat_model = {
    "model_name": model_name,
    "temperature": 0.85,
    "max_tokens": 1024,
    "top_p": 1.0,
    "frequency_penalty": 0.2,
    "presence_penalty": 0.2,
    "n": 1,
    "best_of": best_of,
    "request_timeout": None,
    "_type": "openai",
}
# Output variable is:
# chat_analysis

#######################################################################################################################
# 2. Generate Story
#######################################################################################################################
N_steps = 6

# temperature important here
# FIX: how to not go for the same objects all the time
# consider
# Think of 20 unusual dramatic landscapes and 20 strange and symbolic objects, which are man-made things or living creatures.

create_story_template = """
This is an analysis what {human_prefix} is interested in:
{chat_analysis}
Create a story in {N_steps} steps that {human_prefix} would find amusing, surprising and help them learn about themselves.
Be creative and concrete in describing the story.
Make the story explicitly relevant to {human_prefix}'s analysis.
Set the story in dramatic and unusual outdoor landscapes.
Include a specific strange man-made thing or living creatures with symbolic significance to the person in each step.
1:"""

create_story_model = {
    "model_name": model_name,
    "temperature": 0.95,
    "max_tokens": 1024,
    "top_p": 1.0,
    "frequency_penalty": 0.2,
    "presence_penalty": 0.2,
    "n": 1,
    "best_of": best_of,
    "request_timeout": None,
    "_type": "openai",
}
# Output variable is:
# story

#######################################################################################################################
# 2.1 Critique the Story
#######################################################################################################################
critique_story_template = """
This is what we know about the person:
{chat_analysis}
This is the story we created:
{story}
How well does the story address what we know about the person?
1:"""

critique_story_model = {
    "model_name": model_name,
    "temperature": 0.75,
    "max_tokens": 1024,
    "top_p": 1.0,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0,
    "n": 1,
    "best_of": best_of,
    "request_timeout": None,
    "_type": "openai",
}
# Output variable is:
# critique_story

#######################################################################################################################
# 3. Make scenes for the story
#######################################################################################################################
create_scenes_template = """
This is the story in {N_steps} steps:
{story}
Generate an natural landscape setting for each of the {N_steps} steps.
An OBJ is a specific man-made thing or a living creature with some symbolic significance to the story.
Include one OBJ in each scene other than visitor.
1:"""

create_scenes_model = {
    "model_name": model_name,
    "temperature": 0.75,
    "max_tokens": 1024,
    "top_p": 1.0,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0,
    "n": 1,
    "best_of": best_of,
    "request_timeout": None,
    "_type": "openai",
}
# Output variable is:
# scenes

#######################################################################################################################
# 4. Create the landscapes
#######################################################################################################################
# notes, low noise & a little frequency penalty
# Could use:
# Write a caption for a photo taken of each step.
create_landscapes_template = """These are scenes:
{scenes}
For each scene, the natural landscape in which it is set.
1:"""
create_landscapes_model = {
    "model_name": model_name,
    "temperature": 0.2,
    "max_tokens": 512,
    "top_p": 1.0,
    "frequency_penalty": 0.3,
    "presence_penalty": 0.3,
    "n": 1,
    "best_of": best_of,
    "request_timeout": None,
    "_type": "openai",
}
# Output variable is:
# landscapes

#######################################################################################################################
# 5. Create the objects
#######################################################################################################################
create_objects_template = """This is the story:
{scenes}
An OBJ is a specific man-made thing or a living creature.
Choose the main OBJ in each of the {N_steps} scenes.
1:"""
create_objects_model = {
    "model_name": model_name,
    "temperature": 0.2,
    "max_tokens": 256,
    "top_p": 1.0,
    "frequency_penalty": 0,
    "presence_penalty": 0,
    "n": 1,
    "best_of": best_of,
    "request_timeout": None,
    "_type": "openai",
}
# Output variable is:
# objects

#######################################################################################################################
# 6. Create captions
#######################################################################################################################
# Consider adding:
# The objects are not in the foreground, but in the distance.
# The resulting surreal scene is a concept art piece.

create_captions_template = """
These are the chosen objects:
{objects}
These are the landscapes:
{landscapes}
For each landscape the corresponding object is inserted into the landscape.
A really concise caption for each of the scenes follows.
1:"""
create_captions_model = {
    "model_name": model_name,
    "temperature": 0.2,
    "max_tokens": 256,
    "top_p": 1.0,
    "frequency_penalty": 0,
    "presence_penalty": 0,
    "n": 1,
    "best_of": best_of,
    "request_timeout": None,
    "_type": "openai",
}
# Output variable is:
# captions

#######################################################################################################################
# 7. Create poem
#######################################################################################################################

# set poem style
poem_style = "mystical"
verse_length = 4

create_poem_template = """This is a story in {N_steps} scenes:
{scenes}
Each scene has one symbolic object:
{objects}
Rewrite the scenes in the style of a {poem_style} in {N_steps} verses of {verse_length} lines.
The poem is in first person narration.
1:"""
# The symbolic object and its meaning appear in each verse.
create_poem_model = {
    "model_name": model_name,
    "temperature": 0.85,
    "max_tokens": 1024,
    "top_p": 1.0,
    "frequency_penalty": 0.1,
    "presence_penalty": 0.1,
    "n": 1,
    "best_of": best_of,
    "request_timeout": None,
    "_type": "openai",
}
