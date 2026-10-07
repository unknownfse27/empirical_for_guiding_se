# Understanding and Improving the Use of Human-Written Test Cases as Seeds for Symbolic Execution

This repository presents the data and results for the paper "Understanding and Improving the Use of Human-Written Test Cases as Seeds for Symbolic Execution"

**Note**: The current unified execution script is provided for the five KLEE-based engines. Support for the other five iterative engines (ParaSuit, TopSeed, FeatMaker, SymTuner, and Learch) will be integrated into the unified script in a future update.


## How to Build
We recommend building quickly and easily using a Docker image. To check the build process, refer to the Dockerfile in this repository.
```bash
$ git clone https://github.com/unknownfse27/empirical_for_guiding_se.git
/empirical_for_guiding_se $ docker build -t empirical-artifact .
/empirical_for_guiding_se $ docker run --rm -it --ulimit stack=-1:-1 empirical-artifact /bin/bash
```

## How to Run
### Quick smoke test : 6 minutes
**Baseline approaches**
```bash
/script $ python3 run.py --test-setting base --engine 10_klee --program bison --budget 360 --run-rq none
```
This command runs the original symbolic execution technique without using human-written test cases as seeds. It serves as the baseline configuration for comparison.

**Human-written test case seeded approaches**
```bash
/script $ python3 run.py --test-setting seed --engine 10_klee --program bison --budget 360 --run-rq none
```
This command runs symbolic execution using the human-written test cases as seeds. It corresponds to the conventional seed-guided symbolic execution setting evaluated in our study.

**Research Question 1: Skipping**
```bash
/script $ python3 run.py --test-setting base --engine 10_klee --program bison --budget 360 --run-rq RQ1
```
or
```bash
/script $ python3 run.py --test-setting seed --engine 10_klee --program bison --budget 360 --run-rq RQ1
```
RQ1 enables our Skipping approach, which reduces unnecessary constraint-solving overhead when concrete argument values can be used to determine feasibility without invoking the SMT solver.

**Research Question 2: ConstSampling**
```bash
/script $ python3 run.py --test-setting base --engine 10_klee --program bison --budget 360 --run-rq RQ2
```
or
```bash
/script $ python3 run.py --test-setting seed --engine 10_klee --program bison --budget 360 --run-rq RQ2
```
RQ2 enables ConstSampling, which samples structured concrete inputs such as arguments, input files, and standard input and applies them to generated test cases to explore additional program regions.

**Research Question 3: EnvConfig**
```bash
/script $ python3 run.py --test-setting base --engine 10_klee --program bison --budget 360 --run-rq RQ3
```
or
```bash
/script $ python3 run.py --test-setting seed --engine 10_klee --program bison --budget 360 --run-rq RQ3
```
RQ3 enables EnvConfig, which samples program-specific environment-variable configurations and replays generated test cases under those configurations to exercise additional branches.

**Research Question 4: Combining Research Questions**
```bash
# RQ1 + RQ2
/script $ python3 run.py --test-setting base --engine 10_klee --program bison --budget 360 --run-rq RQ1 RQ2

# RQ1 + RQ3
/script $ python3 run.py --test-setting base --engine 10_klee --program bison --budget 360 --run-rq RQ1 RQ3

# RQ2 + RQ3
/script $ python3 run.py --test-setting base --engine 10_klee --program bison --budget 360 --run-rq RQ2 RQ3

# RQ1 + RQ2 + RQ3
/script $ python3 run.py --test-setting base --engine 10_klee --program bison --budget 360 --run-rq RQ1 RQ2 RQ3
```
RQ4 evaluates combinations of the proposed approaches to examine whether they provide complementary coverage gains. Multiple approaches can be enabled together by listing the corresponding research questions after --run-rq.

The examples above use KLEE with bison and a 360-second budget for a quick smoke test. To reproduce the full experiments, set the time budget to 86400 seconds (24 hours).

Format : python3 run.py --test-setting <base|seed> --engine <engine> --program <program> --budget <seconds> [--run-rq <none|RQ1|RQ2|RQ3>]

The main options are:
* --test-setting: Selects the symbolic execution setting.
    * base: Run the original symbolic execution technique without human-written test case seeding.
    * seed: Run the technique with human-written test case seeds.
* --engine: Selects the symbolic execution engine or technique.
* --program: Selects the target benchmark program.
* --budget: Specifies the symbolic execution time budget in seconds.
* --run-rq: Optionally enables one or more of the proposed approaches:
    * RQ1: Skipping
    * RQ2: ConstSampling
    * RQ3: EnvConfig

Multiple approaches can be enabled together by listing multiple research questions after --run-rq.

*** If the experiment output directory already exists, the script removes the existing directory and creates a new one before execution.

Then, you will see logs as follows.
```bash
*** Configured ***
Program      : bison
Engine       : 10_klee
Test setting : base
[INFO] Start running symbolic execution. RQ=none, Engine=10_klee, Program=bison
```

When symbolic execution completes without errors or reaches the specified time budget, replay and coverage measurement start automatically:
```bash
[INFO] Finish running symbolic execution. RQ=none, Engine=10_klee, Program=bison
[INFO] Replay start. RQ=none, Engine=10_klee, Program=bison
```

During replay, the script periodically reports the accumulated branch coverage:
```bash
[INFO] 50/232 Coverage: 1150
[INFO] 100/232 Coverage: 1152
[INFO] 150/232 Coverage: 1170
[INFO] 200/232 Coverage: 1186
[INFO] Replay done. RQ=RQ1, Engine=10_klee, Program=bison, Coverage=1186
```

* The exact number of generated test cases and the resulting coverage may vary slightly across smoke-test runs due to the randomized behavior of symbolic execution. The full 24-hour experiments provide substantially more stable results.


## Usage
```
/scripts $ python3 run.py --help
usage: run.py [-h] --test-setting {base,seed}
              --engine {4_KLEE_Q,7_Symsize,8_Aaqc,9_Pending,10_klee}
              --program {bison,diff,find,gawk,gcal,grep,m4,sed,sqlite3}
              [--budget INT]
              [--run-rq {none,RQ1,RQ2,RQ3}]
```

### Required Arguments
| Option | Description |
|:------:|:------------|
| `--test-setting` | Selects the symbolic execution setting: base for the original technique or seed for human-written test case seeding |
| `--engine` | Selects the symbolic execution engine or technique |
| `--program` | Selects the target benchmark program |


### Optional Arguments
| Option | Description |
|:------:|:------------|
| `-h, --help` | show help message and exit |
| `--budget` | Time budget for symbolic execution in seconds. The default value is 86400 seconds (24 hours) |
| `--run-rq` | Enables one or more proposed approaches: RQ1, RQ2, and/or RQ3 |


## Source Code Structure
Here are brief descriptions of the files. Some less-important files may be omitted.
```
.
├── benchmarks                              Scripts for downloading and building the benchmark programs with LLVM and GCOV instrumentation
│   └── build.sh
├── concrete_tcs
│   ├── configs                             Human-written concrete test cases collected from the participants
│   │   └── <program>
│   │       ├── <student_idx>
│   │       │   └── <test_case_idx>.json
│   │       └── inputs
│   ├── seeds                               KLEE seed files generated from the human-written test cases
│   │   └── <program>
│   └── replay.py
├── data
│   ├── rq1                                 Argument data used by the RQ1 Skipping approach
│   ├── rq2                                 Structured input data used by the RQ2 ConstSampling approach
│   └── rq3                                 Environment-variable configurations used by the RQ3 EnvConfig approach
├── engines                                 Source code for the ten symbolic execution techniques evaluated in the study
│   ├── 4_KLEE_Q
│   ├── 7_Symsize
│   ├── 8_Aaqc
│   ├── 9_Pending
│   └── 10_klee
└── scripts
    ├── run.py                              Main entry point for running the experiments
    ├── pgm_config                          Program-specific configurations, including LLVM/GCOV paths and symbolic input settings
    ├── engine_config                       Engine-specific command-line configurations
    ├── test.env
    └── subscripts
        ├── config_cmd.py                   Constructs symbolic execution commands for each engine and benchmark
        ├── run_engine.py                   Executes the selected symbolic execution engine
        ├── replay.py                       Replays generated test cases and measures accumulated branch coverage
        ├── rq1.py                          Implements RQ1-specific argument matching and replay functionality
        ├── rq2.py                          Implements RQ2 structured-input sampling and replay functionality
        └── rq3.py                          Implements RQ3 environment-configuration sampling and replay functionality
```


## Data Availability
The experimental results used in our evaluation are available at the following GitHub release:
[https://github.com/unknownfse27/empirical_for_guiding_se/releases/tag/result](https://github.com/unknownfse27/empirical_for_guiding_se/releases/tag/result)

Download the following file from the release:
+ results.tar.gz

You can download and extract the experimental results from the terminal as follows:

```
/empirical_for_guiding_se $ wget https://github.com/unknownfse27/empirical_for_guiding_se/releases/download/result/results.tar.gz
/empirical_for_guiding_se $ tar -xzf results.tar.gz
```

The archive contains the experimental results for all benchmark programs and evaluated symbolic execution techniques. For each experimental setting, we provide:
+ Generated test cases (.ktest) produced during symbolic execution.
+ Branch coverage information, including the branches covered by the generated test cases.
+ Auxiliary files required to reproduce the analyses for RQ1, RQ2, and RQ3.

We additionally provide replay_result.py, which replays the generated test cases and measures their branch coverage. The script can also apply the approaches evaluated in RQ1–RQ3 to the existing experimental results, allowing the corresponding results to be reproduced without rerunning the full 24-hour symbolic execution experiments.

For example, the following command replays the KLEE results for bison while applying the RQ1 approach:
```
/results $ python3 replay_result.py --test-setting 1_baselines --engines 10_klee --programs bison --run-rq RQ1
```
Multiple research-question approaches can be applied simultaneously by specifying multiple values after --run-rq, such as RQ1 RQ2 RQ3.
