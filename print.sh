#!/bin/bash

cat | awk '{ print "\033[34m --> "$0"\033[0m" }' #| grep -E --color --line-buffered '^.*$|$'