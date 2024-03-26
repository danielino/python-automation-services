from abc import abstractmethod


class Plugin(object):
    @abstractmethod
    def run(self):
        pass
