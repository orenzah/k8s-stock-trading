#!/usr/bin/env python3
import os, sys
import time
import argparse
import logging
from ci.ci_class import CI
from ci.exec import run

class Builder(CI):
    def __init__(self):
        self.name = "builder"
        self.description = "Build docker images"        
        self.argparser = None

    def set_args(self, args):
        self.args = args

    def add_args(self, argparser: argparse.ArgumentParser):        
        argparser.add_argument("--base", help="Build base images", action="store_true")
        argparser.add_argument("--builder", help="Build images", action="store_true")
        argparser.add_argument("--build_stocksight", help="Build stocksight image", action="store_true")
        self.argparser = argparser        

    def docker_builder(self, target: str, image: str, tag: str, cwd: str):
        if os.environ.get("DOCKER_BUILDKIT") is None:
            os.environ["DOCKER_BUILDKIT"] = "1"
        if os.environ.get("REGISTRY") is None:
            os.environ["REGISTRY"] = "cr.zahtlv.freeddns.org"    
        registry = os.environ["REGISTRY"]
        run(["docker", "build", "--target", target, "-t", image, "."], cwd=cwd)
        run(["docker", "tag", image, f"{registry}/{image}:{tag}"])
        run(["docker", "push", f"{registry}/{image}:{tag}"])

    def main(self):    
        if self.args.base:       
            self.docker_builder("base", "python-base", "latest", "./stocks")
        elif self.args.builder:        
            self.docker_builder("app", "python-app", "latest", "./stocks")        
        elif self.args.build_stocksight:        
            self.docker_builder("stocksight", "stocksight", "latest", "./stocksight")
        
    
