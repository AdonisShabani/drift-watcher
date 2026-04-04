import os
import yaml
import json

from driftwatch.sources.base import BaseSource
from driftwatch.core.snapshot import Snapshot

class FileSource(BaseSource):
    
    def __init__(self, path):
        self.path = path

    def collect(self) -> Snapshot:
        _, ext = os.path.splitext(self.path)
        if ext in (".yaml", ".yml"):
            with open(self.path) as f:
                data = yaml.safe_load(f)
        elif ext == ".json":
            with open(self.path) as f:
                data = json.load(f)
        else:
            raise ValueError("Extention not supported")
        
        return Snapshot(source=data["source"], data=data["data"])
        
