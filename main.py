import os, sys
import time
import argparse
import logging
import ci.builder
import ci.deployer
import ci.test

from ci.exec import run

if __name__ == "__main__":    
    logging.basicConfig(level=logging.INFO)    
    argparser = argparse.ArgumentParser()
    
    builder = ci.builder.Builder()
    deployer = ci.deployer.Deployer()
    test = ci.test.Test()

    builder.add_args(argparser)
    deployer.add_args(argparser)
    test.add_args(argparser)

    # ci.builder.add_args(argparser)
    # ci.deployer.add_args(argparser)

    # argparser.add_argument("--base", help="Build base images", action="store_true")
    # argparser.add_argument("--builder", help="Build images", action="store_true")
    # argparser.add_argument("--deployer", help="Deploy to k8s", action="store_true")

    args = argparser.parse_args()

    if len(sys.argv) == 1:
        argparser.print_help()
        sys.exit(1)
    builder.set_args(args)
    deployer.set_args(args)
    test.set_args(args)

    builder.main()
    deployer.main()
    test.main()
    # ci.builder.builder(args)
    # ci.deployer.deployer(args)
    
        


