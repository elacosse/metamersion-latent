prompts = ['first prompt','second prompt','third prompt']
seeds = [123, 456, 768]

fn_base_movie = 'movie_example'

def run_parallel(prompts, seeds):

    with open("run_parallel.sh", 'w+') as f:
        f.writelines('#!/bin/bash\n')
        
        for idx_prompt in range(len(prompts)-1):
            gpu_id = idx_prompt
            p1 = prompts[idx_prompt]
            p2 = prompts[idx_prompt+1]
            s1 = seeds[idx_prompt]
            s2 = seeds[idx_prompt+1]
            f.writelines(f'(CUDA_VISIBLE_DEVICES={gpu_id} python xa_run_blending_terminal.py "{p1}" "{p2}" {s1} {s2} {idx_prompt})& \n')
            
        f.writelines('wait')
    
    rc = subprocess.call(["bash","run_parallel.sh"])
    
    print('run_parallel: finished')
    
    list_fn_output = [fn_base_movie+str(idx)+'.mp4' for idx in range(len(prompts)-1)]
    return list_fn_output


list_fn_output = run_parallel(prompts, seeds)
