import os
import time

import random as rd

configs = {
	'root_dir': os.path.abspath(os.getcwd()),
    'klee_build_dir': os.path.abspath('klee/build/'),
}

search_options = {
    "batching" : "--use-batching-search --batch-instructions=10000",
    "branching" : "--use-branching-search",
}

def stgy_handler(top_dir, iteration, weight_idx):
    if iteration == 0:
        return "random-path --search=nurs:covnew"
    return f"auto --feature={top_dir}/features/{iteration}.f --weight={top_dir}/weight/iteration-{iteration}/{weight_idx}.w"
    
class klee_executor:
    def __init__(self, pconfig, top_dir, options):
        self.pconfig = pconfig
        self.pgm = pconfig["pgm_name"]
        self.top_dir = top_dir
        self.n_scores = options.n_scores
        self.small_time = options.small_time
        self.main_option = options.main_option
        self.bin_dir = os.path.abspath('klee/build/bin')
        self.llvm_dir = f"{self.top_dir}/obj-llvm/{self.pconfig['exec_dir']}"

        self.bk_data = {
            "bison"   : {"root_dir" : "bison",     "llvm_version" : "3.8",    "depth" : 1, "src" : "src"},
            "diff"    : {"root_dir" : "diffutils", "llvm_version" : "3.7",    "depth" : 1, "src" : "src"},
            "find"    : {"root_dir" : "findutils", "llvm_version" : "4.7.0",  "depth" : 1, "src" : "find"},
            "gawk"    : {"root_dir" : "gawk",      "llvm_version" : "5.1.0",  "depth" : 0, "src" : ""},
            "gcal"    : {"root_dir" : "gcal",      "llvm_version" : "4.1",    "depth" : 1, "src" : "src"},
            "grep"    : {"root_dir" : "grep",      "llvm_version" : "3.6",    "depth" : 1, "src" : "src"},
            "m4"      : {"root_dir" : "m4",        "llvm_version" : "1.4.18", "depth" : 1, "src" : "src"},
            "sed"     : {"root_dir" : "sed",       "llvm_version" : "4.8",    "depth" : 1, "src" : "sed"},
            "sqlite" : {"root_dir" : "sqlite",    "llvm_version" : "3.33.0", "depth" : 0, "src" : ""},
        }
    
    def gen_run_cmd(self, iteration, weight_idx , klee_max_time, program, with_seed, RQ1_activate):
        symbolic_args = self.pconfig["sym_options"]
        
        search_key = "batching"
        if self.pgm in ["find", "sqlite3"]:
            search_key = "branching"

        if program in ["sqlite"]:
            llvm_path = f'/root/benchmarks/{self.bk_data[program]["root_dir"]}/obj-llvm/{self.bk_data[program]["src"]}/{program}3.bc'
        else:
            llvm_path = f'/root/benchmarks/{self.bk_data[program]["root_dir"]}-{self.bk_data[program]["llvm_version"]}/obj-llvm/{self.bk_data[program]["src"]}/{program}.bc'

        search_stgy = stgy_handler(self.top_dir, iteration, weight_idx)
        if program in ["sqlite"]:
            program = "sqlite3"

        if with_seed:
            seed_dir = f"/root/empirical/engines/run/seeds/{program}"
            seeds = [f"--seed-file={seed_dir}/{seed}" for seed in os.listdir(seed_dir) if seed.endswith(".ktest")]
            selected = rd.sample(seeds, 10)
            # seed_args = ["--allow-seed-extension", "--allow-seed-truncation", f"--seed-dir={seed_dir}"]
            seed_args = ["--allow-seed-extension", "--allow-seed-truncation", "--seed-time=5s"] + selected
        else:
            seed_args = list()

        if RQ1_activate:
            hseeds_options = [
                f"--seed-args-file=/root/empirical/engines/run/RQ1_seed_args/seed_args/{program}.txt", 
                f"--seed-args-log={self.top_dir}/result/iteration-{iteration}/{weight_idx}/seed_args_hit.log",
                "--seed-args-max-combinations=10000"
            ]
        else:
            hseeds_options = list()
        

        klee_options = ["-only-output-states-covering-new", "--simplify-sym-indices", "--output-module=false",
                        "--output-source=false", "--output-stats=false", "--disable-inlining", "--write-kqueries", 
                        "--optimize", "--use-forked-solver", "--use-cex-cache", "--libc=uclibc", "--ignore-solver-failures",
                        "--posix-runtime", f"-env-file={configs['klee_build_dir']}/../test.env",
                        "--max-sym-array-size=4096", "--max-memory-inhibit=false",
                        "--switch-type=internal", search_options[search_key], 
                        f"--watchdog -max-time={klee_max_time} --search={search_stgy} --output-dir={self.top_dir}/result/iteration-{iteration}/{weight_idx}"]

        cmd = [self.bin_dir+"/klee"] + klee_options + seed_args + [llvm_path, symbolic_args, "1>/dev/null 2>/dev/null"]

        run_cmd = " ".join(cmd)
        print(run_cmd)
        return run_cmd

    def execute_klee(self, iteration, t, program, with_seed=False, RQ1_activate=False):
        print("Execute KLEE in iteration ", iteration)
        remaining_time = t
        os.chdir(self.llvm_dir)
        for weight_idx in range(self.n_scores):
            klee_start_time = time.time()
            run_cmd = self.gen_run_cmd(iteration, weight_idx, min(remaining_time, self.small_time), program, with_seed, RQ1_activate) 
            os.system(run_cmd)
            remaining_time -= int(time.time()-klee_start_time)
            if remaining_time <= 0:
                break
        os.system(f"ls -l --time-style full-iso {self.top_dir}/result/iteration-{iteration}/*/*.ktest > {self.top_dir}/result/iteration-{iteration}/time_result 2>/dev/null")
        os.chdir(self.top_dir)

