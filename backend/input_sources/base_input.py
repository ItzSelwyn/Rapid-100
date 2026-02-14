from abc import ABC, abstractmethod

class BaseInputSource(ABC):

    @abstractmethod
    async def start_stream(self, callback):
        """
        callback(audio_chunk: bytes)
        """
        pass
