from dotenv import find_dotenv, load_dotenv

from metamersion_latent.llm.config import Config
from metamersion_latent.llm.metacritic import HumanCritic, MachineCritic

load_dotenv(find_dotenv(), verbose=False)  # load environment variables


config_path = "metamersion_latent/configs/metacritic/machine_critic_v1.py"
config = Config.fromfile(config_path)
ai_critic = MachineCritic(config)
human_critic = HumanCritic(config)

ai_critic(
    "Alright! Let's start by taking a deep breath, and then diving into the unknown. Are you ready for an adventure?"
)

human_critic("OK, I'm ready.")


print(ai_critic.dict_result)

print(human_critic.dict_result)
