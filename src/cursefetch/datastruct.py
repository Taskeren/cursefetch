from dataclasses import dataclass
from typing import Generic, TypeVar


T = TypeVar("T")


@dataclass
class Pagination:
    index: int
    pageSize: int
    resultCount: int
    totalCount: int


@dataclass
class PagedResponse(Generic[T]):
    data: list[T]
    pagination: Pagination

    def next_page(self) -> "PagedResponse[T]":
        raise NotImplementedError("This method is not implemented yet.")


@dataclass
class File:
    id: int
    displayName: str
    fileName: str
    releaseType: int
    fileDate: str
    downloadUrl: str
