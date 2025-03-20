#!/bin/bash

# Set the maximum line length
MAX_LINE_LENGTH=120

# Format Python code with black
echo "Running black..."
black ./ --line-length $MAX_LINE_LENGTH

# Lint Python code with flake8
echo "Running flake8..."
flake8 ./ --max-line-length=$MAX_LINE_LENGTH

echo "Formatting and linting complete!"