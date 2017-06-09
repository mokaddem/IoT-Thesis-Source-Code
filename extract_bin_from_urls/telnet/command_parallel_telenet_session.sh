#!/bin/bash
cat ~/IoT-thesis/all_files.log | time parallel --eta ./telnet_session_extractor.py -d blackhole27 -f ymdhM -s {}
