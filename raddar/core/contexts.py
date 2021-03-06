from contextlib import contextmanager
import tempfile
from typing import Iterator, Optional, Tuple

from fastapi import HTTPException
from git import Repo

from ..lib.exception import FailedToCloneRepoException
from ..lib.managers.repository_manager import clone_repository


@contextmanager
def clone_repo(
    project_dir: str, project_name: str, ref_name: Optional[str] = None
) -> Iterator[Tuple[Repo, str]]:
    with tempfile.TemporaryDirectory(dir=project_dir) as tpf:
        try:
            cloned_repo = clone_repository(tpf, project_name, ref_name)
            yield (cloned_repo, tpf)
        except FailedToCloneRepoException:
            raise HTTPException(status_code=500, detail="Failed to clone repository")
