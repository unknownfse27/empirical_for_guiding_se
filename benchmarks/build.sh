#! /usr/bin/env bash

BASE_DIRECTORY=$(pwd)
# LOG_LEVEL: DEBUG (0) < INFO (1) < WARN (2) < FAIL (3+)
LOG_LEVEL=${LOG_LEVEL:-"INFO"}
# To disable, set COLORED_PROMPT as OFF, otherwise enabled
COLORED_PROMPT=${COLORED_PROMPT:-"ON"}
GREEN=
WHITE=
YELLOW=
RED=
RESET=
if ! [ $COLORED_PROMPT = "OFF" ]; then
    GREEN="\033[0;32m"
    WHITE="\033[0;37m"
    YELLOW="\033[1;33m"
    RED="\033[0;31m"
    RESET="\033[0m"
fi

NOBJ=$NOBJ

function sudoIf () {
    if [ "$(id -u)" -ne 0 ] ; then
        sudo $@
    else
        $@
    fi
}

function get_log_level_integer () {
    local level_string
    local level
    level_string=$(echo $1 | tr 'a-z', 'A-Z')
    case $level_string in
    "DEBUG") level=0;;
    "INFO") level=1;;
    "WARN") level=2;;
    "FAIL") level=3;;
    esac
    return $level
}

function log () {
    local log_level
    local level_string
    local message_level
    
    get_log_level_integer $LOG_LEVEL
    log_level=$?

    level_string=$(echo $1 | tr 'a-z', 'A-Z')
    get_log_level_integer $level_string
    message_level=$?

    if [ $message_level -ge $log_level ]; then
        case $message_level in
        "0") echo -e $GREEN[DEBUG]$RESET $2;;
        "1") echo -e $WHITE[INFO]$RESET $2;;
        "2") echo -e $YELLOW[WARN]$RESET $2;;
        "3") echo -e $RED[FAIL]$RESET $2;;
        esac
    fi
}

function install_dependencies () {
    sudoIf apt-get update
    sudoIf apt-get install automake
}

function download_source_tgz () {
    if [ -d "$1" ]; then
        log INFO "Already downloaded: $1"
        return 0
    fi
    curl -sk $2 | tar xz
    if ! [ -d "$1" ]; then
        log FAIL "Download failed: $1"
        return 1
    fi
}

function download_source_txz () {
    if [ -d "$1" ]; then
        log INFO "Already downloaded: $1"
        return 0
    fi
    curl -sk $2 | tar xJ
    if ! [ -d "$1" ]; then
        log FAIL "Download failed: $1"
        return 1
    fi
}

function build_gcov_obj () {
    if [ -f "$1/$2" ]; then 
        log INFO "Gcov object already built: $1/$2"
        return 0
    fi
    mkdir -p $1
    cd $1
    ../configure --disable-nls CFLAGS="-g -fprofile-arcs -ftest-coverage" > /dev/null && make > /dev/null
    cd ..
    if ! [ -f "$1/$2" ]; then 
        return 1
    fi
}

function build_multiple_gcov_obj () {
    if [ "$NOBJ" = "" ] ; then
        build_gcov_obj $1 $2
        return $?
    fi

    for i in $(seq 1 $NOBJ) ; do
        build_gcov_obj $1$i $2
    done
}

function build_llvm_obj () {
    local base_dir
    base_dir=$(pwd)
    if [ -f "$1/$2" ]; then 
        log INFO "LLVM object already built: $1/$2"
        return 0
    fi
    mkdir -p $1
    cd $1
    LLVM_COMPILER=clang CC=wllvm ../configure --disable-nls CFLAGS="-g -O1 -Xclang -disable-llvm-passes -D__NO_STRING_INLINES  -D_FORTIFY_SOURCE=0 -U__OPTIMIZE__" > /dev/null && \
    LLVM_COMPILER=clang make > /dev/null
    if [ $? -ne 0 ]; then
        return 1
    fi
    if ! [ -z $3 ]; then 
        cd $3
    fi
    find . -executable -type f | xargs -I '{}' extract-bc '{}'
    cd $base_dir
    if ! [ -f "$1/$2" ]; then
        return 1
    fi
}

function build_multiple_llvm_obj () {
    local retcode
    build_llvm_obj $1 $2 $3
    retcode=$?
    if [ "$NOBJ" = "" ] ; then
        return $retcode
    fi

    for i in $(seq 1 $NOBJ) ; do
        if [ -f "$1$i/$2" ] ; then
            log INFO "LLVM object already exists: $1$i/$2"
        else
            cp -r $1 $1$i
            log INFO "Create LLVM objct: $1$i/$2"
        fi
    done
}

function build_bison-3.8 () {
    cd $BASE_DIRECTORY
    log INFO "Downloading: bison-3.8"
    download_source_txz bison-3.8 https://artfiles.org/gnu.org/bison/bison-3.8.tar.xz
    downloaded=$?
    if [ $downloaded -ne 0 ]; then
        log FAIL "Failed to build bison-3.8"
        return 1
    fi

    cd $BASE_DIRECTORY/bison-3.8
    log INFO "Build gcov object: bison-3.8"
    build_multiple_gcov_obj obj-gcov src/bison
    if [ $? -ne 0 ] ; then
        log FAIL "Failed to build gcov object: bison-3.8"
    fi

    cd $BASE_DIRECTORY/bison-3.8
    log INFO "Build LLVM object: bison-3.8"
    build_multiple_llvm_obj obj-llvm src/bison.bc src
    if [ $? -ne 0 ] ; then
        log FAIL "Failed to build LLVM object: bison-3.8"
    fi
    log INFO "Build process finished: bison-3.8"
}

function build_diff-3.7 () {
    cd $BASE_DIRECTORY
    log INFO "Downloading: diffutils-3.7"
    download_source_txz diffutils-3.7 https://artfiles.org/gnu.org/diffutils/diffutils-3.7.tar.xz
    downloaded=$?
    if [ $downloaded -ne 0 ]; then
        log FAIL "Failed to build diffutils-3.7"
        return 1
    fi

    cd $BASE_DIRECTORY/diffutils-3.7
    log INFO "Build gcov object: diff-3.7"
    build_multiple_gcov_obj obj-gcov src/diff
    if [ $? -ne 0 ] ; then
        log FAIL "Failed to build gcov object: diff-3.7"
    fi

    cd $BASE_DIRECTORY/diffutils-3.7
    log INFO "Build LLVM object: diff-3.7"
    build_multiple_llvm_obj obj-llvm src/diff.bc src
    if [ $? -ne 0 ] ; then
        log FAIL "Failed to build LLVM object: diff-3.7"
    fi
    log INFO "Build process finished: diff-3.7"
}

function build_find-4.7.0 () {
    cd $BASE_DIRECTORY
    log INFO "Downloading: findutils-4.7.0"
    download_source_txz findutils-4.7.0 https://artfiles.org/gnu.org/findutils/findutils-4.7.0.tar.xz
    downloaded=$?
    if [ $downloaded -ne 0 ]; then
        log FAIL "Failed to build findutils-4.7.0"
        return 1
    fi

    cd $BASE_DIRECTORY/findutils-4.7.0
    log INFO "Build gcov object: find-4.7.0"
    build_multiple_gcov_obj obj-gcov find/find
    if [ $? -ne 0 ] ; then
        log FAIL "Failed to build gcov object: find-4.7.0"
    fi

    cd $BASE_DIRECTORY/findutils-4.7.0
    log INFO "Build LLVM object: find-4.7.0"
    build_multiple_llvm_obj obj-llvm find/find.bc find
    if [ $? -ne 0 ] ; then
        log FAIL "Failed to build LLVM object: find-4.7.0"
    fi
    log INFO "Build process finished: find-4.7.0"
}

function build_gawk-5.1.0 () {
    cd $BASE_DIRECTORY
    log INFO "Downloading: gawk-5.1.0"
    download_source_txz gawk-5.1.0 https://artfiles.org/gnu.org/gawk/gawk-5.1.0.tar.xz
    downloaded=$?
    if [ $downloaded -ne 0 ]; then
        log FAIL "Failed to build gawk-5.1.0"
        return 1
    fi

    cd $BASE_DIRECTORY/gawk-5.1.0
    log INFO "Build gcov object: gawk-5.1.0"
    build_multiple_gcov_obj obj-gcov gawk
    if [ $? -ne 0 ] ; then
        log FAIL "Failed to build gcov object: gawk-5.1.0"
    fi

    cd $BASE_DIRECTORY/gawk-5.1.0
    log INFO "Build LLVM object: gawk-5.1.0"
    build_multiple_llvm_obj obj-llvm gawk.bc
    if [ $? -ne 0 ] ; then
        log FAIL "Failed to build LLVM object: gawk-5.1.0"
    fi
    log INFO "Build process finished: gawk-5.1.0"
}

function build_gcal-4.1 () {
    cd $BASE_DIRECTORY
    log INFO "Downloading: gcal-4.1"
    download_source_tgz gcal-4.1 https://artfiles.org/gnu.org/gcal/gcal-4.1.tar.gz
    downloaded=$?
    if [ $downloaded -ne 0 ]; then
        log FAIL "Failed to build gcal-4.1"
        return 1
    fi

    cd $BASE_DIRECTORY/gcal-4.1
    log INFO "Build gcov object: gcal-4.1"
    build_multiple_gcov_obj obj-gcov src/gcal
    if [ $? -ne 0 ] ; then
        log FAIL "Failed to build gcov object: gcal-4.1"
    fi

    cd $BASE_DIRECTORY/gcal-4.1
    log INFO "Build LLVM object: gcal-4.1"
    build_multiple_llvm_obj obj-llvm src/gcal.bc src
    if [ $? -ne 0 ] ; then
        log FAIL "Failed to build LLVM object: gcal-4.1"
    fi
    log INFO "Build process finished: gcal-4.1"
}

function build_grep-3.6 () {
    cd $BASE_DIRECTORY
    log INFO "Downloading: grep-3.6"
    download_source_txz grep-3.6 https://artfiles.org/gnu.org/grep/grep-3.6.tar.xz
    downloaded=$?
    if [ $downloaded -ne 0 ]; then
        log FAIL "Failed to build grep-3.6"
        return 1
    fi

    cd $BASE_DIRECTORY/grep-3.6
    log INFO "Build gcov object: grep-3.6"
    build_multiple_gcov_obj obj-gcov src/grep
    if [ $? -ne 0 ] ; then
        log FAIL "Failed to build gcov object: grep-3.6"
    fi

    cd $BASE_DIRECTORY/grep-3.6
    log INFO "Build LLVM object: grep-3.6"
    build_multiple_llvm_obj obj-llvm src/grep.bc src
    if [ $? -ne 0 ] ; then
        log FAIL "Failed to build LLVM object: grep-3.6"
    fi
    log INFO "Build process finished: grep-3.6"
}

function build_m4-1.4.19 () {
    cd $BASE_DIRECTORY
    log INFO "Downloading: m4-1.4.19"
    download_source_txz m4-1.4.19 https://artfiles.org/gnu.org/m4/m4-1.4.19.tar.xz
    downloaded=$?
    if [ $downloaded -ne 0 ]; then
        log FAIL "Failed to build m4-1.4.19"
        return 1
    fi
    download_source_txz m4-1.4.18 https://artfiles.org/gnu.org/m4/m4-1.4.18.tar.xz
    downloaded=$?
    if [ $downloaded -ne 0 ]; then
        log FAIL "Failed to build m4-1.4.19"
        return 1
    fi

    cd $BASE_DIRECTORY/m4-1.4.19
    log INFO "Build gcov object: m4-1.4.19"
    build_multiple_gcov_obj obj-gcov src/m4
    if [ $? -ne 0 ] ; then
        log FAIL "Failed to build gcov object: m4-1.4.19"
    fi
    cd $BASE_DIRECTORY/m4-1.4.19
    log INFO "Build LLVM object: m4-1.4.19"
    build_multiple_llvm_obj obj-llvm src/m4.bc src
    if [ $? -ne 0 ] ; then
        log FAIL "Failed to build LLVM object: m4-1.4.19"
    fi
    log INFO "Build process finished: m4-1.4.19"

    cd $BASE_DIRECTORY/m4-1.4.18
    log INFO "Build gcov object: m4-1.4.19"
    build_multiple_gcov_obj obj-gcov src/m4
    if [ $? -ne 0 ] ; then
        log FAIL "Failed to build gcov object: m4-1.4.19"
    fi
    cd $BASE_DIRECTORY/m4-1.4.18
    log INFO "Build LLVM object: m4-1.4.19"
    build_multiple_llvm_obj obj-llvm src/m4.bc src
    if [ $? -ne 0 ] ; then
        log FAIL "Failed to build LLVM object: m4-1.4.19"
    fi
    log INFO "Build process finished: m4-1.4.19"
}

function build_sed-4.8 () {
    cd $BASE_DIRECTORY
    log INFO "Downloading: sed-4.8"
    download_source_tgz sed-4.8 https://artfiles.org/gnu.org/sed/sed-4.8.tar.gz
    downloaded=$?
    if [ $downloaded -ne 0 ]; then
        log FAIL "Failed to build sed-4.8"
        return 1
    fi

    cd $BASE_DIRECTORY/sed-4.8
    log INFO "Build gcov object: sed-4.8"
    build_multiple_gcov_obj obj-gcov sed/sed
    if [ $? -ne 0 ] ; then
        log FAIL "Failed to build gcov object: sed-4.8"
    fi

    cd $BASE_DIRECTORY/sed-4.8
    log INFO "Build LLVM object: sed-4.8"
    build_multiple_llvm_obj obj-llvm sed/sed.bc sed
    if [ $? -ne 0 ] ; then
        log FAIL "Failed to build LLVM object: sed-4.8"
    fi
    log INFO "Build process finished: sed-4.8"
}

function build_sqlite-3.33.0 () {
    cd $BASE_DIRECTORY

    log INFO "Downloading: sqlite-3.33.0"

    if ! [ -d "sqlite" ]; then
        mkdir sqlite
    fi

    cd $BASE_DIRECTORY/sqlite

    if ! [ -d "sqlite-amalgamation-3330000" ]; then
        wget https://www.sqlite.org/2020/sqlite-amalgamation-3330000.zip
        unzip sqlite-amalgamation-3330000.zip
    else
        log INFO "Already downloaded: sqlite-amalgamation-3330000"
    fi

    if ! [ -f "obj-llvm/sqlite3.bc" ]; then
        log INFO "Build LLVM object: sqlite-3.33.0"

        rm -rf obj-llvm
        cp -r sqlite-amalgamation-3330000 obj-llvm
        cd obj-llvm

        LLVM_COMPILER=clang wllvm -g -O1 -Xclang -disable-llvm-passes \
            -D__NO_STRING_INLINES -D_FORTIFY_SOURCE=0 -U__OPTIMIZE__ \
            -DSQLITE_THREADSAFE=0 -DSQLITE_OMIT_LOAD_EXTENSION \
            -DSQLITE_DEFAULT_MEMSTATUS=0 -DSQLITE_MAX_EXPR_DEPTH=0 \
            -DSQLITE_OMIT_DECLTYPE -DSQLITE_OMIT_DEPRECATED \
            -DSQLITE_DEFAULT_PAGE_SIZE=512 -DSQLITE_DEFAULT_CACHE_SIZE=10 \
            -DSQLITE_DISABLE_INTRINSIC -DSQLITE_DISABLE_LFS \
            -DYYSTACKDEPTH=20 -DSQLITE_OMIT_LOOKASIDE \
            -DSQLITE_OMIT_WAL -DSQLITE_OMIT_PROGRESS_CALLBACK \
            -DSQLITE_DEFAULT_LOOKASIDE='64,5' \
            -DSQLITE_OMIT_SHARED_CACHE \
            -I. shell.c sqlite3.c -o sqlite3

        extract-bc sqlite3
    else
        log INFO "LLVM object already built: sqlite-3.33.0"
    fi

    cd $BASE_DIRECTORY/sqlite

    if [ "$NOBJ" = "" ]; then
        gcov_indices="1"
    else
        gcov_indices=$(seq 1 $NOBJ)
    fi

    for i in $gcov_indices ; do
        gcov_dir="obj-gcov${i}"

        if [ -f "$gcov_dir/sqlite3" ]; then
            log INFO "Gcov object already built: $gcov_dir/sqlite3"
            continue
        fi

        log INFO "Build gcov object: sqlite-3.33.0 ($gcov_dir)"

        rm -rf $gcov_dir
        cp -r sqlite-amalgamation-3330000 $gcov_dir
        cd $gcov_dir

        gcc -g -fprofile-arcs -ftest-coverage -O0 \
            -DSQLITE_THREADSAFE=0 -DSQLITE_OMIT_LOAD_EXTENSION \
            -DSQLITE_DEFAULT_MEMSTATUS=0 -DSQLITE_MAX_EXPR_DEPTH=0 \
            -DSQLITE_OMIT_DECLTYPE -DSQLITE_OMIT_DEPRECATED \
            -DSQLITE_DEFAULT_PAGE_SIZE=512 -DSQLITE_DEFAULT_CACHE_SIZE=10 \
            -DSQLITE_DISABLE_INTRINSIC -DSQLITE_DISABLE_LFS \
            -DYYSTACKDEPTH=20 -DSQLITE_OMIT_LOOKASIDE \
            -DSQLITE_OMIT_WAL -DSQLITE_OMIT_PROGRESS_CALLBACK \
            -DSQLITE_DEFAULT_LOOKASIDE='64,5' \
            -DSQLITE_OMIT_SHARED_CACHE \
            -I. shell.c sqlite3.c -o sqlite3

        cd $BASE_DIRECTORY/sqlite
    done

    log INFO "Build process finished: sqlite-3.33.0"
}



function help () {
    cat <<-EOF
Usage: $0 [-h|--help] [-l|--list] [--n-objs INT]
        <benchmark> [<benchmark> ...]
Optional arguments:
    -h, --help      Print this list
    -l, --list      List benchmarks
        --n-objs INT
                    Build multiple objects
        
Positional arguments:
    <benchmark>     The name of benchmark, see the supported list
                    with --list option
EOF
}

function list () {
    cat <<-EOF
Benchmark lists
    bison-3.8
    diff-3.7        diffutils-3.7
    find-4.7.0      findutils-4.7.0
    gawk-5.1.0
    gcal-4.1
    grep-3.6
    m4-1.4.19
    sed-4.8
    sqlite-3.33.0
    all             download and build all
EOF
}


function build () {
    case $1 in
    "bison-3.8") build_bison-3.8;;
    "diff-3.7") build_diff-3.7;;
    "find-4.7.0") build_find-4.7.0;;
    "gawk-5.1.0") build_gawk-5.1.0;;
    "gcal-4.1") build_gcal-4.1;;
    "grep-3.6") build_grep-3.6;;
    "m4-1.4.19") build_m4-1.4.19;;
    "sed-4.8") build_sed-4.8;;
    "sqlite-3.33.0") build_sqlite-3.33.0;;
    *) log WARN "Unknown benchmark: $1";;
    esac
}

if [ -z "$1" ] ; then
    help
    exit 1
fi

if [ "$1" = "-h" ] || [ "$1" = "--help" ] ; then
    help
    exit 0
fi

if [ "$1" = "-l" ] || [ "$1" = "--list" ] ; then
    list
    exit 0
fi

if [ "$1" = "--n-objs" ] ; then
    NOBJ=$2
    shift
    shift
fi

if [ "$1" = "all" ] ; then
    benchmarks="bison-3.8 diff-3.7 find-4.7.0 gawk-5.1.0 gcal-4.1 grep-3.6 m4-1.4.19 sed-4.8 sqlite-3.33.0"
else
    benchmarks=$@
fi

for benchmark in $benchmarks; do
    build $benchmark
done
