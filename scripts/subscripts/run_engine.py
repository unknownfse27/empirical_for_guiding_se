import os
import re
import ast
import subprocess as sp


def remove_symbolic_terminator(data):
    if data.endswith(b"\xff"):
        return data[:-1]
    return data


def extract_arguments(output):
    arguments = []
    current_object = None

    for line in output.splitlines():
        line = line.strip()

        name_match = re.match(r"object\s+(\d+):\s+name:\s+'(.*)'$", line)
        if name_match:
            current_object = {"index": int(name_match.group(1)), "name": name_match.group(2)}
            continue

        if current_object is None:
            continue

        data_match = re.match(r"object\s+\d+:\s+data:\s+(b[\"'].*[\"'])$", line)
        if data_match:
            arg_match = re.fullmatch(r"arg(\d+)", current_object["name"])
            if arg_match:
                try:
                    data = ast.literal_eval(data_match.group(1))
                    data = remove_symbolic_terminator(data)
                    arguments.append((int(arg_match.group(1)), data))
                except (ValueError, SyntaxError):
                    pass

    arguments.sort(key=lambda x: x[0])
    return [data for _, data in arguments]


def prepare_rq1(pgm_name, engine, running_dir, output_dir):
    seed_dir = f"{running_dir}/../concrete_tcs/seeds/{pgm_name}"
    seed_args_dir = f"{running_dir}/../data/rq1"
    seed_args_path = f"{seed_args_dir}/{pgm_name}.txt"

    ktest_tool_path = f"/root/empirical/engines/{engine}/build/bin/ktest-tool"

    if not os.path.exists(seed_dir):
        raise FileNotFoundError(f"Seed directory not found: {seed_dir}")

    if not os.path.exists(ktest_tool_path):
        raise FileNotFoundError(f"ktest-tool not found: {ktest_tool_path}")

    os.makedirs(seed_args_dir, exist_ok=True)

    seeds = [f"{seed_dir}/{tc}" for tc in os.listdir(seed_dir) if tc.endswith(".ktest")]
    seeds = sorted(seeds)

    arg_data = {}

    for testcase in seeds:
        cmd = [ktest_tool_path, testcase]
        result = sp.run(cmd, stdout=sp.PIPE, stderr=sp.PIPE, universal_newlines=True, check=True)

        arguments = extract_arguments(result.stdout)

        for i, argument in enumerate(arguments):
            arg_name = f"arg{i:02d}"
            arg_data.setdefault(arg_name, []).append(argument)

    with open(seed_args_path, "w") as f:
        for arg_name, values in arg_data.items():
            for value in values:
                f.write(f"{arg_name} {value.hex()}\n")

    rq1_options = [
        f"--seed-args-file={seed_args_path}",
        f"--seed-args-log={output_dir}/seed_args_hit.log",
        "--seed-args-max-combinations=10000",
    ]

    return rq1_options


def run(pgm_name, engine, run_rq, budget, llvm_path, engine_options, symbolic_options, running_dir, output_dir):
    if "RQ1" in run_rq:
        try:
            rq1_options = prepare_rq1(pgm_name, engine, running_dir, output_dir)
            engine_options += rq1_options
        except Exception as e:
            print(f"[ERROR] Failed to prepare RQ1: {e}")
            return None

    llvm_bc = f"{llvm_path}/{pgm_name}.bc"
    cmd = engine_options + [llvm_bc] + symbolic_options
    cmd = " ".join(cmd)

    rq_name = ("+".join(run_rq) if run_rq else "Original")
    print(f"[INFO] Start running symbolic execution. RQ={rq_name}, Engine={engine}, Program={pgm_name}")
    try:
        result = sp.run(cmd, stdout=sp.PIPE, stderr=sp.PIPE, shell=True, check=True, timeout=int(1.25 * budget))
    except sp.TimeoutExpired:
        print("[WARNING] Exceeded the time budget. Iteration terminated.")
    except sp.CalledProcessError as e:
        stderr = e.stderr.decode(errors="replace")
        lines = stderr.strip().splitlines()
        lastline = lines[-1] if lines else ""

        if "kill(9)" in lastline:
            print("[WARNING] Process kill(9)ed. Failed to terminate nicely.")
        else:
            print(f"[WARNING] Fail({e.returncode})ed to execute KLEE.")
    print(f"[INFO] Finish running symbolic execution. RQ={rq_name}, Engine={engine}, Program={pgm_name}")
    return None