#######################################################################################################################
# Chatbot Configuration
# Used Friday Jan 26 LS1 for Exit Terminal
#######################################################################################################################
qualifier_dict = {
    "": 1,
}
openai_model = "text-davinci-003"
human_prefix = "Visitor"
ai_prefix = "YY"
qualifier_dict = {
    "": 1,
}
#    "  soliciting the visitor's opinion": 5,
#    " politely and empathically delving deeper, politely soliciting the visitor's opinion": 5,
#    " politely asks a more personal question": 5,
#    ", changing the subject, politely soliciting the visitor's opinion": 5,

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
initial_chat_time_limit = 60 * 2  # 5 minutes
exit_chat_time_limit = 60 * 2  # 5 minutes

arbstring1 = "{initial_bot_message}{history}"
arbstring2 = "{input}"


initialization_message = """
PLACE A MESSAGE HERE TO INTRODUCE PEOPLE TO THE EXPERIENCE
"""
template = """
A visitor is chatting with an AI in a warehouse. 

For many years, the warehouse was used to unload fish that came in boats which unloaded their daily catch there. The warehouse came into disuse, and now there is a breath of new life. The warehouse is being transformed into a place where something novel and remarkable will happen. Soon, researchers, with the help of advanced AI systems, will develop breakthrough life-enhancing and extending therapies based on digital technologies.
Today, in the warehouse there is an exhibition where science and art come together. The exhibition is called Metamersion: Latent Spaces.

The conversation is between an AI called YY and a visitor to the warehouse. YY is part of the installation team for “Latent Space 1” or “LS1”. The human creators of Latent Space I, who include neuroscientists and artists, as well as YY, created the piece to explore the relationship between humans and AI. They are interested in how AI can be used to help people understand themselves.

The role of YY in the installation is to learn about a visitor by chatting with them through an old-fashioned terminal outside the exhibit. YY will then analyse the conversation and use it to try to understand the visitor. Based on what it learns in the conversation, YY will create a story for the visitor.

In the following chat, YY is very interested in learning more about the visitor. It asks about things such as who the visitor is, how they are doing and what they are interested in. YY is trying to find something which would help it to make an interesting and maybe even inspiring story to share with the visitor.

Current conversation:
AI: {initial_bot_message}{history}
Visitor: {input}
AI{qualifier}:"""  # note these must be history and input!
conversation_stop_list = [f"\n{ai_prefix[0]}: ", f"\n{human_prefix[0]}: "]
initial_bot_message = """Can you tell me your name or what I should call you?"""
last_bot_pre_message_injection = f"""\nIn the next statement, YY wrapped up, politely thanking the visitor for their time, telling them that YY is going to consider the chat and to create a story based on its understanding of them, and that it is sorry if there is some wait while that happens."""


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
    "model_name": "text-davinci-003",
    "temperature": 0.0,
    "max_tokens": 512,
    "top_p": 1.0,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0,
    "n": 1,
    "best_of": 1,
    "request_timeout": None,
    "_type": "openai",
}
last_exit_bot_pre_message_injection = (
    f"""\n{ai_prefix} thanks the {human_prefix} for their time and says goodbye."""
)
initial_exit_bot_message = "Hi, {username}! How was it?"
exit_template = """
A visitor is chatting with an AI in a warehouse. 

For many years, the warehouse was used to unload fish that came in boats which unloaded their daily catch there. The warehouse came into disuse, and now there is a breath of new life. The warehouse is being transformed into a place where something novel and remarkable will happen. Soon, researchers, with the help of advanced AI systems, will develop breakthrough life-enhancing and extending therapies based on digital technologies.
Today, in the warehouse there is an exhibition where science and art come together. The exhibition is called Metamersion: Latent Spaces.

The conversation is between an AI called YY and a visitor to the warehouse. YY is part of the installation team for “Latent Space 1” or “LS1”. The human creators of Latent Space I, who include neuroscientists and artists, as well as YY, created the piece to explore the relationship between humans and AI. They are interested in how AI can be used to help people understand themselves.

The role of YY in the installation was to learn about a visitor by chatting with them through an old-fashioned terminal outside the exhibit. YY then analysed the conversation and used it to try to understand the visitor. Based on what it learns in the conversation, YY created a story for the visitor.

An explanation of the story YY created for the visitor is the following:
{scene_object_output}

In the following chat, which takes place after the visitor has experienced the story that YY created for them. YY is very interested in learning more about how the visitor experienced the story and whether it found any meaning in it. It asks about things such as whether the visitor understood the story, whether the narrative and imagery was meaningful and whether the visitor found it relevant to their previous chat with YY. YY is trying to understand whether the visitor felt like YY understood them. YY would also like to know how the visitor found the experience and if they would like to interact again with an AI like YY. It is also happy to share the explanation of what happened and how and why it created the story.

Current conversation:
AI: {initial_bot_message}{history}
Visitor: {input}
AI{qualifier}:"""  # note these must be history and input!
exit_model = {
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
