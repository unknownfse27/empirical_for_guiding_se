from pathlib import Path

from subscripts.config_cmd import get_command
from subscripts.run_engine import run
from subscripts.replay import replay


import os
import re
import sys
import glob
import json
import struct
import argparse

import random as rd
import subprocess as sp


parser = argparse.ArgumentParser()

parser.add_argument("--test-setting", type=str, required=True, 
    choices=["base", "seed"], 
    help="Baseline test setting, i.e., base (baseline techniques), seed (guiding with seeds)")

parser.add_argument("--engine", required=True,
    choices=["1_ParaSuit", "2_TopSeed", "3_FeatMaker", "4_KLEE_Q", "5_Symtuner",
        "6_Learch", "7_Symsize", "8_Aaqc", "9_Pending", "10_klee"],
    help="Engines to evaluate, e.g., 9_pending 10_klee")

parser.add_argument("--program", required=True,
    choices=["all", "bison", "diff", "find", "gawk", "gcal", "grep", "m4", "sed", "sqlite3"],
    help="Program to evaluate, e.g., bison grep m4")

parser.add_argument(
    "--run-rq",
    nargs="+",
    required=True,
    choices=["none", "RQ1", "RQ2", "RQ3"],
    help="Research questions to evaluate, e.g., RQ1 RQ2 RQ3"
)

parser.add_argument("--budget", type=int, default=86400, help="Time budget in seconds")

args = parser.parse_args()
running_dir = os.getcwd()
engine_root = f"{running_dir}/../engines/{args.engine}/build/bin/klee"

test_setting = args.test_setting
engine = args.engine
program = args.program
budget = args.budget
run_rq = args.run_rq

config_file = f"pgm_config/{program}.json"
if os.path.exists(config_file):
    with open(config_file, "r") as f:
        pgm_config = json.load(f)
else:
    print(f"[ERROR] Program configuration file not found: {config_file}")
    sys.exit(1)

pgm_name = pgm_config["pgm_name"]
gcov_path = pgm_config["gcov_path"]
llvm_path = pgm_config["llvm_path"]
src_depth = pgm_config["src_depth"]
sym_cmd = pgm_config["sym_cmd"]

engine_options, symbolic_options, output_dir = get_command(engine_root, pgm_name, engine, running_dir, budget, sym_cmd, test_setting)
run(pgm_name, engine, run_rq, budget, llvm_path, engine_options, symbolic_options, running_dir, output_dir)
# run(pgm_name, budget, llvm_path, gcov_path, engine_options, symbolic_options)
replay(pgm_name, engine, run_rq, output_dir, running_dir, gcov_path, src_depth)
