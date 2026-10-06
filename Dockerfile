FROM ubuntu:18.04

ARG BASE_DIR=/root/main
ARG SOURCE_DIR=/root/main/
ARG DEBIAN_FRONTEND=noninteractive

# install requirements
RUN apt-get -y update
RUN apt-get install -y build-essential curl libcap-dev git cmake libncurses5-dev python3-minimal unzip libtcmalloc-minimal4 libgoogle-perftools-dev libsqlite3-dev doxygen gcc-multilib g++-multilib wget

# install python3.9.7
RUN apt-get install -y wget build-essential checkinstall libreadline-gplv2-dev libssl-dev tk-dev libgdbm-dev libc6-dev libbz2-dev libffi-dev zlib1g-dev
WORKDIR /root
RUN wget https://www.python.org/ftp/python/3.9.7/Python-3.9.7.tgz
RUN tar xzf Python-3.9.7.tgz
WORKDIR /root/Python-3.9.7
RUN ./configure --enable-optimizations --enable-shared
RUN make install
ENV LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH


RUN apt-get -y install python3-pip
RUN pip3 install --upgrade pip
RUN pip3 install numpy wllvm scikit-learn
RUN pip3 install matplotlib
RUN apt-get -y install clang-6.0 llvm-6.0 llvm-6.0-dev llvm-6.0-tools
RUN ln -s /usr/bin/clang-6.0 /usr/bin/clang
RUN ln -s /usr/bin/clang++-6.0 /usr/bin/clang++
RUN ln -s /usr/bin/llvm-config-6.0 /usr/bin/llvm-config
RUN ln -s /usr/bin/llvm-link-6.0 /usr/bin/llvm-link

WORKDIR /root

# Install ORBiS
WORKDIR ${BASE_DIR}
RUN git clone https://github.com/minjongkim99/orbis.git
WORKDIR ${BASE_DIR}/orbis
RUN python3 setup.py install

# Install stp solver
RUN apt-get -y install cmake bison flex libboost-all-dev python perl minisat
WORKDIR ${BASE_DIR}
RUN git clone https://github.com/stp/stp.git
WORKDIR ${BASE_DIR}/stp
RUN git checkout tags/2.3.3
RUN mkdir build
WORKDIR ${BASE_DIR}/stp/build
RUN cmake ..
RUN make
RUN make install

RUN echo "ulimit -s unlimited" >> /root/.bashrc


# install Klee-uclibc
WORKDIR ${BASE_DIR}/orbis
RUN git clone https://github.com/klee/klee-uclibc.git
WORKDIR ${BASE_DIR}/orbis/klee-uclibc
RUN chmod 777 -R *
RUN ./configure --make-llvm-lib
RUN make -j2


WORKDIR ${BASE_DIR}/orbis
RUN curl -OL https://github.com/google/googletest/archive/release-1.7.0.zip
RUN unzip release-1.7.0.zip
WORKDIR ${BASE_DIR}/orbis/engine/klee
RUN echo "export LLVM_COMPILER=clang" >> /root/.bashrc
RUN echo "export WLLVM_COMPILER=clang" >> /root/.bashrc
RUN echo "KLEE_REPLAY_TIMEOUT=1" >> /root/.bashrc
RUN mkdir build
WORKDIR ${BASE_DIR}/orbis/engine/klee/build
RUN cmake -DENABLE_SOLVER_STP=ON -DENABLE_POSIX_RUNTIME=ON -DENABLE_KLEE_UCLIBC=ON -DKLEE_UCLIBC_PATH=${BASE_DIR}/orbis/klee-uclibc -DENABLE_UNIT_TESTS=ON -DGTEST_SRC_DIR=${BASE_DIR}/orbis/googletest-release-1.7.0 -DLLVM_CONFIG_BINARY=/usr/bin/llvm-config-6.0 -DLLVMCC=/usr/bin/clang-6.0 -DLLVMCXX=/usr/bin/clang++-6.0 ${BASE_DIR}/orbis/engine/klee
RUN make
WORKDIR ${BASE_DIR}/orbis/engine/klee
RUN env -i /bin/bash -c '(source testing-env.sh; env > test.env)'
RUN echo "export PATH=$PATH:/root/main/orbis/engine/klee/build/bin" >> /root/.bashrc


WORKDIR ${BASE_DIR}/orbis/engine
RUN chmod 777 -R *

# Install Benchmarks (e.g. grep-3.4)
WORKDIR ${BASE_DIR}/orbis/benchmarks
RUN bash building_benchmark.sh grep-3.4

# Initializing Starting Directory
WORKDIR ${BASE_DIR}/orbis/benchmarks
