from pathlib import Path

import os
import ast
import json

import subprocess as sp

from .rq1 import load_symbol_data, extract_arg_candidates, filter_symbol_data, get_defined_args, replay_with_matched_args
from .rq2 import extract_elements_in_testcase, replace_values, replay_with_sampled
from .rq3 import sample_env_set, replay_with_env


def find_all(path, ends):
    # Search for files in the current directory and all sub-directories
    found = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith(f'.{ends}'):
                found.append(os.path.join(root, file))
    return found


def clear_gcov(g_path, depth=1):
    # Initialize ".gcda" and ".gcov" files
    for _ in range(depth):
        g_path = g_path[:g_path.rfind('/')]
    gcdas = find_all(g_path, "gcda")
    gcovs = find_all(g_path, "gcov")
    for gcda in gcdas:
        os.system(f"rm -f {gcda}")
    for gcov in gcovs:
        os.system(f"rm -f {gcov}")


def get_testcases(output_dir, engine):
    if engine in ["1_ParaSuit", "2_TopSeed", "5_symtuner", "6_learch"]:
        testcases = list()
        iterations = [f"{output_dir}/{iteration}" for iteration in os.listdir(output_dir) if iteration.startswith("iteration")]
        for iteration in iterations:
            testcases = testcases + [f"{iteration}/{tc}" for tc in os.listdir(iteration) if tc.endswith(".ktest")]
    elif engine in ["3_FeatMaker"]:
        testcases = list()
        iterations = [f"{output_dir}/{iteration}" for iteration in os.listdir(output_dir) if iteration.startswith("iteration")]
        for iteration in iterations:
            indices = [f"{iteration}/{index}" for index in os.listdir(iteration) if not index.endswith("time_result")]
            for index in indices:
                testcases = testcases + [f"{index}/{tc}" for tc in os.listdir(index) if tc.endswith(".ktest")]
    else:
        testcases = [f"{output_dir}/{tc}" for tc in os.listdir(output_dir) if tc.endswith(".ktest")]
    return testcases


def replay_original(replay_bin, target, testcase):
    cmd = [replay_bin, str(target), str(testcase)]
    process = sp.Popen(cmd, stdout=sp.PIPE, stderr=sp.PIPE)
    try:
        process.communicate(timeout=0.1)
    except sp.TimeoutExpired:
        pass
    finally:
        process.kill()


# RQ1
def replay_rq1(engine, target, testcase, replay_bin, ktest_tool_bin, symbol_data):
    const_file = str(testcase).replace(".ktest", ".const")
    if not os.path.exists(const_file):
        return

    try:
        with open(const_file, "r",) as f:
            constraints = ast.literal_eval(f.read().strip())

        limits = extract_arg_candidates(constraints)
        defined_args = get_defined_args(ktest_tool_bin, testcase)

        data = {key: value for key, value in symbol_data.items() if key in defined_args}
        matched_data = filter_symbol_data(data, limits)
        matched_args = {key: [bytes.fromhex(value).rstrip(b"\x00") for value in values] for key, values in matched_data.items()}

        if engine in ["1_ParaSuit", "2_TopSeed", "3_FeatMaker", "5_Symtuner"]:
            sample_k = 4
        else:
            sample_k = 40
        replay_with_matched_args(replay_bin, target, testcase, matched_args, sample_k)

    except Exception as e:
        pass


# RQ2
def replay_rq2(engine, target, testcase, ktest_tool_bin, unsampled_data, input_file_path):
    try:
        testcase_data = extract_elements_in_testcase(ktest_tool_bin, testcase)
        if engine in ["1_ParaSuit", "2_TopSeed", "3_FeatMaker", "5_Symtuner"]:
            sample_k = 4
        else:
            sample_k = 40

        sampled_testcases = replace_values(unsampled_data, testcase_data, input_file_path, sample_k)
        replay_with_sampled(target, sampled_testcases)
    except Exception as e:
        print(f"[ERROR] RQ2 replay failed for {testcase}: {e}")


# RQ3
def replay_rq3(engine, target, testcase, replay_bin, env_data):
    try:
        if engine in ["1_ParaSuit", "2_TopSeed", "3_FeatMaker", "5_Symtuner"]:
            sample_k = 4
        else:
            sample_k = 40

        sampled_env_set = sample_env_set(env_data, sample_k)
        replay_with_env(replay_bin, target, testcase, sampled_env_set)

    except Exception as e:
        print(f"[ERROR] RQ3 replay failed for {testcase}: {e}")


def get_branch_coverage(program, target, src_depth=1):
    target = Path(target).absolute()
    target_dir = target.parent
    original_path = Path.cwd()

    base = Path()
    for _ in range(src_depth):
        base = base / ".."

    gcda_pattern = base / "**/*.gcda"
    gcdas = list(target_dir.glob(str(gcda_pattern)))
    gcdas = [gcda.absolute() for gcda in gcdas]

    covered = set()
    if len(gcdas) == 0:
        return covered

    try:
        os.chdir(str(target_dir))
        cmd = ["gcov", "-b", "-c", *list(map(str, gcdas))]
        result = sp.run(cmd, stdout=sp.PIPE, stderr=sp.PIPE, universal_newlines=True)
        if result.returncode != 0:
            print(f"[GCOV ERROR] {program}")
            print(result.stderr)
            return covered

        # Find generated .gcov files
        base = Path()
        for _ in range(src_depth):
            if program not in ["gawk", "sqlite3"]:
                base = base / ".."

        gcov_pattern = base / "**/*.gcov"
        gcovs = list(Path().glob(str(gcov_pattern)))

        # Extract covered branches
        for gcov in gcovs:
            try:
                with gcov.open(encoding="UTF-8", errors="replace") as f:
                    file_name = (f.readline().strip().split(":")[-1])
                    for i, line in enumerate(f):
                        if ("branch" in line and "never" not in line and "taken 0%" not in line
                            and ":" not in line and "returned 0% blocks executed 0%" not in line):
                            branch_id = f"{file_name} {i}"
                            covered.add(branch_id)
            except Exception:
                pass
    finally:
        os.chdir(str(original_path))
    return covered


def replay(program, engine, run_rq, output_dir, running_dir, gcov_path, src_depth):
    rq_name = ("+".join(run_rq) if run_rq else "Original")
    target = Path(f"{gcov_path}/{program}").absolute()
    testcases = get_testcases(output_dir, engine)

    print(f"[INFO] Replay start. RQ={rq_name}, Engine={engine}, Program={program}")

    # replay_bin = f"{running_dir}/../engines/{engine}/build/bin/klee-replay"
    replay_bin = f"/root/empirical/engines/{engine}/build/bin/klee-replay"
    # ktest_tool_bin = f"{running_dir}/../engines/{engine}/build/bin/ktest-tool"
    ktest_tool_bin = f"/root/empirical/engines/{engine}/build/bin/ktest-tool"

    # RQ1 Data
    symbol_data = None
    if "RQ1" in run_rq:
        seed_args_path = f"{running_dir}/../data/rq1/{program}.txt"
        if not os.path.exists(seed_args_path):
            print(f"[ERROR] RQ1 argument data not found: {seed_args_path}")
            sys.exit(1)
        symbol_data = load_symbol_data(seed_args_path)

    # RQ2 Data
    unsampled_data = None
    input_file_path = None

    if "RQ2" in run_rq:
        unsampled_data_path = f"{running_dir}/../data/rq2/{program}.json"
        input_file_path = f"{running_dir}/../concrete_tcs/configs/{program}/inputs"
        if not os.path.exists(unsampled_data_path):
            print(f"[ERROR] RQ2 data not found: {unsampled_data_path}")
            sys.exit(1)
        if not os.path.exists(input_file_path):
            print(f"[ERROR] RQ2 input directory not found: {input_file_path}")
            sys.exit(1)

        with open(unsampled_data_path, "r", encoding="utf-8") as f:
            unsampled_data = json.load(f)

    # RQ3 Data
    env_data = None
    if "RQ3" in run_rq:
        env_data_path = f"{running_dir}/../data/rq3/{program}.json"
        if not os.path.exists(env_data_path):
            print(f"[ERROR] RQ3 environment data not found: {env_data_path}")
            return set()
        with open(env_data_path, "r", encoding="utf-8") as f:
            env_data = json.load(f)
        

    union_covered = set()
    for idx, testcase in enumerate(testcases):
        clear_gcov(str(target.parent), src_depth)
        replay_original(replay_bin, target, testcase)

        # Replay RQ1
        if "RQ1" in run_rq:
            replay_rq1(engine, target, testcase, replay_bin, ktest_tool_bin, symbol_data)

        # Replay RQ2
        if "RQ2" in run_rq:
            replay_rq2(engine, target, testcase, ktest_tool_bin, unsampled_data, input_file_path)
        
        # Replay RQ3
        if "RQ3" in run_rq:
            replay_rq3(engine, target, testcase, replay_bin, env_data)

        covered = get_branch_coverage(program, target, src_depth)
        union_covered.update(covered)

        if (idx + 1) % 50 == 0:
            print(f"[INFO] {idx + 1}/{len(testcases)} Coverage: {len(union_covered)}")

    print(f"[INFO] Replay done. RQ={rq_name}, Engine={engine}, Program={program}, Coverage={len(union_covered)}")

    return union_covered