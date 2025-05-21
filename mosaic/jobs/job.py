import json
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Self, cast
from uuid import UUID, uuid4


@dataclass
class JobInfo:
    command: str
    id: UUID
    input_file: Path
    output_file: Path

    def save(self, path: Path) -> None:
        info = {k: str(v) for k, v in asdict(self).items()}
        with open(path, 'w') as f:
            json.dump(info, f, indent=4)

    @classmethod
    def load(cls, path: Path) -> Self:
        with open(path, 'r') as f:
            kwargs = cast(dict[str, Any], json.load(f))
        return cls(**kwargs)
