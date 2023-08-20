import argparse
import logging
from ci.ci_class import CI
from ci.exec import run
from ci.path import GRAFANA_ROOT

from ci.config import CONFIG

class Deployer(CI):
    def __init__(self):
        self.name = "deployer"
        self.description = "Deploy to k8s"        
        self.argparser = None
        self.args = None

    def set_args(self, args):
        self.args = args
        
    def add_args(self, argparser: argparse.ArgumentParser):
        deployer_group = argparser.add_argument_group("Deployer Group")        
        deployer_group.add_argument("--deployer", help="Deploy to k8s", action="store_true")
        deployer_group.add_argument("--template", help="Output templates", action="store_true")
        self.argparser = argparser
    

    def main(self):
        if self.args.deployer:
            
            # grafana_token
            values = {
                "influxdb.username": "admin",
                "influxdb.password": "password", # chagnge password after deployment
                "grafana.datasources[0].secureJsonData.token": CONFIG["grafana"]["influxdb"]["token"],                
                "global.common.path": CONFIG["nfs"]["path"],
                "global.common.nfs_server": CONFIG["nfs"]["server"],
                
            }        
            cmd = ["helm", "upgrade", "--install", "--namespace", "stock", "stock-trading", "."]
            if self.args.template:
                cmd = ["helm", "template", "--namespace", "stock", "stock-trading", ".", "--debug"]
            for v in values.keys():
                cmd.append(f"--set {v}={values[v]}")
            run(cmd, cwd="./stocks/stocks-trading")