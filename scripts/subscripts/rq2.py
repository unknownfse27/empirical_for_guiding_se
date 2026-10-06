import os
import re
import random as rd
import subprocess as sp


def extract_elements_in_testcase(ktest_tool_bin, testcase):
    cmd = [ktest_tool_bin, str(testcase)]
    extracted = {"Input Files": [], "Stdin": []}

    result = sp.run(cmd, stdout=sp.PIPE, stderr=sp.PIPE, universal_newlines=True)
    if result.returncode != 0:
        return extracted

    current_name = None
    for line in result.stdout.splitlines():
        name_match = re.search(r"name:\s*'([^']+)'", line)

        if name_match:
            current_name = name_match.group(1)
            continue

        hex_match = re.search(r"hex\s*:\s*0x([0-9a-fA-F]*)", line)
        if not hex_match or current_name is None:
            continue
        hex_value = hex_match.group(1).lower()

        try:
            raw_value = bytes.fromhex(hex_value)
        except ValueError:
            current_name = None
            continue

        # Arguments
        if re.fullmatch(r"arg\d+", current_name):
            value = raw_value.split(b"\x00", 1)[0]
            value = value.rstrip(b"\xff")
            value = value.decode("latin-1", errors="replace")

            arg_name = (f"Arg{int(current_name[3:])}")
            extracted[arg_name] = value

        # Input files
        elif (current_name.endswith("-data") and not current_name.endswith("-data-stat")):
            value = (raw_value.rstrip(b"\x00").decode("latin-1",errors="replace"))
            extracted["Input Files"].append(value)

        # Stdin
        elif current_name == "stdin":
            value = (raw_value.rstrip(b"\x00").decode("latin-1", errors="replace"))
            extracted["Stdin"].append(value)
        current_name = None
    return extracted


def replace_values(unsampled_data, testcase_data, input_file_path, sample_k):
    candidates = [symbol for symbol in testcase_data if (symbol in unsampled_data and len(unsampled_data[symbol]) > 0)]
    modes = ["arguments"]
    if len(unsampled_data.get("Input Files", [])) > 0:
        modes.append("input_file")

    if len(unsampled_data.get("Stdin", [])) > 0:
        modes.append("stdin")

    sampled_testcases = []
    for _ in range(sample_k):
        mode = rd.choice(modes)
        selected = []
        sampled = {}

        if mode == "arguments":
            argument_candidates = [candidate for candidate in candidates if candidate not in ["Input Files", "Stdin"]]
            for candidate in argument_candidates:
                if rd.random() > 0.5:
                    selected.append(candidate)
        elif mode == "input_file":
            selected = ["Input Files"]
        elif mode == "stdin":
            selected = ["Stdin"]

        for key, value in testcase_data.items():
            if key not in selected:
                sampled[key] = value
                continue

            if key == "Input Files":
                sampled_inputs = []

                for _ in range(len(value)):
                    sampled_file = rd.choice(unsampled_data[key])
                    sampled_inputs.append(os.path.join(input_file_path, sampled_file))
                sampled[key] = sampled_inputs
            else:
                sampled[key] = rd.choice(unsampled_data[key])
        sampled_testcases.append(sampled)
    return sampled_testcases


def replay_with_sampled(target, sampled_testcases, timeout=0.1):
    target = str(target)
    program = os.path.basename(target)

    for sampled in sampled_testcases:
        cmd = [os.fsencode(target)]

        # Arguments
        arg_keys = sorted([key for key in sampled if key.startswith("Arg")], key=lambda x: int(x[3:]))

        for key in arg_keys:
            value = sampled[key]
            if not isinstance(value, str):
                value = str(value)

            value = value.replace("\x00", "")
            if value == "":
                continue

            cmd.append(value.encode("latin-1", errors="replace"))

        # Input files
        for file_idx, input_file in enumerate(sampled.get("Input Files", [])):
            input_file = input_file.replace("\x00", "")
            if input_file == "":
                continue

            if not os.path.exists(input_file):
                output_path = f"/tmp/{program}_{file_idx}"
                with open(output_path, "wb") as output_file:
                    output_file.write(input_file.encode("latin-1", errors="replace"))
                input_file = output_path

            input_file_bytes = os.fsencode(input_file)

            if "gcal" in target:
                cmd.append(b"@" + input_file_bytes)
            else:
                cmd.append(input_file_bytes)

        # Stdin
        stdin_values = sampled.get("Stdin", [])

        if isinstance(stdin_values, str):
            stdin_data = stdin_values
        else:
            stdin_data = stdin_values[0] if stdin_values else ""

        stdin_data = stdin_data.replace("\x00", "")
        stdin_bytes = stdin_data.encode("latin-1", errors="replace")
        process = sp.Popen(cmd, cwd=os.path.dirname(target), stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.PIPE)

        try:
            process.communicate(input=stdin_bytes, timeout=timeout)
        except sp.TimeoutExpired:
            process.kill()
            process.communicate()