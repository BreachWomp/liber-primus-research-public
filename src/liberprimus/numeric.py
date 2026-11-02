"""Case-sensitive base-60 pairs used by the numeric-table hypothesis."""
ALPHABET = '0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwx'

def decode_pair(token):
    if len(token) != 2 or any(c not in ALPHABET for c in token):
        raise ValueError('Expected two case-sensitive base-60 symbols')
    return 60 * ALPHABET.index(token[0]) + ALPHABET.index(token[1])

def encode_pair(value):
    if not isinstance(value, int) or isinstance(value, bool) or not 0 <= value < 3600:
        raise ValueError('Expected integer in 0..3599')
    high, low = divmod(value, 60)
    return ALPHABET[high] + ALPHABET[low]

def apply_overlay(pages, observations):
    """Return copied grids, requiring each explicitly named old token to match."""
    grids = {p['page_id']: [list(row) for row in p['tokens_by_source']['relikd_canonical']]
             for p in pages}
    seen = set()
    for item in observations:
        page, row, col = item['page_id'], item['row_1based']-1, item['column_1based']-1
        key = (page, row, col)
        if key in seen or row < 0 or col < 0:
            raise ValueError('Duplicate or invalid cell')
        seen.add(key)
        if grids[page][row][col] not in item['historical_alternatives']:
            raise ValueError('Overlay base does not match historical token')
        if item['selected_token'] not in item['historical_alternatives']:
            raise ValueError('Selected token is not a recorded alternative')
        grids[page][row][col] = item['selected_token']
    return grids
