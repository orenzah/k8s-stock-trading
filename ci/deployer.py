import argparse
import logging
from ci.ci_class import CI
from ci.exec import run

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
            values = {
                "influxdb.username": "admin",
                "influxdb.password": "password", # chagnge password after deployment
            }        
            cmd = ["helm", "upgrade", "--install", "--namespace", "stock", "stock-trading", "."]
            for v in values.keys():
                cmd.append(f"--set {v}={values[v]}")
            run(cmd, cwd="./stocks-trading")