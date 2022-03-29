from abc import ABC, abstractmethod


class Engine(ABC):

    @abstractmethod
    def backup(self, db_name: str, creds: dict, backup_file: str, options: str=None) -> None:
        pass

    @abstractmethod
    def restore(self,db_name: str, creds: dict, backup_file: str, options: str=None) -> None:
        pass
    
    @abstractmethod
    def prerequisites(self)->None:
        pass

    @abstractmethod
    def credentials(self, service_name: str, key_name: str='key') -> dict:
        pass