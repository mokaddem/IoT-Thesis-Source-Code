#!/bin/bash
cat all_ip.txt | time parallel -P 10 --eta ./make_stats_certificate.py -u username -p password {}
