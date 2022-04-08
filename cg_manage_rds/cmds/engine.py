from abc import ABC, abstractmethod


class Engine(ABC):
    @abstractmethod
    def export_svc(
        self, svc_name: str, creds: dict, backup_file: str, options: str = None
    ) -> None:
        pass

    @abstractmethod
    def import_svc(
        self, svc_name: str, creds: dict, backup_file: str, options: str = None
    ) -> None:
        pass

    @abstractmethod
    def prerequisites(self) -> None:
        pass

    @abstractmethod
    def credentials(self, service_name: str, key_name: str = "key") -> dict:
        pass

    @abstractmethod
    def default_export_options(self, options: str, ignore: bool = False) -> str:
        pass

    @abstractmethod
    def default_import_options(self, options: str, ignore: bool = False) -> str:
        pass