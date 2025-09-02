from abc import ABC, abstractmethod

class BaseGame(ABC):
    @abstractmethod
    def stop(self):
        pass

    @abstractmethod
    def format_board(self):
        pass

    @abstractmethod
    def handle_message(self, content):
        pass
