# Copyright 2022 Lunar Ring. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os, sys
sys.path.append("../../../latentblending")
import torch
torch.backends.cudnn.benchmark = False
import numpy as np
import warnings
warnings.filterwarnings('ignore')
import warnings
import torch
from tqdm.auto import tqdm
from PIL import Image
import torch
from movie_util import MovieSaver
from typing import Callable, List, Optional, Union
from latent_blending import LatentBlending, add_frames_linear_interp
from stable_diffusion_holder import StableDiffusionHolder
torch.set_grad_enabled(False)

def txt_load(fp_txt):
    with open(fp_txt, "r") as myfile:
        lines = myfile.readlines()
    lines= [l.split("\n")[0] for l in lines]
        
    return lines

#%% First let us spawn a stable diffusion holder
device = 'cuda'
fp_ckpt = "../../../stable_diffusion_models/ckpt/v2-1_768-ema-pruned.ckpt"
fp_config = '../../../latentblending/configs/v2-inference-v.yaml'
sdh = StableDiffusionHolder(fp_ckpt, fp_config, device)

    
#%% Let's setup the multi transition
fp_prompts = '/home/lugo/latentblending/prompts.txt'
fps = 30
duration_single_trans = 15
quality = 'medium'
depth_strength = 0.5 #Specifies how deep (in terms of diffusion iterations the first branching happens)

# Specify a list of prompts below
list_prompts = txt_load(fp_prompts)
list_prompts = [l for l in list_prompts if len(l) > 10]
print(f"found {len(list_prompts)} prompts. generating movie now")

# You can optionally specify the seeds
list_seeds = None

lb = LatentBlending(sdh)
lb.load_branching_profile(quality=quality, depth_strength=depth_strength)
lb.set_negative_prompt("frame, ugly")
lb.set_width(768)

fp_movie = f"movie_{lb.sdh.width}px.mp4"

lb.run_multi_transition(
        fp_movie, 
        list_prompts, 
        list_seeds=None, 
        fps=fps, 
        duration_single_trans=duration_single_trans
    )


