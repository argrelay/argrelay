import subprocess
from subprocess import TimeoutExpired, Popen

from argrelay.misc_helper_common import eprint
from argrelay.mongo_data.MongoConfig import MongoConfig


class MongoServerWrapper:

    def __init__(self):
        self.use_mongomock: bool = True
        self.is_started: bool = False
        self.mongo_proc: Popen

    def start_mongo_server(self, mongo_config: MongoConfig):

        eprint(f"use_mongomock: {mongo_config.use_mongomock}")
        if mongo_config.use_mongomock:
            self.use_mongomock = True
            return
        else:
            self.use_mongomock = False

        eprint(f"start_server: {mongo_config.mongo_server.start_server}")
        eprint(f"is_started: {self.is_started}")
        if mongo_config.mongo_server.start_server and not self.is_started:
            eprint(f"server_start_command: {mongo_config.mongo_server.server_start_command}")
            self.mongo_proc = subprocess.Popen(mongo_config.mongo_server.server_start_command, shell = True)
            try:
                self.mongo_proc.wait(timeout = 5)
            except TimeoutExpired:
                # Ignore: it probably started without issues. Or did it?
                pass
            exit_code = self.mongo_proc.poll()
            eprint("mongo_proc: exit_code: ", exit_code)
            if not exit_code:
                # It must be still running:
                self.is_started = True
            elif exit_code != 0:
                # Something went wrong:
                raise RuntimeError

    def stop_mongo_server(self):

        if self.use_mongomock:
            return

        if self.is_started:
            self.mongo_proc.kill()
        while self.is_started:
            try:
                self.mongo_proc.wait(timeout = 5)
            except TimeoutExpired:
                eprint("still running: mongo_proc: ", self.mongo_proc)
            exit_code = self.mongo_proc.poll()
            eprint("mongo_proc: exit_code: ", exit_code)
            if exit_code:
                # Process finished:
                self.is_started = False
