import os
import random as rd
import subprocess as sp


def sample_env_set(env_data, sample_k):
    sampled_env_set = []

    for _ in range(sample_k):
        selected = []

        for env_var in env_data:
            if rd.random() > 0.5:
                selected.append(env_var)

        sampled = {var: rd.choice(env_data[var]) for var in selected}
        sampled_env_set.append(sampled)

    return sampled_env_set


def replay_with_env(replay_bin, target, testcase, sampled_env_set, timeout=0.1):
    for sampled in sampled_env_set:
        env = os.environ.copy()

        for var, value in sampled.items():
            if value is not None:
                env[var] = str(value)

        cmd = [replay_bin, str(target), str(testcase)]
        process = sp.Popen(cmd, cwd=str(target.parent), stdout=sp.PIPE, stderr=sp.PIPE, env=env)

        try:
            process.communicate(timeout=timeout)
        except sp.TimeoutExpired:
            process.kill()
            process.communicate()