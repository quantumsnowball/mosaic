import time
from contextlib import ExitStack
from threading import Event, Thread

from mosaic.utils.logging import trace


class Splitter:
    def __init__(self) -> None:
        self.event = Event()

    @trace
    def __enter__(self):
        pass

    @trace
    def __exit__(self, *_):
        pass

    @trace
    def run(self):
        def worker():
            i = 0
            while not self.event.is_set() and i < 10:
                print(f'{self} running ...')
                time.sleep(1)
                i += 1
        self.thread = Thread(target=worker)
        self.thread.start()

    @trace
    def wait(self):
        self.thread.join()

    @trace
    def stop(self):
        self.event.set()


class Combiner:
    def __init__(self, source: Splitter) -> None:
        self.source = source
        self.event = Event()

    @trace
    def __enter__(self):
        pass

    @trace
    def __exit__(self, *_):
        pass

    @trace
    def run(self):
        def worker():
            i = 0
            while not self.event.is_set() and i < 10:
                print(f'{self} running ...')
                time.sleep(1)
                i += 1
        self.thread = Thread(target=worker)
        self.thread.start()

    @trace
    def wait(self):
        self.thread.join()

    @trace
    def stop(self):
        self.event.set()


class Master:
    def __init__(self):
        self.splitter = Splitter()
        self.combiner = Combiner(self.splitter)
        self.master = ExitStack()

    @trace
    def __enter__(self):
        self.master.enter_context(self.splitter)
        self.master.enter_context(self.combiner)
        return self

    @trace
    def __exit__(self, *_):
        self.wait()
        self.master.close()

    @trace
    def run(self):
        self.splitter.run()
        self.combiner.run()

    @trace
    def wait(self):
        self.splitter.wait()
        self.combiner.wait()

    @trace
    def stop(self):
        self.splitter.stop()
        self.combiner.stop()


if __name__ == "__main__":
    with Master() as master:
        master.run()
        try:
            master.wait()
        except KeyboardInterrupt:
            master.stop()
