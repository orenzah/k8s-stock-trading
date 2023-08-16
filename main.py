import os, sys
import time
import argparse
import logging
import ci.builder
import ci.deployer

from ci.exec import run

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)    
    argparser = argparse.ArgumentParser()
    
    builder = ci.builder.Builder()
    deployer = ci.deployer.Deployer()

    builder.add_args(argparser)
    deployer.add_args(argparser)


    # ci.builder.add_args(argparser)
    # ci.deployer.add_args(argparser)

    # argparser.add_argument("--base", help="Build base images", action="store_true")
    # argparser.add_argument("--builder", help="Build images", action="store_true")
    # argparser.add_argument("--deployer", help="Deploy to k8s", action="store_true")

    args = argparser.parse_args()
    builder.set_args(args)
    deployer.set_args(args)

    builder.main()
    deployer.main()
    # ci.builder.builder(args)
    # ci.deployer.deployer(args)
    
        


