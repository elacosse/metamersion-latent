#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Jan  4 11:40:36 2023

@author: lunarring
"""

import os

def txt_load(fp_txt):
    r"""
    Loads txt file from disk
    """
    with open(fp_txt, "r") as myfile:
        lines = myfile.readlines()
    lines= [l.split("\n")[0] for l in lines]
    return lines

def txt_save(fp_txt, list_write, append=False):
    if append:
        mode = "a+"
    else:
        mode = "w"
    with open(fp_txt, mode) as fa:
        for item in list_write:
            fa.write("%s\n" % item)

def construct_prompt_from_file(
        new_input: str, 
        fp_zeroshot: str, 
        split_character="|", 
        pretext_input="input:", 
        prextext_target="summary:"
        ):
    r"""
    Generates a gpt3 prompt on basis of an fp_zeroshot file, e.g. example.txt
    The file has the following structure:
    Example input 1 | Example target 1
    Example input 2 | Example target 2
    Example input 3 | Example target 3
    ...
    e.g. if we want to get a function for making a full sentence based on a word:
    house | The cat was in the house
    car | The car was speeding down the road
    plane | The plane was high in sky
    
    Args:
        new_input: input sample which is the argument for our function.
            in the example above this could be 'cloud' and we would get a sentence
            including a cloud
        fp_zeroshot: file path to the text file including the zero-shot examples
            (as shown above)
        split_character: character that is used to split input and target for each
            zero-shot training sample in fp_zeroshot
        pretext_input: this text will be put in front of each respective input
        prextext_target: this text will be put in front of each respective target
        
            
    """
    assert os.path.isfile(fp_zeroshot), f"fp_zeroshot does not exist: {fp_zeroshot}"
    txt_raw = txt_load(fp_zeroshot)
    
    # split inputs and targets
    list_inputs = []
    list_targets = []
    for x in txt_raw:
        if len(x) < 5: 
            continue
        if "|" not in x:
            continue
        example, target = x.split(split_character)
        example = example.strip()
        target = target.strip()
        
        list_inputs.append(example)
        list_targets.append(target)
    
    # assemble new gpt_prompt
    gpt_prompt = ""
    for i in range(len(list_inputs)):
        gpt_prompt += f"{pretext_input} {list_inputs[i]}\n"
        gpt_prompt += f"{prextext_target} {list_targets[i]}\n"
    
    # insert new example
    gpt_prompt += f"{pretext_input} {new_input}\n"
    gpt_prompt += f"{prextext_target}"
    
    return gpt_prompt

if __name__ == "__main__":
    
    # create an example txt file
    fp_zeroshot = "/tmp/zeroshot.txt"
    list_test = []
    list_test.append("house | The cat was in the house")
    list_test.append("car | The car was speeding down the road")
    list_test.append("plane | The plane was high in sky")
    txt_save(fp_zeroshot, list_test)
    
    # run prompt construction
    prompt = construct_prompt_from_file("cloud", fp_zeroshot)
    
    
    
    