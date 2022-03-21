# Pypes <a href='https://github.com/schlerp/pypes'><img src='.assets/pypes_logo.svg' align="right" height="270"/></a>

[![Test](https://github.com/schlerp/pypes/actions/workflows/tests.yml/badge.svg)](https://github.com/schlerp/pypes/actions/workflows/tests.yml)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)


Pypes (pronounced "pipes") is a workflow engine/pipeline implementation for unix jobs. 
## Overview

Pypes isn't here to reinvent the wheel. As such, all inputs and outputs are files, while commands are simple bash commands. This allows seamless integration with existing pipelines all while giving a central location to configure, maintain and run the pipelines.

A pipeline represents the top level object of this application. It has a name, an owner, a working directory and a set of steps. Steps represent an atomic job that usually means they make take resources as input, execute a command, then write out resources as output. A resource is essentially a file at this stage. Resources have a path and a status as to if that path exists. 

Dependency resolution is calculated at run time by representing the pipeline as a Directed Acyclic Graph (DAG), specifically using the topographic sort algorithm. While this is nothing new, it is very effective and allows jobs to be defined in any order, taking away some of that stress and enabling multidisciplinary teams to work togther. The only thing that needs to be agreed upon are the resources used by each job.

## Usage

Install like any other python application. I suggest using a virtual env.

```bash

# create virtual environment
python3 -m venv .venv && source .venv/bin/activate

# install dependencies
pip install -r requirements.txt

# only needed for devs: provides linting, formatters and tests
pip install -r requirements-dev.txt

# install and run pypes application
pip install -e src/
python -m pypes
```

## Tests

```bash
# assuming environment is set up and activated
coverage run -m pytest

# for coverage report
coverage report

```

## Author

- [Patrick Coffey](https://github.com/schlerp)