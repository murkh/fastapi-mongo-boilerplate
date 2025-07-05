from pydantic import BaseModel
from typing import List, Optional, Union


class FileEntry(BaseModel):
    name: str
    is_dir: bool
    size: Optional[int] = None


class DirectoryListResponse(BaseModel):
    entries: List[FileEntry]


class DirectoryTreeNode(BaseModel):
    name: str
    is_dir: bool
    size: Optional[int] = None
    children: Optional[List['DirectoryTreeNode']] = None

class DirectoryTreeResponse(BaseModel):
    tree: List[DirectoryTreeNode]
