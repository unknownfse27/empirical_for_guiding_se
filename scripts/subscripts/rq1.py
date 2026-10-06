import re
import random as rd
import subprocess as sp


def extract_arg_candidates(constraints, min_value=0, max_value=255):
    candidates = {}
    read_pattern = re.compile(r"\(Read\s+w8\s+(\d+)\s+(arg\d+)\)")

    for constraint in constraints:
        for index_str, symbol in read_pattern.findall(constraint):
            index = int(index_str)

            candidates.setdefault(symbol, {})
            candidates[symbol].setdefault(index, set(range(min_value, max_value + 1)))

    # (Eq 45 (Read w8 0 arg00))
    eq_pattern1 = re.compile(
        r"^\(Eq\s+(\d+)\s+"
        r"\(Read\s+w8\s+(\d+)\s+(arg\d+)\)\)$"
    )

    # (Eq (Read w8 0 arg00) 45)
    eq_pattern2 = re.compile(
        r"^\(Eq\s+"
        r"\(Read\s+w8\s+(\d+)\s+(arg\d+)\)\s+(\d+)\)$"
    )

    # (Eq false (Eq 45 (Read w8 0 arg00)))
    neq_pattern1 = re.compile(
        r"^\(Eq\s+false\s+\(Eq\s+(\d+)\s+"
        r"\(Read\s+w8\s+(\d+)\s+(arg\d+)\)\)\)$"
    )

    # (Eq false (Eq (Read w8 0 arg00) 45))
    neq_pattern2 = re.compile(
        r"^\(Eq\s+false\s+\(Eq\s+"
        r"\(Read\s+w8\s+(\d+)\s+(arg\d+)\)\s+(\d+)\)\)$"
    )

    for constraint in constraints:
        constraint = constraint.strip()
        match = eq_pattern1.match(constraint)
        if match:
            value = int(match.group(1))
            index = int(match.group(2))
            symbol = match.group(3)
            if symbol in candidates and index in candidates[symbol]:
                if min_value <= value <= max_value:
                    candidates[symbol][index].intersection_update({value})
                else:
                    candidates[symbol][index].clear()
            continue

        match = eq_pattern2.match(constraint)
        if match:
            index = int(match.group(1))
            symbol = match.group(2)
            value = int(match.group(3))
            if symbol in candidates and index in candidates[symbol]:
                if min_value <= value <= max_value:
                    candidates[symbol][index].intersection_update({value})
                else:
                    candidates[symbol][index].clear()
            continue

        match = neq_pattern1.match(constraint)
        if match:
            value = int(match.group(1))
            index = int(match.group(2))
            symbol = match.group(3)
            if symbol in candidates and index in candidates[symbol]:
                candidates[symbol][index].discard(value)
            continue

        match = neq_pattern2.match(constraint)
        if match:
            index = int(match.group(1))
            symbol = match.group(2)
            value = int(match.group(3))
            if symbol in candidates and index in candidates[symbol]:
                candidates[symbol][index].discard(value)

    result = {}
    for symbol in sorted(candidates, key=lambda x: int(x[3:])):
        result[symbol] = {}
        for index in sorted(candidates[symbol]):
            result[symbol][index] = [f"{value:02x}" for value in sorted(candidates[symbol][index])]
    return result


def load_symbol_data(file_path):
    symbol_data = {}
    with open(file_path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue

            parts = line.split()
            if len(parts) != 2:
                continue

            symbol, hex_data = parts
            symbol_data.setdefault(symbol, []).append(hex_data.lower())
    return symbol_data


def satisfies_constraints(hex_data, constraints):
    if len(hex_data) % 2 != 0:
        return False

    bytes_list = [hex_data[i:i + 2] for i in range(0, len(hex_data), 2)]

    for byte_index, allowed_values in constraints.items():
        byte_index = int(byte_index)
        if byte_index >= len(bytes_list):
            return False

        actual_value = bytes_list[byte_index].lower()
        allowed_values = {value.lower() for value in allowed_values}

        if actual_value not in allowed_values:
            return False
    return True


def filter_symbol_data(symbol_data, constraints):
    result = {}
    for symbol, byte_constraints in constraints.items():
        result[symbol] = []
        if symbol not in symbol_data:
            continue

        for hex_data in symbol_data[symbol]:
            if satisfies_constraints(hex_data, byte_constraints):
                result[symbol].append(hex_data)
    return result


def get_defined_args(ktest_tool_bin, testcase):
    cmd = [ktest_tool_bin, str(testcase)]
    result = sp.run(cmd, stdout=sp.PIPE, stderr=sp.PIPE, universal_newlines=True)

    if result.returncode != 0:
        return []

    arg_symbols = []
    current_symbol = None

    for line in result.stdout.splitlines():
        name_match = re.search(r"name:\s*'(arg\d+)'", line)
        if name_match:
            current_symbol = name_match.group(1)
            continue

        hex_match = re.search(r"hex\s*:\s*0x([0-9a-fA-F]+)", line)
        if hex_match and current_symbol is not None:
            hex_value = hex_match.group(1)

            # Ignore arguments consisting entirely of null bytes.
            is_all_null = all(hex_value[i:i + 2] == "00" for i in range(0, len(hex_value), 2))
            if not is_all_null:
                arg_symbols.append(current_symbol)

            current_symbol = None
    return arg_symbols


def replay_with_matched_args(replay_bin, target, testcase, matched_args, sample_k=4, random_seed=None, timeout=0.1):
    valid_matched_args = {symbol: values for symbol, values in matched_args.items() if len(values) > 0}
    if not valid_matched_args:
        return

    symbols = sorted(valid_matched_args.keys(), key=lambda x: int(x[3:]))

    # Remove duplicate candidate values.
    value_lists = []
    for symbol in symbols:
        values = list(dict.fromkeys(valid_matched_args[symbol]))
        value_lists.append(values)

    total_combinations = 1
    for values in value_lists:
        total_combinations *= len(values)

    if total_combinations == 0:
        return
    sample_size = min(sample_k, total_combinations)
    rng = rd.Random(random_seed)
    selected_indices = set()

    while len(selected_indices) < sample_size:
        selected_indices.add(rng.randrange(total_combinations))

    for combination_index in selected_indices:
        index = combination_index
        combination = [None] * len(value_lists)

        for i in range(len(value_lists) - 1, -1, -1):
            values = value_lists[i]
            value_index = index % len(values)
            index //= len(values)
            combination[i] = values[value_index]

        cmd = [replay_bin.encode()]

        for symbol, value in zip(symbols, combination):
            replace_arg = (b"--replace-symbol=" + symbol.encode("ascii") + b"=" + value)
            cmd.append(replace_arg)

        cmd.extend([str(target).encode(), str(testcase).encode()])
        process = sp.Popen(cmd, cwd=str(target.parent), stdout=sp.PIPE, stderr=sp.PIPE)
        try:
            process.communicate(timeout=timeout)
        except sp.TimeoutExpired:
            process.kill()
            process.communicate()