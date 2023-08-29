import argparse
import sys
import logging
import os
from ci.ci_class import CI
from ci.exec import run

class Test(CI):
    def __init__(self):
        self.name = "test"
        self.description = "test the code"   
        self.argparser = None
        self.args = None

    def set_args(self, args):
        self.args = args
        
    def add_args(self, argparser: argparse.ArgumentParser):
        test_group = argparser.add_argument_group("Run tests")        
        test_group.add_argument("--test-formatting", help="Run Formatting", action="store_true")          
        test_group.add_argument("--test-gdelt", help="Test gdelt code", action="store_true")
        test_group.add_argument("--test-path", help="Test Path", action="store_true")
        
        self.argparser = argparser
    

    def main(self):        
        if self.args.test_gdelt:            
            run(["python3", "./gdelt/download_realtime.py"], cwd="./")
        if self.args.test_path:
            run(["python3", "./ci/path.py"], cwd="./")        
        
            
            
