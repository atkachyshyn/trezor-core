from trezor.messages.EosPublicKey import EosPublicKey
from trezor.messages.EosGetPublicKey import EosGetPublicKey
from trezor.crypto.curve import secp256k1
from trezor.crypto.hashlib import ripemd160
from trezor.crypto import base58
from trezor import wire

from apps.common import seed
from apps.eos.layout import require_get_public_key


def _ripemd160_32(data: bytes) -> bytes:
    return ripemd160(data).digest()[:4]

def _public_key_to_wif(pub_key: bytes) -> str:
    if len(pub_key) == 65:
        head = 0x03 if (pub_key[64] & 0x01) == 1 else 0x02
        compresed_pub_key = bytes([head]) + pub_key[1:33]
    elif len(pub_key) == 33:
        compresed_pub_key = pub_key
    else:
        raise wire.DataError("invalid public key length")
    return 'EOS' + base58.encode_check(compresed_pub_key, _ripemd160_32)

def _get_public_key(node):
    seckey = node.private_key()
    public_key = secp256k1.publickey(seckey, True)
    wif = _public_key_to_wif(public_key)
    return wif, public_key

async def get_public_key(ctx, msg: EosGetPublicKey):
    address_n = msg.address_n or ()
    node = await seed.derive_node(ctx, address_n)
    wif, public_key = _get_public_key(node)
    if msg.show_display:
        await require_get_public_key(ctx, wif)
    return EosPublicKey(wif, public_key)
