"""Gematria Primus, indexed 0..28 in prime order.

Order checked against the original implementation's reference table:
https://github.com/relikd/LiberPrayground#m-gematria-primus
Unicode variants are explicit; unknown symbols are never silently discarded.
Transliteration is many-to-one and is not an English spelling correction.
"""

from collections.abc import Iterable

RUNES = "ᚠᚢᚦᚩᚱᚳᚷᚹᚻᚾᛁᛄᛇᛈᛉᛋᛏᛒᛖᛗᛚᛝᛟᛞᚪᚫᚣᛡᛠ"
MODULUS = len(RUNES)
PRIMES = (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47,
          53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109)
LATIN = ("F", "U", "TH", "O", "R", "C", "G", "W", "H", "N", "I", "J",
         "EO", "P", "X", "S", "T", "B", "E", "M", "L", "NG", "OE", "D",
         "A", "AE", "Y", "IA", "EA")
RUNE_TO_INDEX = {rune: i for i, rune in enumerate(RUNES)}
RUNE_ALIASES = {"ᛂ": "ᛄ", "ᛜ": "ᛝ"}
SEPARATORS = frozenset("-./%&$§•⁘⁚⁖⁜:;,!?\"'()[]{}\\|_—–…")


def validate_indices(values: Iterable[int]) -> list[int]:
    """Materialize and validate, without silently reducing indices modulo 29."""
    result = list(values)
    if any(type(value) is not int or not 0 <= value < MODULUS for value in result):
        raise ValueError("indices must be integers in 0..28 (booleans are invalid)")
    return result


def to_indices(text: str, *, ignore_separators: bool = True) -> list[int]:
    result = []
    for position, symbol in enumerate(text):
        rune = RUNE_ALIASES.get(symbol, symbol)
        if rune in RUNE_TO_INDEX:
            result.append(RUNE_TO_INDEX[rune])
        elif ignore_separators and (symbol.isspace() or symbol in SEPARATORS):
            continue
        else:
            raise ValueError(f"unknown character {symbol!r} at text offset {position}")
    return result


def to_runes(values: Iterable[int]) -> str:
    return "".join(RUNES[i] for i in validate_indices(values))


def transliterate(values: Iterable[int], *, separator: str = "") -> str:
    """Choose U/C/S/NG/IA for the ambiguous U/V, C/K, S/Z, NG/ING, IA/IO."""
    return separator.join(LATIN[i] for i in validate_indices(values))


def render_like(template: str, values: Iterable[int], *, latin: bool = False) -> str:
    """Replace rune slots, preserving punctuation. Length must match exactly."""
    indices = validate_indices(values)
    if len(to_indices(template)) != len(indices):
        raise ValueError("template and replacement must have the same rune count")
    iterator = iter(indices)
    glyphs = LATIN if latin else RUNES
    return "".join(glyphs[next(iterator)] if RUNE_ALIASES.get(c, c) in RUNE_TO_INDEX
                   else c for c in template)


def latin_to_indices(text: str, *, digraphs: bool = True) -> list[int]:
    """Explicit greedy encoding convention, NOT unique recovery of rune spelling.

    With digraphs=True, longest tokens (including ING) win. With False only
    single-letter spellings are accepted. Q has no default mapping and raises.
    For unambiguous experiments prefer literal runes or explicit index arrays.
    """
    tokens = {token: i for i, token in enumerate(LATIN) if digraphs or len(token) == 1}
    tokens.update({"V": 1, "K": 5, "Z": 15})
    if digraphs:
        tokens.update({"ING": 21, "IO": 27})
    text = text.upper()
    result, position = [], 0
    lengths = (3, 2, 1) if digraphs else (1,)
    while position < len(text):
        symbol = text[position]
        if symbol.isspace() or symbol in SEPARATORS:
            position += 1
            continue
        for length in lengths:
            token = text[position:position + length]
            if len(token) == length and token in tokens:
                result.append(tokens[token])
                position += length
                break
        else:
            raise ValueError(f"unencodable Latin character at offset {position}: {symbol!r}")
    return result


def gematria_sum(values: Iterable[int]) -> int:
    return sum(PRIMES[i] for i in validate_indices(values))
