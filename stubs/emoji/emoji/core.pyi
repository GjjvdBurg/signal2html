from typing import Any
from typing import Optional

def emojize(
    string: Any,
    use_aliases: bool = ...,
    delimiters: Any = ...,
    variant: Optional[Any] = ...,
    language: str = ...,
): ...
def demojize(
    string: Any,
    use_aliases: bool = ...,
    delimiters: Any = ...,
    language: str = ...,
): ...
def get_emoji_regexp(language: str = ...): ...
def emoji_lis(string: Any, language: str = ...): ...
def distinct_emoji_lis(string: Any): ...
def emoji_count(string: Any): ...
