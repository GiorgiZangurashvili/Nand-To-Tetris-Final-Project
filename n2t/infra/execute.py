from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Iterator, Protocol

from n2t.core import Executor as DefaultExecutor
from n2t.infra.io import File


@dataclass
class ExecutorProgram:
    path: Path
    executor: Executor = field(default_factory=DefaultExecutor.create)

    @classmethod
    def load_from(cls, file_name: str) -> ExecutorProgram:
        return cls(Path(file_name))

    def __post_init__(self) -> None:
        _, file_extension = os.path.splitext(self.path)
        assert file_extension.lower() in [".hack", ".asm"]

    def execute(self, cycles: int, is_asm: bool, filepath: str) -> None:
        self.executor.execute(self, cycles, is_asm, filepath)

    def __iter__(self) -> Iterator[str]:
        yield from File(self.path).load()


class Executor(Protocol):  # pragma: no cover
    def execute(
        self, file: Iterable[str], cycles: int, is_asm: bool, filepath: str
    ) -> None:
        pass
