from trezor.messages import EosAsset


def eos_name_to_string(value) -> str:
    charmap = ".12345abcdefghijklmnopqrstuvwxyz"
    tmp = value
    string = ''
    actual_size = 13
    for i in range(0, 13):
        c = charmap[tmp & (0x0f if i == 0 else 0x1f)]
        string = c + string
        tmp >>= 4 if i == 0 else 5

    while actual_size != 0 and string[actual_size-1] == '.':
        actual_size -= 1

    return string[:actual_size]

def symbol_to_string(sym: int) -> str:
    sym >>= 8
    string = ''
    for _ in range(0, 7):
        c = chr(sym & 0xff)
        if not c:
            break
        string += c
        sym >>= 8

    return string.rstrip('\x00')

def extract_precision_from_symbol(sym: int) -> (int, int):
    return sym & 0xff

def eos_asset_to_string(asset: EosAsset) -> str:
    integer = fraction = symbol = ''

    p = extract_precision_from_symbol(asset.symbol)
    p10 = 10 ** p
    # integer part
    integer += str(int(asset.amount / p10))

    # fraction part
    remainder = asset.amount % p10
    for _ in range(p, 0, -1):
        fraction = str(int(remainder % 10)) + fraction
        remainder /= 10

    # symbol part
    symbol += symbol_to_string(asset.symbol)

    return "%s.%s %s" % (integer, fraction, symbol)

def pack_variant32(value: int) -> str:
    out = bytearray()
    val = value
    while True:
        b = val & 0x7f
        val >>= 7
        b |= ((val > 0) << 7)
        out.append(b)

        if val == 0:
            break

    return bytes(out)
