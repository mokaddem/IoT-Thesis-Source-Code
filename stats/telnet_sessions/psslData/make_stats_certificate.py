#!/usr/bin/env python3
from pypssl import PyPSSL
import argparse
import ast
from pprint import pprint
import redis
import json

serv_ip = redis.StrictRedis(
    host='localhost',
    port=6501,
    db=5)

serv_pssl = redis.StrictRedis(
    host='localhost',
    port=6500,
    db=5)

def ListToDico(l):
    items = l.split(', ')
    dico = {}
    for item in items:
        item = item.split('=')
        key = item[0]
        val = "".join(item[1:])
        dico[key] = val
    return dico


def query_certificates():
    parser = argparse.ArgumentParser()
    parser.add_argument('-u', '--username', required=True, type=str)
    parser.add_argument('-p', '--password', required=True, type=str)
    parser.add_argument('ip')
    args = parser.parse_args()

    ip = args.ip
    psslObj = PyPSSL(basic_auth=(args.username, args.password))

    resp = psslObj.query(ip)
    if len(resp) == 0:
        serv_pssl.set(ip, {})
    else:
        serv_pssl.set(ip, resp[ip])



def make_stats():
    all_ip = serv_pssl.keys('*.*.*')

    dico_country = {}
    dico_organization = {}
    dico_organizationalUnit = {}

    totCert = 0
    totIpCert = 0
    for ip in all_ip:
        certs = serv_pssl.get(ip).decode('utf8')
        certs = ast.literal_eval(certs)
        if len(certs) == 0:
            continue
        totIpCert += 1
        
        for cert_hash, cert_raw in certs['subjects'].items():
            totCert += 1
            cert = cert_raw['values']
            cert = ListToDico(cert[0])
            #country
            try:
                if cert['C'] not in dico_country:
                    dico_country[cert['C']] = 1
                else:
                    dico_country[cert['C']] += 1
            except KeyError:
                pass
    
            #org
            try:
                if cert['O'] not in dico_organization:
                    dico_organization[cert['O']] = 1
                else:
                    dico_organization[cert['O']] += 1
            except KeyError:
                pass
    
            #orgUnit
            try:
                if cert['OU'] not in dico_organizationalUnit:
                    dico_organizationalUnit[cert['OU']] = 1
                else:
                    dico_organizationalUnit[cert['OU']] += 1
            except KeyError:
                pass

    to_write = {
            'country': dico_country,
            'org': dico_organization,
            'orgUnit': dico_organizationalUnit,
            'totCert': totCert,
            'totIp': len(all_ip),
            'totIpCert': totIpCert
            }

    with open('make_stats_certificate.output', 'w') as f:
        json.dump(to_write, f)
        

if __name__ == "__main__":
    #query_certificates()
    make_stats()
