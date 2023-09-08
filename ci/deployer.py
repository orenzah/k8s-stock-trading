import argparse
import logging
import logging.config

import yaml
import json
import time

from ci.ci_class import CI
from ci.config import CONFIG
from ci.exec import run
from ci.logger import LOGGING_CONFIG
from ci.path import CI_ROOT, STOCKS_ROOT, JENKINS_ROOT

import base64
class Deployer(CI):
    def __init__(self):
        self.name = "deployer"
        self.description = "Deploy to k8s"
        self.argparser = None
        self.args = None
        self.context = None
        self.namespace = None
        self.get_context()
        self.logger = logging.getLogger(__name__)
        logging.config.dictConfig(LOGGING_CONFIG)

    def set_args(self, args):
        self.args = args

    def add_args(self, argparser: argparse.ArgumentParser):
        deployer_group = argparser.add_argument_group("Deployer Group")
        deployer_group.add_argument("--deployer", help="Deploy to k8s", action="store_true")
        deployer_group.add_argument("--deploy-jenkins", help="Deploy to k8s", action="store_true")
        deployer_group.add_argument("--template", help="Output templates", action="store_true")        
        deployer_group.add_argument("--ci-mode", help="Set CI Mode", action="store_true")
        self.argparser = argparser

    def get_context(self):
        with open(f"{CI_ROOT}/env/stocks.yaml", 'r') as f:
            context = yaml.load(f, Loader=yaml.FullLoader)        
        self.context = context["context"]
        self.namespace = context["namespace"]

    def helm_cmd(self, cmd: list[str], name: str, chart: str, values: dict, namespace: str):
        if not self.args.ci_mode:
            cmd = ["helm", "--kube-context", self.context] + cmd + ["--namespace", namespace, name, chart]
        else:
            cmd = ["helm"] + cmd + ["--namespace", namespace, name, chart]
        for v in values.keys():
            cmd.append(f"--set {v}={values[v]}")
        return cmd
    
    def update_config(self, values: dict):
        config64 = base64.b64encode(json.dumps(values).encode('ascii'))        
        old = run(['kubectl', 'get', 'secret', 'ci-config', '--namespace', 'jenkins',              
             '-o', 'json'])                
        with open(f'/tmp/ci-config.{time.strftime("%Y%m%d-%H%M%S")}.yaml', 'w') as f:
            f.write(old.output)
        old = run(['kubectl', 'delete', 'secret', '--namespace', 'jenkins', 'ci-config'])
        run(['kubectl', 'create', 'secret', 'generic', '--namespace', 'jenkins', 'ci-config', 
             f'--from-literal=config="{config64}"'])            
        
    def main(self):
        if self.args.deploy_jenkins:
            cmd = ["upgrade", "--install", "-f", f"{JENKINS_ROOT}/jenkins/values.yaml", "-f", f"{JENKINS_ROOT}/values.yaml"]
            cmd = self.helm_cmd(cmd, name="jenkins", chart=".", values={}, namespace="jenkins")
            if self.args.template:
                cmd = ["template", "--debug"]
                cmd = self.helm_cmd(cmd, name="jenkins", chart=".", values={}, namespace="jenkins")                        
            run(cmd, cwd=f"{JENKINS_ROOT}/jenkins") 
        if self.args.deployer:
            # grafana_token
            if self.args.ci_mode:
                output = run(['kubectl', 'get', 'secret', '--namespace', 'jenkins', 'ci-config', '-o', 'json'], '/', quiet=self.args.ci_mode)
                config = json.loads(output.output)['data']                
                config = base64.b64decode(config['config'])                
                config = config[2:-1:1].decode()                
                values = json.loads(base64.b64decode(config))                   
            else:
                values = {
                    "influxdb.username": "admin",
                    "influxdb.password": "password",  # chagnge password after deployment
                    "grafana.datasources[0].secureJsonData.token": CONFIG["grafana"]["influxdb"]["token"],
                    "global.common.path": CONFIG["nfs"]["path"],
                    "global.common.nfs_server": CONFIG["nfs"]["server"],
                    "global.common.mysql.db_name": CONFIG["mysql"]["db_name"],                             
                    "stock-engine.binance.api_key": CONFIG["binance"]["api_key"],
                    "stock-engine.binance.api_secret": CONFIG["binance"]["api_secret"]
                }
                self.update_config(values)                
            cmd = ["upgrade", "--install"]
            cmd = self.helm_cmd(cmd, name="stock-trading", chart=".", values={}, namespace="stock")
            if self.args.template:
                cmd = ["template", "--debug"]
                cmd = self.helm_cmd(cmd, name="stock-trading", chart=".", values={}, namespace="stock")
            for v in values.keys():
                cmd.append(f"--set {v}={values[v]}")            
            run(cmd, cwd=f"{STOCKS_ROOT}/stocks-trading", quiet=self.args.ci_mode)
