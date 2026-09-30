from pathlib import Path

import os
import json
import argparse

import subprocess as sp


parser = argparse.ArgumentParser()
original_path = Path.cwd()

def run_config(program, target_dir, testcase, input_root=None):
    testcase = Path(testcase).resolve()
    target_dir = Path(target_dir).resolve()

    with testcase.open("r", encoding="utf-8") as f:
        config = json.load(f)

    envs = config.get("envs", [])
    args = config.get("args", [])
    dirs = config.get("dirs", [])
    files = config.get("files", [])
    stdin = config.get("stdin", "")

    if input_root is not None:
        input_root = Path(input_root).resolve()
        files = [str(input_root / file) for file in files]

    converted_args = []
    file_idx = 0

    for arg in args:
        if arg == "@@":
            if file_idx >= len(files):
                raise ValueError(f"Not enough files to replace @@ in {testcase}")
            converted_args.append(files[file_idx])
            file_idx += 1
        else:
            converted_args.append(arg)

    target = str(target_dir / program)
    command = [target] + converted_args

    env = os.environ.copy()

    for item in envs:
        key, value = item.split("=", 1)
        env[key] = value

    process = sp.Popen(command, cwd=str(target_dir), env=env, stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)
    try:
        stdout, stderr = process.communicate(input=stdin.encode("utf-8") if stdin else None, timeout=3)
    except sp.TimeoutExpired:
        process.kill()
        stdout, stderr = process.communicate()

    return process.returncode, stdout, stderr

def get_coverage_root(target_dir, src_depth):
    coverage_root = Path(target_dir).resolve()
    for _ in range(src_depth):
        coverage_root = coverage_root.parent
    return coverage_root

def initialize_gcov(target_dir, src_depth=1):
    target_dir = Path(target_dir).resolve()
    coverage_root = get_coverage_root(target_dir, src_depth)
    for gcda in coverage_root.rglob("*.gcda"):
        try:
            gcda.unlink()
        except OSError:
            pass

    for gcov in coverage_root.rglob("*.gcov"):
        try:
            gcov.unlink()
        except OSError:
            pass

    for gcov in target_dir.rglob("*.gcov"):
        try:
            gcov.unlink()
        except OSError:
            pass


def get_branch_coverage(program, target_dir, src_depth=1):
    base = Path()
    for _ in range(src_depth):
        base = base / '..'
    gcda_pattern = base / '**/*.gcda'
    gcdas = list(Path(target_dir).glob(str(gcda_pattern)))
    gcdas = [gcda.absolute() for gcda in gcdas]

    covered = set()
    if len(gcdas) > 0:
        os.chdir(str(target_dir))
        cmd = ["gcov", "-b", "-c", *list(map(str, gcdas))]
        result = sp.run(cmd, stdout=sp.PIPE, stderr=sp.PIPE, universal_newlines=True)

        if result.returncode != 0:
            print(f"[ERRORED] GCOV ERROR: {program} / {engine} / {testcase}")
            print(result.stderr)
            os.chdir(str(original_path))
            return covered
            
        base = Path()
        for _ in range(src_depth):
            if program in ["gawk", "make", "sqlite"]:
                pass
            else:
                base = base / ".."

        gcov_pattern = base / "**/*.gcov"
        gcovs = list(Path().glob(str(gcov_pattern)))

        for gcov in gcovs:
            try:
                with gcov.open(encoding="UTF-8", errors="replace") as f:
                    file_name = f.readline().strip().split(":")[-1]
                    for i, line in enumerate(f):
                        if ("branch" in line and "never" not in line and "taken 0%" not in line and ":" not in line and "returned 0% blocks executed 0%" not in line):
                            bid = f"{file_name} {i}"
                            covered.add(bid)
            except:
                pass
    else:
        covered = set()
    os.chdir(str(original_path))
    return covered

parser.add_argument(
    "--programs",
    nargs="+",
    required=True,
    choices=["all", "bison", "diff", "find", "gawk", "gcal", "grep", "m4", "sed", "sqlite"],
    help="Programs to evaluate, e.g., bison grep m4"
)


args = parser.parse_args()

if "all" in args.programs:
    programs = ["bison", "diff", "find", "gawk", "gcal", "grep", "m4", "sed", "sqlite"]
else:
    programs = args.programs



for program in programs:
    print(f"[INFO] Replaying student-written test cases for {program} program")
    # Load program configurations
    with open(f"../scripts/pgm_config/{program}.json", "r") as conf_f:
        configs = json.load(conf_f)
    
    target_dir = configs["gcov_path"]
    src_depth = configs["src_depth"]
    input_file_root = str(Path(f"configs/{program}/inputs").resolve())

    # Load concrete test cases + calculate branch coverage
    union_covered = set()
    testcases = sorted(Path(f"configs/{program}").rglob("*.json"))
    for i, testcase in enumerate(testcases):
        if (i + 1) % 50 == 0:
            print(f"[INFO] Replaying test cases: {i+1}/{len(testcases)} -> Accumulated coverage : {len(union_covered)}")
        initialize_gcov(target_dir, src_depth)
        covered = get_branch_coverage(program, target_dir, src_depth)
        run_config(configs["pgm_name"], target_dir, testcase, input_file_root)
        covered = get_branch_coverage(program, target_dir, src_depth)
        union_covered = union_covered.union(covered)
    print(f"[INFO] Replay done. the accumulated coverage for {program} program : {len(union_covered)}")
    print()
