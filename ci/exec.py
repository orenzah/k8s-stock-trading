import os, sys
import time
import argparse
import subprocess

from ci.logger import mylogger

class RunOutput():
    def __init__(self, output: str, error: str):
        self.output = output
        self.error = error
    def __repr__(self):
        return f"Output: {self.output}\nError: {self.error}"


def run(cmd: list[str], cwd: str = ".", env: dict = {}, quiet: bool = False):    
    # cmd = " ".join(cmd)
    # cmd = f"env -C {cwd} {cmd}"                        
    logger = mylogger.getLogger(__name__)
    new_env = os.environ.copy()
    new_env.update(env)
    # cmd = " ".join(cmd)        
    logger.info(f"env -C {env if env else ''}{cwd if cwd != './' else ''} {cmd}")        
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=False, cwd=cwd, env=new_env)
    (output, error) = proc.communicate()    
    if not quiet:
        for line in output.decode("utf-8").split("\n"):
            line = line.strip()
            if line:
                logger.info(line)
    output = RunOutput(output, error)
    return output

    
