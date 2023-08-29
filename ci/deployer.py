import argparse
import logging
import yaml
from ci.ci_class import CI
from ci.exec import run
from ci.path import GRAFANA_ROOT, CI_ROOT

from ci.config import CONFIG
from ci.logger import logger
class Deployer(CI):
    def __init__(self):
        self.name = "deployer"
        self.description = "Deploy to k8s"        
        self.argparser = None
        self.args = None
        self.context = None
        self.namespace = None
        self.get_context()

    def set_args(self, args):
        self.args = args
        
    def add_args(self, argparser: argparse.ArgumentParser):
        deployer_group = argparser.add_argument_group("Deployer Group")        
        deployer_group.add_argument("--deployer", help="Deploy to k8s", action="store_true")
        deployer_group.add_argument("--template", help="Output templates", action="store_true")
        self.argparser = argparser
    
    def get_context(self):
        with open(f"{CI_ROOT}/env/stocks.yaml", 'r') as f:
            context = yaml.load(f, Loader=yaml.FullLoader)
        self.context = context["context"]
        self.namespace = context["namespace"]

    def helm_cmd(self, cmd, name, chart, values):        
        cmd = ["helm", "--kube-context",self.context] + cmd + ["--namespace", self.namespace, name, chart]        
        for v in values.keys():
            cmd.append(f"--set {v}={values[v]}")
        return cmd

    def main(self):
        if self.args.deployer:
            
            # grafana_token
            values = {
                "influxdb.username": "admin",
                "influxdb.password": "password", # chagnge password after deployment
                "grafana.datasources[0].secureJsonData.token": CONFIG["grafana"]["influxdb"]["token"],                
                "global.common.path": CONFIG["nfs"]["path"],
                "global.common.nfs_server": CONFIG["nfs"]["server"],
                "global.common.mysql.db_name": CONFIG["mysql"]["db_name"],
                
            }        
            cmd = ["upgrade", "--install"]
            cmd = self.helm_cmd(cmd, name="stock-trading", chart=".", values={})
            if self.args.template:
                cmd = ["template", "--debug"]
                cmd = self.helm_cmd(cmd, name="stock-trading", chart=".", values={})
            for v in values.keys():
                cmd.append(f"--set {v}={values[v]}")            
            run(cmd, cwd="./stocks/stocks-trading")