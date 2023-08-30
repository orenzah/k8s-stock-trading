import argparse
import os

from ci.ci_class import CI
from ci.exec import run
from ci.logger import mylogger


class CQ(CI):
    def __init__(self):
        self.name = "Code Quality"
        self.description = "Check and fix code quality"
        self.argparser = None
        self.args = None

    def set_args(self, args):
        self.args = args

    def add_args(self, argparser: argparse.ArgumentParser):
        test_group = argparser.add_argument_group("Formmating")
        test_group.add_argument(
            "--fix-formatting",
            help="Fix Formatting",
            action="store_true")
        self.argparser = argparser

    def main(self):
        logger = mylogger.getLogger(__name__)
        if self.args.fix_formatting:
            cmd = [
                'git',
                'diff',
                '--name-only',
                '--diff-filter=ACMRTUXB',
                'origin/master']

            output = run(cmd, cwd="./")
            files = output.output.split("\n")
            files = [f for f in files if f.endswith(".py")]
            exists_files = []
            for f in files:
                if os.path.exists(f):
                    exists_files.append(f)

            if exists_files:
                run(["black", '--diff'] + exists_files, cwd="./", quiet=True, submodule_name="black")
                run(['autopep8', '--in-place',
                    '--aggressive',
                     '--max-line-length=120',
                     '--exclude=venv,__pycache__,.pytest,.git'] + exists_files,
                    cwd="./",
                    submodule_name="autopep8")
                run(["autoflake", "--in-place"] + exists_files, cwd="./", submodule_name="autoflake")
                run(["isort", "--profile", "hug"] + exists_files, cwd="./", submodule_name="isort")
            else:
                logger.info("No files to check")
