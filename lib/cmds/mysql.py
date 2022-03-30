import click
from lib.cmds.utils import run_sync
from lib.cmds.engine import Engine


class MySql(Engine):
    def prerequisites(self) -> None:
        pass

    def backup(
        self, db_name: str, creds: dict, backup_file: str, options: list = list()
    ) -> None:
        pass

    def restore(
        self, db_name: str, creds: dict, backup_file: str, options: list = list()
    ) -> None:
        pass

    def credentials(self, service_name: str, key_name: str = "key") -> dict:
        pass

    def default_options(self, options: str, ignore: bool = False) -> str:
        pass
