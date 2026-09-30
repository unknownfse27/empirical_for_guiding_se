# REQUIREMENTS

## Hardware Requirements
- Minimum: 8 GB RAM
- Recommended: 16 GB RAM or more
- Storage: At least 20 GB of free disk space for the Docker image, container, and experiment outputs
- Architecture: x86-64 (`linux/amd64`)

## Software Requirements
- Operating System: Linux
- Docker: Required (tested with Docker 24.x)
- Internet connection: Required to download the Docker image
- Python environment: python 3.9+ (if running outside Docker)

## Docker Image
Pull the pre-built Docker image:
```bash
docker pull minjongkim99/parasuit-icse26:v1.1
```

Run the container:
```bash
docker run --rm -it --ulimit stack=-1:-1 minjongkim99/orbis-ase26:v1.1 /bin/bash
```

## Dependencies
- All required dependencies, including ORBiS, Python, LLVM, KLEE, STP, and the benchmark programs, are pre-installed in the Docker image.
- No additional installation is required when using Docker.

## Execution Time
- Smoke test: expected to complete within 10 minutes
- Pulling the pre-built Docker image: 2 minutes
- Symbolic-execution budget for the smoke test: 6 minutes
- Full experiments require substantial computational resources and may take multiple days, depending on hardware and parallelism.

## Known Limitations
- The artifact is primarily tested on x86-64 Linux.
- Experimental results may vary slightly depending on system load and hardware.
