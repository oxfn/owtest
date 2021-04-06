#!/bin/sh

echo
echo Running Flake8 linting... 
echo

flake8

echo
echo Running tests with coverage...
echo

coverage run -m pytest
coverage report
