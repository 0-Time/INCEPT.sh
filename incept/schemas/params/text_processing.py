"""Parameter schemas for Text Processing (6 intents)."""

from typing import Literal

from pydantic import BaseModel


class SearchTextParams(BaseModel):
    pattern: str
    path: str | None = None
    recursive: bool = False
    ignore_case: bool = False
    regex_type: Literal["basic", "extended", "perl"] | None = None
    show_line_numbers: bool = False


class ReplaceTextParams(BaseModel):
    pattern: str
    replacement: str
    file: str
    global_replace: bool = True
    in_place: bool = False
    backup: str | None = None


class SortOutputParams(BaseModel):
    input_file: str | None = None
    reverse: bool = False
    numeric: bool = False
    unique: bool = False
    field: int | None = None


class CountLinesParams(BaseModel):
    input_file: str | None = None
    mode: Literal["lines", "words", "chars"] = "lines"


class ExtractColumnsParams(BaseModel):
    field_spec: str
    input_file: str | None = None
    delimiter: str | None = None


class UniqueLinesParams(BaseModel):
    input_file: str | None = None
    count: bool = False
    only_duplicates: bool = False
