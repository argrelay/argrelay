import subprocess
from subprocess import TimeoutExpired, Popen

from argrelay.misc_helper import eprint
from argrelay.mongo_data.MongoConfig import MongoConfig


class MongoServerWrapper:
    is_mongomock: bool
    is_started: bool
    mongo_proc: Popen

    def __init__(self):
        self.is_started = False

    def start_mongo_server(self, mongo_config: MongoConfig):

        if mongo_config.use_mongomock_only:
            self.is_mongomock = True
            return

        if mongo_config.mongo_server.start_server and not self.is_started:
            self.mongo_proc = subprocess.Popen(mongo_config.mongo_server.server_start_command, shell = True)
            try:
                self.mongo_proc.wait(timeout = 5)
            except TimeoutExpired:
                # Ignore: it probably started without issues. Or did it?
                pass
            ret_code = self.mongo_proc.poll()
            eprint("mongo_proc: ret_code: ", ret_code)
            if not ret_code:
                # It must be still running:
                self.is_started = True
            elif ret_code != 0:
                # Something went wrong:
                raise RuntimeError

    def stop_mongo_server(self):

        if self.is_mongomock:
            return

        if self.is_started:
            self.mongo_proc.kill()
        while self.is_started:
            try:
                self.mongo_proc.wait(timeout = 5)
            except TimeoutExpired:
                eprint("still running: mongo_proc: ", self.mongo_proc)
            ret_code = self.mongo_proc.poll()
            eprint("mongo_proc: ret_code: ", ret_code)
            if ret_code:
                # Process finished:
                self.is_started = False
