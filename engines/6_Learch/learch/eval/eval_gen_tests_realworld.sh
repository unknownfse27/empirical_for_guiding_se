#!/bin/bash

PROG=${1}
BC_PATH=${2}
OUTPUT_DIR=${3}
MAX_TIME=${4}
SEARCHER=${5}
KLEE_OPTIONS=${6}
WITH_SEED=${7}
RQ1_ACTIVATE=${8}

items=(${SEARCHER//##/ })
searcher_name=${items[0]}
searcher_path=${items[1]}
if [[ "${searcher_name}" == "feedforward" ]]; then
    searcher_options="--feature-extract --search=ml --model-type=feedforward --model-path=${searcher_path}"
elif [[ "${searcher_name}" == "linear" ]]; then
    searcher_options="--feature-extract --search=ml --model-type=linear --model-path=${searcher_path}"
elif [[ "${searcher_name}" == "rnn" ]]; then
    searcher_options="--feature-extract --search=ml --model-type=rnn --model-path=${searcher_path}"
else
    searcher_options="--search=${searcher_name}"
fi


# if [[ "${WITH_SEED}" == "true" ]]; then
#     seed_options="--allow-seed-extension --allow-seed-truncation --seed-dir=/root/empirical/engines/run/seeds/${PROG}"
# else
#     seed_options=""
# fi

if [[ "${WITH_SEED}" == "true" ]]; then
    seed_dir="/root/empirical/engines/run/seeds/${PROG}"

    mapfile -t seeds < <(
        find "${seed_dir}" -maxdepth 1 -type f -name "*.ktest" \
        | shuf \
        | head -n 10
    )

    seed_options="--allow-seed-extension --allow-seed-truncation --seed-time=5s"

    for seed in "${seeds[@]}"; do
        seed_options+=" --seed-file=${seed}"
    done
else
    seed_options=""
fi


if [[ "${RQ1_ACTIVATE}" == "true" ]]; then
    hseed_options="--seed-args-file=/root/empirical/engines/run/RQ1_seed_args/seed_args/${PROG}.txt --seed-args-log=${OUTPUT_DIR}/seed_args_hit.log --seed-args-max-combinations=10000"
else
    hseed_options=""
fi

/root/empirical/engines/5_learch/klee/build/bin/klee --simplify-sym-indices --write-cvcs --write-cov --output-module --disable-inlining \
--optimize --use-forked-solver --use-cex-cache --libc=uclibc --posix-runtime \
--external-calls=all --watchdog --max-memory-inhibit=false --switch-type=internal \
--only-output-states-covering-new \
--dump-states-on-halt=false \
--output-dir=${OUTPUT_DIR} --env-file=/tmp/test.env --run-in-dir=/root/empirical/engines/5_learch/learch/sandboxes/sandbox_${PROG} \
--max-memory=4096 --max-time=${MAX_TIME}s \
--use-branching-search ${searcher_options} ${seed_options} ${hseed_options} \
${BC_PATH} \
${KLEE_OPTIONS}