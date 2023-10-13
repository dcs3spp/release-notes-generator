from enum import Enum
from pydantic import BaseModel


class ChangeEnum(str, Enum):
    added = "Add"
    deleted = "Deleted"
    deprecated = "Deprecated"
    fixed = "Fix"
    internal = "Internal"
    none = "None"
    updated = "Update"


class ProductEnum(str, Enum):
    classicPortal = "Tyk Portal (old)"
    portal = "Tyk Portal"
    dashboard = "Tyk Dashboard"
    docs = "Documentation"
    gateway = "Tyk Gateway"
    internal = "Internal"
    none = "None"
    plugin = "Tyk Plugin"
    pump = "Tyk Pump"


class ChangeLog(BaseModel):
    added: list[str] = []
    deleted: list[str] = []
    deprecated: list[str] = []
    fixed: list[str] = []
    updated: list[str] = []


class ProductChangeLog(BaseModel):
    changelog: ChangeLog
    product: ProductEnum


class ReleaseNote(BaseModel):
    changelogs: dict[str, ProductChangeLog]
    semanticVersion: str
    summary: str
    rowParseErrors: dict[int, list[str]]
