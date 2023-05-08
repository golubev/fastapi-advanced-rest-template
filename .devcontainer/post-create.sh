#!/bin/bash

set -u
set -e

# add a line to `.bashrc` to start the terminal at the API application's source directory
echo 'cd /workspace/api' >> /home/appuser/.bashrc

# set the git hooks directory path to .githooks
git config core.hooksPath .githooks
