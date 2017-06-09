#!/usr/bin/bash
cat all_files.log | time parallel --eta ./put_in_redis.py -d blackhole27 -f ymd -s {}
