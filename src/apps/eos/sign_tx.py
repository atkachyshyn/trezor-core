from trezor import wire
from trezor.crypto.curve import secp256k1
from trezor.crypto.hashlib import sha256
from trezor.messages.EosSignedTx import EosSignedTx
from trezor.messages.EosSignTx import EosSignTx
from trezor.messages.EosTxActionRequest import EosTxActionRequest
from trezor.messages.MessageType import EosTxActionAck
from trezor.utils import HashWriter

from apps.common import paths
from apps.eos import writers
from apps.eos.actions import process_action
from apps.eos.helpers import validate_full_path
from apps.eos.layout import require_sign_tx


async def sign_tx(ctx, msg: EosSignTx, keychain):
    check(msg)

    await paths.validate_path(ctx, validate_full_path, path=msg.address_n)

    node = keychain.derive(msg.address_n)
    sha = HashWriter(sha256())
    await _init(ctx, sha, msg)
    await _actions(ctx, sha, msg.num_actions)
    writers.write_variant32(sha, 0)
    writers.write_bytes(sha, bytearray(32))

    digest = sha.get_digest()
    signature = secp256k1.sign(
        node.private_key(), digest, True, secp256k1.CANONICAL_SIG_EOS
    )

    return EosSignedTx(
        signature[0],
        signature[1:33],
        signature[33:]
    )


async def _init(ctx, sha, msg):
    writers.write_bytes(sha, msg.chain_id)
    writers.write_header(sha, msg.header)
    writers.write_variant32(sha, 0)
    writers.write_variant32(sha, msg.num_actions)

    await require_sign_tx(ctx, msg.num_actions)


async def _actions(ctx, sha, num_actions: int):
    for i in range(num_actions):
        action = await ctx.call(EosTxActionRequest(), EosTxActionAck)
        await process_action(ctx, sha, action)


def check(msg: EosSignTx):
    if msg.chain_id is None:
        raise wire.DataError("No chain id")
    if msg.header is None:
        raise wire.DataError("No header")
    if msg.num_actions == 0:
        raise wire.DataError("No actions")
