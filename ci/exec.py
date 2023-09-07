import os
import subprocess

from ci.logger import mylogger


class RunOutput():
    def __init__(self, output: str, error: str):
        self.output = output
        self.error = error

    def __repr__(self):
        return f"Output: {self.output}\nError: {self.error}"


def run(cmd: list[str], cwd: str = ".", env: dict = {}, quiet: bool = False, submodule_name: str = None):
    if submodule_name:
        logger = mylogger.getLogger(__name__ + "." + submodule_name)
    else:
        logger = mylogger.getLogger(__name__)
    new_env = os.environ.copy()
    new_env.update(env)
    # cmd = ' '.join(cmd)
    cmd = ' '.join(cmd)
    if not quiet:
        logger.info(f"env -C {env if env else ''}{cwd if cwd != './' else ''} {cmd}")    
    # completed_proc = subprocess.run(cmd, capture_output=True, shell=True, cwd=cwd, env=new_env)
    proc = subprocess.Popen(cmd, shell=True,
                            cwd=cwd, env=new_env,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.STDOUT,
                            universal_newlines=True,
                            bufsize=1)
    live_output = ""
    for line in iter(proc.stdout.readline, ''):
        live_output += line
        if line:
            if not quiet:
                logger.info(line.strip('\n'))
    (output, error) = proc.communicate()
    exitcode = proc.wait()  # 0 means success
    # get all output

    # completed_proc = subprocess.CompletedProcess(proc.args, proc.returncode)

    # output = completed_proc.stdout
    # error = completed_proc.stderr
    # if completed_proc.returncode != 0:
    #     logger.error(completed_proc.args)
    #     for line in error.split("\n"):
    #         line = line.strip()
    #         if line:
    #             logger.error(line)
    # if not quiet:
    #     for line in output.split("\n"):
    #         if line:
    #             logger.info(line)
    # output = RunOutput(output, error)
    return RunOutput(live_output, error)
