import os
import sys
import argparse

import random as rd


learch_root = "/root/empirical/engines/5_learch/learch"

os.environ["SOURCE_DIR"] = learch_root
os.environ["PYTHONPATH"] = (learch_root + ":" + os.environ.get("PYTHONPATH", ""))

sym_args = {
    "bison"   : "--sym-arg 51 --sym-arg 37 --sym-arg 74 --sym-arg 70 --sym-arg 24 --sym-arg 39 --sym-arg 63 --sym-arg 26 --sym-arg 17 --sym-arg 12 --sym-arg 7 --sym-arg 18 --sym-arg 16 --sym-arg 11 --sym-arg 11 --sym-arg 8 --sym-arg 7 --sym-arg 5 --sym-arg 7 --sym-files 2 900 --sym-stdin 201",
    "diff"    : "--sym-arg 74 --sym-arg 75 --sym-arg 49 --sym-arg 62 --sym-arg 41 --sym-arg 45 --sym-arg 23 --sym-arg 45 --sym-arg 24 --sym-arg 10 --sym-arg 15 --sym-arg 12 --sym-arg 24 --sym-arg 23 --sym-arg 8 --sym-arg 15 --sym-arg 6 --sym-arg 2 --sym-files 2 800 --sym-stdin 19",
    "find"    : "--sym-arg 12 --sym-arg 81 --sym-arg 77 --sym-arg 58 --sym-arg 76 --sym-arg 50 --sym-arg 54 --sym-arg 64 --sym-arg 35 --sym-arg 18 --sym-arg 20 --sym-arg 33 --sym-arg 16 --sym-arg 18 --sym-arg 16 --sym-arg 8 --sym-arg 11 --sym-arg 6 --sym-arg 5 --sym-arg 2 --sym-arg 6 --sym-arg 4 --sym-arg 3 --sym-arg 14 --sym-arg 3 --sym-arg 2 --sym-arg 6 --sym-arg 1 --sym-arg 2 --sym-arg 5 --sym-arg 1 --sym-arg 1 --sym-stdin 31",
    "gawk"    : "--sym-arg 92 --sym-arg 77 --sym-arg 74 --sym-arg 62 --sym-arg 76 --sym-arg 48 --sym-arg 38 --sym-arg 15 --sym-arg 19 --sym-arg 17 --sym-arg 13 --sym-arg 16 --sym-arg 9 --sym-arg 2 --sym-arg 11 --sym-files 5 900 --sym-stdin 81",
    "gcal"    : "--sym-arg 67 --sym-arg 76 --sym-arg 60 --sym-arg 49 --sym-arg 39 --sym-arg 37 --sym-arg 31 --sym-arg 41 --sym-arg 43 --sym-arg 24 --sym-arg 27 --sym-arg 21 --sym-arg 14 --sym-arg 15 --sym-arg 6 --sym-arg 16 --sym-arg 8 --sym-arg 6 --sym-arg 15 --sym-arg 6 --sym-arg 4 --sym-arg 7 --sym-arg 6 --sym-arg 4 --sym-arg 7 --sym-arg 2 --sym-arg 6 --sym-arg 2 --sym-arg 1 --sym-arg 1 --sym-files 3 900 --sym-stdin 480",
    "grep"    : "--sym-arg 33 --sym-arg 85 --sym-arg 85 --sym-arg 35 --sym-arg 56 --sym-arg 53 --sym-arg 67 --sym-arg 21 --sym-arg 32 --sym-arg 19 --sym-arg 17 --sym-arg 43 --sym-arg 33 --sym-arg 16 --sym-arg 16 --sym-arg 4 --sym-arg 2 --sym-arg 4 --sym-arg 2 --sym-arg 4 --sym-arg 1 --sym-files 3 900 --sym-stdin 70",
    "m4"      : "--sym-arg 35 --sym-arg 32 --sym-arg 72 --sym-arg 21 --sym-arg 22 --sym-arg 16 --sym-arg 27 --sym-arg 16 --sym-arg 16 --sym-arg 19 --sym-arg 18 --sym-arg 15 --sym-arg 18 --sym-arg 14 --sym-arg 16 --sym-arg 21 --sym-arg 2 --sym-arg 2 --sym-arg 2 --sym-arg 2 --sym-arg 3 --sym-arg 2 --sym-arg 5 --sym-arg 2 --sym-arg 4 --sym-arg 2 --sym-arg 1 --sym-arg 2 --sym-arg 1 --sym-arg 2 --sym-arg 1 --sym-arg 2 --sym-arg 1 --sym-arg 3 --sym-arg 3 --sym-arg 2 --sym-arg 1 --sym-arg 2 --sym-files 2 300 --sym-stdin 332",
    "sed"     : "--sym-arg 84 --sym-arg 86 --sym-arg 81 --sym-arg 64 --sym-arg 46 --sym-arg 64 --sym-arg 50 --sym-arg 25 --sym-arg 12 --sym-arg 16 --sym-arg 16 --sym-arg 9 --sym-arg 8 --sym-files 2 500 --sym-stdin 77",
    "sqlite3" : "--sym-arg 10 --sym-arg 23 --sym-arg 11 --sym-arg 10 --sym-arg 10 --sym-arg 10 --sym-arg 4 --sym-arg 17 --sym-arg 10 --sym-arg 4 --sym-arg 1 --sym-files 1 30 --sym-stdin 315",
}

benchmarks = {
    "bison"   : {"root_dir" : "bison",     "llvm_version" : "3.8",    "depth" : 1, "src" : "src"},
    "diff"    : {"root_dir" : "diffutils", "llvm_version" : "3.7",    "depth" : 1, "src" : "src"},
    "find"    : {"root_dir" : "findutils", "llvm_version" : "4.7.0",  "depth" : 1, "src" : "find"},
    "gawk"    : {"root_dir" : "gawk",      "llvm_version" : "5.1.0",  "depth" : 0, "src" : ""},
    "gcal"    : {"root_dir" : "gcal",      "llvm_version" : "4.1",    "depth" : 1, "src" : "src"},
    "grep"    : {"root_dir" : "grep",      "llvm_version" : "3.6",    "depth" : 1, "src" : "src"},
    "m4"      : {"root_dir" : "m4",        "llvm_version" : "1.4.18", "depth" : 1, "src" : "src"},
    "sed"     : {"root_dir" : "sed",       "llvm_version" : "4.8",    "depth" : 1, "src" : "sed"},
    "sqlite3" : {"root_dir" : "sqlite",    "llvm_version" : "3.33.0", "depth" : 0, "src" : ""},
}



klee_path = "/root/empirical/engines/5_learch/klee/build/bin/klee"
eval_path = "/root/empirical/engines/5_learch/learch/eval/eval_gen_tests_realworld.sh"

def run_learch(program, llvm_path, output_path, iter_budget, weight_file, with_seed=False, RQ1_activate=False):
    # cmd = f'{eval_path} {program} {llvm_path} {output_path} {iter_budget} "feedforward {weight_file}" "{sym_args[program]}" {"true" if with_seed else "false"}'
    cmd = f'{eval_path} {program} {llvm_path} {output_path} {iter_budget} "feedforward {weight_file}" "{sym_args[program]}" {"true" if with_seed else "false"} {"true" if RQ1_activate else "false"}'
    os.system(cmd)
    print(cmd)


parser = argparse.ArgumentParser()

parser.add_argument("program", choices=list(benchmarks.keys()), help="Benchmark program")
parser.add_argument("time_budget", type=int, help="Total time budget in seconds")
parser.add_argument("--with-seed", action="store_true", help="Run Learch with seeds")
parser.add_argument("--RQ1-activate", action="store_true", help="Run Learch with seeds")

args = parser.parse_args()

program = args.program
time_budget = args.time_budget
with_seed = args.with_seed
RQ1_activate = args.RQ1_activate

if program in ["sqlite3"]:
    llvm_path = f'/root/benchmarks/{benchmarks[program]["root_dir"]}/obj-llvm/{benchmarks[program]["src"]}/{program}.bc'
else:
    llvm_path = f'/root/benchmarks/{benchmarks[program]["root_dir"]}-{benchmarks[program]["llvm_version"]}/obj-llvm/{benchmarks[program]["src"]}/{program}.bc'

if not os.path.exists(f"/root/empirical/engines/5_learch/learch/sandboxes/sandbox_{program}"):
    os.system(f"tar xvf /root/empirical/engines/5_learch/learch/sandbox.tgz -C /root/empirical/engines/5_learch/learch/sandboxes")
    os.system(f"mv /root/empirical/engines/5_learch/learch/sandboxes/sandbox /root/empirical/engines/5_learch/learch/sandboxes/sandbox_{program}")

if not os.path.exists(f"/root/empirical/engines/run/experiments/learch_RQ1_{program}"):
    os.system(f"mkdir /root/empirical/engines/run/experiments/learch_RQ1_{program}")

for i in range(4):
    weight_file = f"/root/empirical/engines/5_learch/learch/train/trained/feedforward_{i}.pt"
    output_path = f"/root/empirical/engines/run/experiments/learch_RQ1_{program}/iteration_{i}"
    run_learch(program, llvm_path, output_path, time_budget // 4, weight_file, with_seed=with_seed, RQ1_activate=RQ1_activate)
