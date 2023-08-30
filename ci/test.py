import argparse
import os

from ci.ci_class import CI
from ci.exec import run
from ci.logger import mylogger


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
        test_group.add_argument(
            "--test-formatting",
            help="Run Formatting",
            action="store_true")
        test_group.add_argument(
            "--test-gdelt",
            help="Test gdelt code",
            action="store_true")
        test_group.add_argument(
            "--test-path",
            help="Test Path",
            action="store_true")

        self.argparser = argparser

    def main(self):
        logger = mylogger.getLogger(__name__)
        if self.args.test_gdelt:
            run(["python3", "./gdelt/download_realtime.py"], cwd="./")
        if self.args.test_path:
            run(["python3", "./ci/path.py"], cwd="./")
        if self.args.test_formatting:
            cmd = [
                'git',
                'diff',
                '--name-only',
                '--diff-filter=ACMRTUXB',
                'HEAD',
                'origin/master']

            # cmd = ['ls', '-l']
            output = run(cmd, cwd="./")
            files = output.output.decode("utf-8").split("\n")
            files = [f for f in files if f.endswith(".py")]
            exists_files = []
            for f in files:
                if os.path.exists(f):
                    exists_files.append(f)

            if exists_files:
                run(["black", '--diff'] + exists_files, cwd="./", quiet=True)
                run(['autopep8', '--in-place',
                    '--aggressive', '--ignore=E501',
                     '--max-line-length=120',
                     '--exclude=venv,__pycache__,.pytest,.git'] + exists_files,
                    cwd="./")
                run(["flake8"] + exists_files, cwd="./")
                run(["isort", "--profile", "hug"] + exists_files, cwd="./")
            else:
                logger.info("No files to check")
