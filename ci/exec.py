import os, sys
import time
import argparse
import logging

def run(cmd: list[str], cwd: str = ".", env: dict = {}, quiet: bool = False):
    for e in env.keys():
        os.environ[e] = env[e]        

    cmd = " ".join(cmd)
    cmd = f"env -C {cwd} {cmd}"
    logging.info(f"{cmd}")
    os.system(cmd)
