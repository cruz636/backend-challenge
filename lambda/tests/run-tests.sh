#!/bin/bash

# Script to run Lambda tests in a Docker container

set -e

echo "Building test Docker image..."
docker build -t lambda-tests -f Dockerfile ..

echo ""
echo "Running tests..."
docker run --rm lambda-tests

echo ""
echo "Tests completed!"
