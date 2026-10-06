import os
import sys
import json


def get_sym_cmd(sym_cmd):
    cmd = list()
    for arg in sym_cmd["args"]:
        cmd.append(f"--sym-arg {arg}")
    
    if len(sym_cmd["files"]) > 0:
        cmd.append(f"--sym-files {sym_cmd['files']}")
    cmd.append(f"--sym-stdin {sym_cmd['stdin']}")
    return cmd


def get_command(engine_root, program, engine, running_dir, budget, sym_cmd, test_setting):
    config_file = f"{running_dir}/engine_config/{engine}.json"
    if os.path.exists(config_file):
        with open(config_file, "r") as f:
            engine_config = json.load(f)
    else:
        print(f"[ERROR] Engine configuration file not found: {config_file}")
        sys.exit(1)

    # Build sandbox
    os.system("tar xvf sandbox.tgz -C . > /dev/null 2>&1")
    sb_path = f"/tmp/sandbox_{engine}_{program}"
    if os.path.exists(sb_path):
        os.system(f"rm -rf {sb_path}")
    os.system(f"mv sandbox {sb_path}")
    
    engine_options = [engine_root] + engine_config["options"] + [f"--run-in-dir={sb_path}", f"--env-file={running_dir}/test.env"]

    # Set output directory
    output_dir = f"{running_dir}/experiments/{engine}_{test_setting}_{program}"
    if os.path.exists(output_dir):
        print(f"[WARNING] Output directory exists. We will delete: {output_dir}")
        os.system(f"rm -rf {output_dir}")
    engine_options = engine_options + [f"--output-dir={output_dir}", f"--max-time={budget}"]

    # Get SEED mode
    if test_setting in ["seed"]:
        seed_dir = f"{running_dir}/../concrete_tcs/seeds/{program}"
        engine_options = engine_options + ["--allow-seed-truncation", "--allow-seed-extension", f"--seed-dir={seed_dir}"]

    # Get symbolic arguments
    symbolic_options = get_sym_cmd(sym_cmd)
    return engine_options, symbolic_options, output_dir
    