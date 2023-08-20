import argparse
import logging
from ci.ci_class import CI
from ci.exec import run
from ci.path import 
class Deployer(CI):
    def __init__(self):
        self.name = "deployer"
        self.description = "Deploy to k8s"        
        self.argparser = None
        self.args = None

    def set_args(self, args):
        self.args = args
        
    def add_args(self, argparser: argparse.ArgumentParser):
        argparser.add_argument("--deployer", help="Deploy to k8s", action="store_true")
        self.argparser = argparser
    

    def main(self):
        if self.args.deployer:
            with open(f"{GRAFANA_ROOT}/influx_token.ignore", "r") as f:
                grafana_token = f.read().strip()
            # grafana_token
            values = {
                "influxdb.username": "admin",
                "influxdb.password": "password", # chagnge password after deployment
                "grafana.datasources[0].secureJsonData.token": grafana_token
            }        
            cmd = ["helm", "upgrade", "--install", "--namespace", "stock", "stock-trading", "."]
            for v in values.keys():
                cmd.append(f"--set {v}={values[v]}")
            run(cmd, cwd="./stocks-trading")