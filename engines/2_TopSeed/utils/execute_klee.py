import os
import sys
import datetime

import random as rd

from collections import defaultdict

remove_flag = False

configs = {
    'script_path': os.path.abspath(os.getcwd()),
    'b_dir': os.path.abspath('./klee/build/'),
}

# sym_args_for_seed = {
#     "diff"    : "--sym-arg 74 --sym-arg 72 --sym-arg 49 --sym-arg 66 --sym-arg 41 --sym-arg 31 --sym-arg 49 --sym-arg 28 --sym-arg 19 --sym-arg 17 --sym-arg 38 --sym-arg 26 --sym-arg 50 --sym-arg 25 --sym-arg 10 --sym-arg 10 --sym-arg 10 --sym-arg 10 --sym-arg 10 --sym-arg 7 --sym-arg 9 --sym-arg 17 --sym-arg 17 --sym-arg 10 --sym-arg 6 --sym-arg 5 --sym-arg 10 --sym-arg 10 --sym-arg 14 --sym-arg 8 --sym-arg 10 --sym-arg 8 --sym-arg 6 --sym-arg 9 --sym-arg 2 --sym-arg 7 --sym-arg 2 --sym-arg 6 --sym-arg 2 --sym-arg 10 --sym-arg 2 --sym-arg 4 --sym-arg 2 --sym-arg 10 --sym-arg 13 --sym-arg 16 --sym-arg 19 --sym-arg 22 --sym-arg 23 --sym-arg 21 --sym-arg 12 --sym-arg 14 --sym-arg 13 --sym-arg 2 --sym-arg 11 --sym-arg 13 --sym-arg 2 --sym-arg 20 --sym-arg 20 --sym-arg 2 --sym-arg 2 --sym-arg 14 --sym-arg 2 --sym-arg 14 --sym-arg 2 --sym-arg 14 --sym-arg 2 --sym-arg 14 --sym-arg 2 --sym-arg 14 --sym-arg 8 --sym-arg 11 --sym-arg 6",
#     "find"    : "--sym-arg 12 --sym-arg 80 --sym-arg 76 --sym-arg 36 --sym-arg 132 --sym-arg 48 --sym-arg 54 --sym-arg 64 --sym-arg 35 --sym-arg 32 --sym-arg 20 --sym-arg 33 --sym-arg 47 --sym-arg 15 --sym-arg 16 --sym-arg 9 --sym-arg 11 --sym-arg 6 --sym-arg 5 --sym-arg 2 --sym-arg 5 --sym-arg 6 --sym-arg 3 --sym-arg 14 --sym-arg 6 --sym-arg 7 --sym-arg 5 --sym-arg 2 --sym-arg 6 --sym-arg 5 --sym-arg 2 --sym-arg 5 --sym-arg 6 --sym-arg 2 --sym-arg 5 --sym-arg 3 --sym-arg 2 --sym-arg 5 --sym-arg 5 --sym-arg 2 --sym-arg 5 --sym-arg 5 --sym-arg 2 --sym-arg 6 --sym-arg 9 --sym-arg 2 --sym-arg 6 --sym-arg 11 --sym-arg 1 --sym-arg 2 --sym-arg 1 --sym-arg 5 --sym-arg 5 --sym-arg 2 --sym-arg 5 --sym-arg 5 --sym-arg 2 --sym-arg 5 --sym-arg 9 --sym-arg 1 --sym-arg 1",
#     "gawk"    : "--sym-arg 328 --sym-arg 568 --sym-arg 94 --sym-arg 164 --sym-arg 190 --sym-arg 162 --sym-arg 53 --sym-arg 41 --sym-arg 31 --sym-arg 133 --sym-arg 22 --sym-arg 22 --sym-arg 250 --sym-arg 21 --sym-arg 16 --sym-arg 15 --sym-arg 15 --sym-arg 15 --sym-arg 15 --sym-arg 9 --sym-arg 2 --sym-arg 6 --sym-arg 2 --sym-arg 10",
#     "gcal"    : "--sym-arg 1225 --sym-arg 811 --sym-arg 1106 --sym-arg 1414 --sym-arg 1405 --sym-arg 1210 --sym-arg 365 --sym-arg 128 --sym-arg 439 --sym-arg 571 --sym-arg 47 --sym-arg 37 --sym-arg 33 --sym-arg 1408 --sym-arg 48 --sym-arg 1225 --sym-arg 33 --sym-arg 103 --sym-arg 1408 --sym-arg 1408 --sym-arg 103 --sym-arg 50 --sym-arg 29 --sym-arg 48 --sym-arg 29 --sym-arg 33 --sym-arg 1094 --sym-arg 33 --sym-arg 30 --sym-arg 31 --sym-arg 33 --sym-arg 31 --sym-arg 47 --sym-arg 563 --sym-arg 26 --sym-arg 33 --sym-arg 26 --sym-arg 30 --sym-arg 41 --sym-arg 23 --sym-arg 28 --sym-arg 28 --sym-arg 26 --sym-arg 17 --sym-arg 31 --sym-arg 21 --sym-arg 21 --sym-arg 24 --sym-arg 53 --sym-arg 35 --sym-arg 13 --sym-arg 49 --sym-arg 21 --sym-arg 19 --sym-arg 16 --sym-arg 21 --sym-arg 23 --sym-arg 16 --sym-arg 21 --sym-arg 4 --sym-arg 10 --sym-arg 20 --sym-arg 7 --sym-arg 17 --sym-arg 12 --sym-arg 17 --sym-arg 9 --sym-arg 17 --sym-arg 2 --sym-arg 2 --sym-arg 2 --sym-arg 37 --sym-arg 2 --sym-arg 21 --sym-arg 13 --sym-arg 14 --sym-arg 2 --sym-arg 3 --sym-arg 2 --sym-arg 3 --sym-arg 19 --sym-arg 20 --sym-arg 20 --sym-arg 23 --sym-arg 24 --sym-arg 15 --sym-arg 21 --sym-arg 25 --sym-arg 37 --sym-arg 20 --sym-arg 20 --sym-arg 32 --sym-arg 35 --sym-arg 28 --sym-arg 17 --sym-arg 19 --sym-arg 15 --sym-arg 11 --sym-arg 28 --sym-arg 25",
#     "grep"    : "--sym-arg 240 --sym-arg 10001 --sym-arg 155 --sym-arg 135 --sym-arg 43 --sym-arg 131 --sym-arg 43 --sym-arg 73 --sym-arg 191 --sym-arg 108 --sym-arg 69 --sym-arg 43 --sym-arg 63 --sym-arg 71 --sym-arg 58 --sym-arg 42 --sym-arg 47 --sym-arg 52 --sym-arg 36 --sym-arg 64 --sym-arg 64 --sym-arg 42 --sym-arg 25 --sym-arg 23 --sym-arg 24 --sym-arg 24 --sym-arg 23 --sym-arg 42 --sym-arg 22 --sym-arg 24 --sym-arg 24 --sym-arg 23 --sym-arg 23 --sym-arg 18 --sym-arg 15 --sym-arg 19 --sym-arg 22 --sym-arg 17 --sym-arg 21 --sym-arg 17 --sym-arg 12 --sym-arg 18 --sym-arg 22 --sym-arg 17 --sym-arg 21 --sym-arg 16 --sym-arg 15 --sym-arg 16 --sym-arg 16 --sym-arg 15 --sym-arg 10 --sym-arg 15 --sym-arg 12 --sym-arg 18 --sym-arg 22 --sym-arg 16 --sym-arg 21 --sym-arg 16 --sym-arg 17 --sym-arg 18 --sym-arg 12 --sym-arg 18 --sym-arg 22 --sym-arg 13 --sym-arg 21 --sym-arg 16 --sym-arg 12 --sym-arg 9 --sym-arg 12 --sym-arg 15 --sym-arg 14 --sym-arg 11 --sym-arg 14 --sym-arg 12 --sym-arg 14 --sym-arg 14 --sym-arg 14 --sym-arg 10 --sym-arg 10 --sym-arg 10 --sym-arg 19 --sym-arg 10 --sym-arg 12 --sym-arg 10 --sym-arg 16 --sym-arg 8 --sym-arg 12 --sym-arg 14 --sym-arg 13 --sym-arg 12 --sym-arg 16 --sym-arg 11 --sym-arg 12 --sym-arg 11 --sym-arg 9 --sym-arg 8 --sym-arg 8 --sym-arg 11 --sym-arg 11 --sym-arg 16 --sym-arg 13 --sym-arg 12 --sym-arg 13 --sym-arg 18 --sym-arg 8 --sym-arg 11 --sym-arg 8",
#     "m4"      : "--sym-arg 52 --sym-arg 31 --sym-arg 32 --sym-arg 145 --sym-arg 22 --sym-arg 16 --sym-arg 17 --sym-arg 17 --sym-arg 27 --sym-arg 13 --sym-arg 11 --sym-arg 27 --sym-arg 11 --sym-arg 12 --sym-arg 16 --sym-arg 22 --sym-arg 12 --sym-arg 23 --sym-arg 28 --sym-arg 21 --sym-arg 30 --sym-arg 6 --sym-arg 13 --sym-arg 6 --sym-arg 5 --sym-arg 5 --sym-arg 5 --sym-arg 5 --sym-arg 5 --sym-arg 5 --sym-arg 5 --sym-arg 5 --sym-arg 5 --sym-arg 5 --sym-arg 5 --sym-arg 5 --sym-arg 5 --sym-arg 5 --sym-arg 5 --sym-arg 5 --sym-arg 5 --sym-arg 5 --sym-arg 5",
#     "sed"     : "--sym-arg 115 --sym-arg 637 --sym-arg 75 --sym-arg 62 --sym-arg 47 --sym-arg 64 --sym-arg 50 --sym-arg 23 --sym-arg 15 --sym-arg 24 --sym-arg 24 --sym-arg 11 --sym-arg 8 --sym-arg 6 --sym-arg 14 --sym-arg 10 --sym-arg 5 --sym-arg 14 --sym-arg 6 --sym-arg 14 --sym-arg 5 --sym-arg 14 --sym-arg 14 --sym-arg 14 --sym-arg 9 --sym-arg 14 --sym-arg 15 --sym-arg 14 --sym-arg 11 --sym-arg 14 --sym-arg 12 --sym-arg 14 --sym-arg 29 --sym-arg 14 --sym-arg 27 --sym-arg 15 --sym-arg 2 --sym-arg 14 --sym-arg 2 --sym-arg 15 --sym-arg 2 --sym-arg 20 --sym-arg 2 --sym-arg 60 --sym-arg 2 --sym-arg 20 --sym-arg 15",
#     "sqlite3" : "--sym-arg 30 --sym-arg 315 --sym-arg 274 --sym-arg 264 --sym-arg 258 --sym-arg 188 --sym-arg 224 --sym-arg 202 --sym-arg 143 --sym-arg 204 --sym-arg 170 --sym-arg 79 --sym-arg 24 --sym-arg 22 --sym-arg 14 --sym-arg 93 --sym-arg 16 --sym-arg 12 --sym-arg 29 --sym-arg 28 --sym-arg 10 --sym-arg 15 --sym-arg 9 --sym-arg 15 --sym-arg 13 --sym-arg 15 --sym-arg 11 --sym-arg 24 --sym-arg 7 --sym-arg 12 --sym-arg 6 --sym-arg 14",
# }

def gen_run_cmd(pconfig, pgm, a_budget, trial, out_dir, seed, with_seed=False, RQ1_activate=False):

    argv = pconfig["sym_args"]
    # argv = argv.replace("--sym-args 0 1 10 --sym-args 0 2 2", sym_args_for_seed[pgm])

    if "sqlite" in pgm:
        pgm = "sqlite3"
    
    if seed == "":
        postfix = " ".join(["",
            pgm + ".bc",
            argv])
    else:
        postfix = " ".join(["",
            "-seed-file=" + seed,
            pgm + ".bc",
            argv])
    
    run_cmd_list = [configs['b_dir']+"/bin/klee"]

    # For Seeding Human Test dir
    if with_seed:
        seed_dir = f"/root/empirical/engines/run/seeds/{pgm}"
        seeds = [f"--seed-file={seed_dir}/{seed}" for seed in os.listdir(seed_dir) if seed.endswith(".ktest")]
        selected = rd.sample(seeds, 10)
        
        # seed_args = ["--allow-seed-extension", "--allow-seed-truncation", f"--seed-dir={seed_dir}"]
        seed_args = ["--allow-seed-extension", "--allow-seed-truncation", "--seed-time=5s"] + selected
    else:
        seed_args = list()
    

    if RQ1_activate:
        hseeds_options = [
            f"--seed-args-file=/root/empirical/engines/run/RQ1_seed_args/seed_args/{pgm}.txt", 
            f"--seed-args-log={out_dir}/seed_args_hit.log",
            "--seed-args-max-combinations=10000"
        ]
    else:
        hseeds_options = list()

    run_cmd = " ".join(run_cmd_list + seed_args + hseeds_options + ["-only-output-states-covering-new", "--simplify-sym-indices", "--output-module=false",
                        "--output-source=false", "--output-stats=false", "--disable-inlining", 
                        "--optimize", "--use-forked-solver", "--use-cex-cache", "--libc=uclibc", 
                        "--posix-runtime", "-env-file=" + configs['b_dir'] + "/../test.env",
                        "--max-sym-array-size=4096", "--max-memory-inhibit=false",
                        "--switch-type=internal", "--use-batching-search", 
                        "--batch-instructions=10000", "--write-kqueries",
                        "--watchdog",
                        "-max-time=" + a_budget,  
                        f"{postfix}"
                    ]) 
    print(run_cmd)
    return run_cmd

def running_function(pconfig, pgm, iter_dir, trial, total_time, init_time, a_budget, seed, with_seed, RQ1_activate):
    global remove_flag

    group_dir = configs["top_dir"] + "/obj_llvm"
    os.system(" ".join(["cp -rf", pconfig['pgm_dir'] + "*", group_dir]))

    tc_location = group_dir + "/" + pconfig['exec_dir']
    os.chdir(tc_location)

    out_dir = os.path.join(tc_location, "klee-out-0")
    run_cmd = gen_run_cmd(pconfig, pgm, a_budget, trial, out_dir, seed, with_seed, RQ1_activate) # klee command & log
    
    with open(os.devnull, 'wb') as devnull:
        os.system(run_cmd) # klee execution

    info_file = open(tc_location + "/klee-out-0/info", 'a')
    info_file.write("File : " + configs["script_path"] + "/" + sys.argv[0] + "\n")
    info_file.close()

    os.system(" ".join(["mv klee-out-0", iter_dir]))
    os.chdir(configs['script_path'])

def run(pconfig, pgm, trial, total_time, init_time, a_budget, ith_trial, seed="", with_seed=False, RQ1_activate=False):
    global configs
    configs['top_dir'] = os.path.abspath("./experiments_exp_" + pgm + "/#" + str(ith_trial) + "experiment/")

    iter_dir = "/".join([configs['top_dir'], "iteration_" + trial])
    os.makedirs(iter_dir)    

    running_function(pconfig, pgm, iter_dir, trial, total_time, init_time, a_budget, seed, with_seed, RQ1_activate)
