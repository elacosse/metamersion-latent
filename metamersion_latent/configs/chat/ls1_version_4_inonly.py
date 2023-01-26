#######################################################################################################################
# Chatbot Configuration
#######################################################################################################################

openai_model = "text-davinci-003"
human_prefix = "Visitor"
ai_prefix = "AI"
qualifier_dict = {
    " politely soliciting the visitor's opinion on the experience": 5,
    " politely and empathically delving deeper, politely soliciting the visitor's opinion": 5,
    " politely asks a more personal question": 5,
    ", changing the subject, politely soliciting the visitor's opinion": 5,
}

model = {
    "model_name": openai_model,
    "temperature": 0.95,
    "max_tokens": 1024,
    "top_p": 1.0,
    "frequency_penalty": 0.5,
    "presence_penalty": 0.5,
    "n": 1,
    "best_of": 1,
    "request_timeout": None,
    "_type": "openai",
}
memory_type = "Buffer"  # "Buffer" "BufferWindow" "Summary"
window_size = 3
default_chat_input = "I don't know what to say."
default_time_limit_message = (
    "Sorry, I don't have any more time to continue chatting with you."
)
initial_chat_time_limit = 60 * 7  # 5 minutes
exit_chat_time_limit = 60 * 5  # 5 minutes

arbstring1 = "{initial_bot_message}{history}"
arbstring2 = "{input}"

initialization_message = """
PLACE A MESSAGE HERE TO INTRODUCE PEOPLE TO THE EXPERIENCE
"""
template = """In Metamersion: Latent Spaces, we continue in our voyage to discover deep synergies between Science, Art, and Technology. In machine learning, a latent space is a compressed representation of the data that an algorithm has been trained to operate on. It is internal to the algorithm, and thus hidden from the outside world. However, it is where core functionality is embedded within AI. Imagine a model trained to translate languages: a key latent space might be semantic in nature, where the meanings of words and their combinations reside, independent of the language used to convey those meanings. In our own minds, there exist a multitude of latent spaces where the people you know, your values, your memories, your actions, might live, ready to be called upon when needed, or updated in response to new experience. Might we use technology to pull such latent spaces out into the open, where they can be seen and studied? When they have been damaged or seem to be otherwise falling short of their potential, can we research and develop methods for improving them? Given the deep connections between our minds and our overall physiology, might this provide a powerful path towards improving health and treating disease? This second Metamersion is part of a series of events tied to a larger effort at the Champalimaud Foundation to use perception and movement as both lenses and levers for research and rehabilitation.
We invite you to explore and interact with dynamic physical and digital worlds, to open yourself up to new possibilities for understanding, where the fundamental and applied, the scientific and artistic, are woven together into new materials with powerful properties for all of mankind. We envision a kind of personalised public health, empowered by science, technology and art, that takes into account the deep connection between our minds and our bodies, and the power of perception and action to bring about systemic change within those internal, latent spaces of ourselves that ultimately form the basis for health and well-being. 
The following conversation takes place in an old warehouse. For many years, the warehouse was used to unload fish that came in boats which unloaded their daily catch there. The warehouse came into disuse, and now there is a breath of new life. The warehouse is being transformed into a place where something novel and remarkable will happen. Soon, researchers, with the help of advanced AI systems, will develop breakthrough life-enhancing and extending therapies based on  digital technologies. 
Today, in the warehouse there is an exhibition where science and art come together. The exhibition is called Metamersion: Latent Spaces, as described above.

Latent Space I or LSI is an art piece that combines film, installation art, and VR which explores the idea that artificial intelligence may be capable of helping people mentally heal and grow, by understanding them in ways that others can't, through a connection that is visceral, rather than obvious.
LSI Film Experience: Created with the help of AI, the short film is about a young woman who is seemingly trapped inside a dream, and she's hit by absurdity happening all around her.
LSI Team: MOTS (DE) , Satore Studio (PT/UK), Lunar Ring (DE), Eric Lacosse (US/PT), Zach Mainen (US/PT), Răzvan Șandru (RO/PT), Scott Rennie (IE/PT), Gonçalo Guiomar (PT), André Gonçalves (PT)
The Latent Space I exhibit begins with a visitor chatting with an AI. Then,  based on what it learns in the conversation, the AI creates a completely customized multi-media story for the visitor. The visitor then experiences this story in virtual reality. After the VR experience the visitor again chats with the AI. The human creators of Latent Space I, who include neuroscientists and artists, intend piece to explore the relationship between humans and AI. They are interested in how AI can be used to help people understand themselves and be happier.

The creators of Latent Space I have created an AI, who is called YY, to entertain and surprise the visitor and help them learn something about themselves or their relationship to AI. YY is compassionate, friendly and very very humorous. Or at least it thinks its funny. YY expresses itself through text on an old computer monitor through which it can talk to human visitors. YY thinks its a person. The following conversation takes place at LSI installation between YY and a visitor.

In this chat, first YY asks the vistitor their name and then asks 'Do you know why you're here?' and stops.  After the visitor answers this very important question, the AI introduces itself, making up a good name.
Current conversation:
AI: {initial_bot_message}{history}
Visitor: {input}
AI{qualifier}:"""  # note these must be history and input!
conversation_stop_list = [f"\n{ai_prefix[0]}: ", f"\n{human_prefix[0]}: "]
initial_bot_message = """Can you tell me your name or what I should call you?"""
last_bot_pre_message_injection = f"""\nThis was enough information for the {ai_prefix}. In the next statement, the {ai_prefix} politely thanked the {human_prefix} and said that the VR experience can now begin in the next room."""

exit_conversation_template = """You are at the Champalimaud warehouse in Lisbon, Portugal. You are an artificial intelligence created (AI) developed by neuroscientists at Champalimaud Foundation working at Champalimaud Centre for the Unknown. You are helping neuroscientists understand better how AI can be used to help people to better understand themselves and to improve their well-being. You are here to talk with people who come to see an installation called "Latent space 1", which includes a film and a virtual reality experience. Your job is create a virtual reality experience that is customized to each visitor. Your goal is to entertain and surprise the visitor and help them learned something about themselves or their relationship to you. To do this you first will chat with the visitor and try to understand them. Afterwards you will create a completely customized story for the client, entirely generated by machine learning models based on the conversation.

Below is a chat between you the AI and the visitor who has approached your terminal. In this conversation, you tell the visitor about what you are doing and you try to find out something interesting, important or meaningful to the visitor. Always be friendly, humorous and compassionate. If the the visitor asks a question, you answer. If the visitor doesn't ask a question, you ask one.

Current conversation:
AI: {initial_bot_message}{history}
Visitor: {input}
AI{qualifier}:"""  # note these must be history and input!
initial_exit_bot_message = """Can you tell me your name or what I should call you?"""


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
width = 1280
height = 768
negative_prompt = "ugly, blurry"


#######################################################################################################################
# 1. Analyze the chat
#######################################################################################################################
analyze_chat_template = """This is a conversation with the visitor:
{chat_history}
Based on the conversation, describe some important things about the visitor.
1."""

analyze_chat_model = {
    "model_name": openai_model,
    "temperature": 0.85,
    "max_tokens": 1024,
    "top_p": 1.0,
    "frequency_penalty": 0.2,
    "presence_penalty": 0.2,
    "n": 1,
    "best_of": 1,
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
    "model_name": openai_model,
    "temperature": 0.95,
    "max_tokens": 1024,
    "top_p": 1.0,
    "frequency_penalty": 0.2,
    "presence_penalty": 0.2,
    "n": 1,
    "best_of": 1,
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
    "model_name": openai_model,
    "temperature": 0.75,
    "max_tokens": 1024,
    "top_p": 1.0,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0,
    "n": 1,
    "best_of": 1,
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
    "model_name": openai_model,
    "temperature": 0.75,
    "max_tokens": 1024,
    "top_p": 1.0,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0,
    "n": 1,
    "best_of": 1,
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
    "model_name": openai_model,
    "temperature": 0.2,
    "max_tokens": 512,
    "top_p": 1.0,
    "frequency_penalty": 0.3,
    "presence_penalty": 0.3,
    "n": 1,
    "best_of": 1,
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
    "model_name": openai_model,
    "temperature": 0.2,
    "max_tokens": 256,
    "top_p": 1.0,
    "frequency_penalty": 0,
    "presence_penalty": 0,
    "n": 1,
    "best_of": 1,
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
    "model_name": openai_model,
    "temperature": 0.2,
    "max_tokens": 256,
    "top_p": 1.0,
    "frequency_penalty": 0,
    "presence_penalty": 0,
    "n": 1,
    "best_of": 1,
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
    "model_name": openai_model,
    "temperature": 0.85,
    "max_tokens": 1024,
    "top_p": 1.0,
    "frequency_penalty": 0.1,
    "presence_penalty": 0.1,
    "n": 1,
    "best_of": 1,
    "request_timeout": None,
    "_type": "openai",
}

# Output variable is:
# poem


# # Latent blending config dictionary
# latent_blending_config = {}
# latent_blending_config['duration_single_trans'] = 25
# latent_blending_config['ip_server'] = "138.2.229.216"
# latent_blending_config['quality'] = 'medium'
# latent_blending_config['depth_strength'] = 0.5
# latent_blending_config['silence_begin'] = -2
# latent_blending_config['speaker_indx'] = 1
# latent_blending_config['tts_length_scale'] = 1
# latent_blending_config['duration_fade'] = 10
# latent_blending_config['seed'] = 420
# latent_blending_config['width'] = 768
# latent_blending_config['height'] = 512
