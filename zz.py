import asyncio
import os
import signal
import string
import sys
import time
from argparse import ArgumentParser
from itertools import chain, product
from multiprocessing import Process, Queue
from typing import List

import asyncstdlib as asyncstdlib
import pyzipper


def signal_handler(signal_num: int, frame):
    sys.exit(2)


def bruteforce_process_crack(queue, archive_dir: str, first_file_name: str, words: List[str]):
    zip_file: pyzipper.AESZipFile = pyzipper.AESZipFile(archive_dir, "r")
    for word in words:
        try:
            zip_file.setpassword(word.encode('utf8', errors='ignore'))
            zip_file.read(first_file_name)
        except:
            pass
        else:
            queue.put(word)
            zip_file.close()
            return
    zip_file.close()


class ZipCracker:

    def __init__(self, archive_path: str, max_length: int, max_proc: int, max_gather: int, continue_index: int):
        self.archive_path: str = archive_path
        self.max_length: int = max_length
        self.max_proc: int = max_proc
        self.gather_max_words: int = max_gather
        self.continue_index: int = continue_index // max_gather
        self.processes: List[Process] = []
        self.queue: Queue = Queue()

    @staticmethod
    def print_found(word: str):
        hexes = ":".join("{:02X}".format(ord(c)) for c in word)
        print(f"Password was found. The password is: {word} [{hexes}]")

    @staticmethod
    def tries_print(tries: int, word: str):
        hexes = ":".join("{:02X}".format(ord(c)) for c in word)
        print(f"Tries: {tries} > {word} [{hexes}]")

    @staticmethod
    async def generate_bruteforce_list(max_length: int, gather_max: int):
        possible_chars: str = string.printable
        gather_values: List[str] = []
        for val in (''.join(candidate) for candidate in chain.from_iterable(product(possible_chars, repeat=i) for i in range(1, max_length + 1))):
            gather_values.append(val)
            if len(gather_values) >= gather_max:
                yield gather_values
                gather_values = []
        if len(gather_values) != 0:
            yield gather_values

    def wait_for_jobs(self, index: int, last_word: str):
        if len(self.processes) >= self.max_proc:
            for p in self.processes:
                p.join()
            if self.queue.qsize() != 0:
                self.print_found(self.queue.get())
                return
            self.processes.clear()
            self.tries_print(index * self.gather_max_words, last_word)

    async def bruteforce_entry(self):
        zip_object: pyzipper.AESZipFile = pyzipper.AESZipFile(self.archive_path, "r")
        first_file_name: str = zip_object.namelist()[0]
        zip_object.close()
        index: int = 0
        words: List[str] = []
        async for index, words in asyncstdlib.enumerate(self.generate_bruteforce_list(self.max_length, self.gather_max_words), start=1):
            if index < self.continue_index:
                continue
            p: Process = Process(target=bruteforce_process_crack, args=(self.queue, self.archive_path, first_file_name, words))
            p.start()
            self.processes.append(p)
            self.wait_for_jobs(index, words[-1])
        # make sure to process last products even if index is not evenly divisible
        self.wait_for_jobs(index, words[-1])


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("-f", dest="archive", type=str, required=True, help="Archive to crack")
    parser.add_argument("-l", dest="max_length", type=int, required=True, help="The max length for the bruteforce passwords")
    parser.add_argument("-p", dest="max_proc", type=int, default=10, help="The max amount of spawned processes")
    parser.add_argument("-m", dest="max_gather", type=int, default=100, help="Number of password guesses per job")
    parser.add_argument("-c", dest="continue_index", type=int, default=0, help="Last index to continue from")
    args = parser.parse_args()

    if not os.path.exists(args.archive):
        print(f"Zipfile doesn't exist {args.archive}")
        sys.exit(1)

    signal.signal(signal.SIGINT, signal_handler)
    zip_cracker: ZipCracker = ZipCracker(args.archive, args.max_length, args.max_proc, args.max_gather, args.continue_index)

    start: float = time.time()
    asyncio.run(zip_cracker.bruteforce_entry())
    stop: float = time.time()
    print(f"Elapsed {stop - start}")
