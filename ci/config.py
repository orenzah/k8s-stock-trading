import yaml
from ci.path import SOURCE_ROOT

class Config:
    def __init__(self):
        with open(f"{SOURCE_ROOT}/config.ignore.yaml", "r") as f:
            self.config = yaml.load(f, Loader=yaml.FullLoader)        


CONFIG = Config().config