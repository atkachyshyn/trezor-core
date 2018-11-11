from ubinascii import hexlify

from trezor.messages import ButtonRequestType
from trezor.messages import EosActionBuyRam
from trezor.messages import EosActionBuyRamBytes
from trezor.messages import EosActionSellRam
from trezor.messages import EosActionDelegate
from trezor.messages import EosActionUndelegate
from trezor.messages import EosActionRefund
from trezor.messages import EosActionUpdateAuth
from trezor.messages import EosActionDeleteAuth
from trezor.messages import EosActionVoteProducer
from trezor.messages import EosActionTransfer
from trezor.messages import EosActionLinkAuth
from trezor.messages import EosActionUnlinkAuth
from trezor.messages import EosActionNewAccount


from trezor import ui
from trezor.ui.text import Text
from trezor.utils import chunks
from trezor.messages.ButtonRequest import ButtonRequest
from trezor.messages import MessageType
from trezor.ui.confirm import ConfirmDialog
from trezor.ui.scroll import Scrollpage, animate_swipe, paginate

from apps.eos import helpers
from apps.eos.get_public_key import _public_key_to_wif
from apps.eos.layout import require_confirm


LINE_LENGTH = 17
LINE_PLACEHOLDER = "{:<" + str(LINE_LENGTH)+"}"
FIRST_PAGE = 0
TWO_FIELDS_PER_PAGE = 2
THREE_FIELDS_PER_PAGE = 3
FOUR_FIELDS_PER_PAGE = 4
FIVE_FIELDS_PER_PAGE = 5


def confirm_action_buyram(ctx, msg: EosActionBuyRam):
    await ctx.call(ButtonRequest(code=ButtonRequestType.ConfirmOutput), MessageType.ButtonAck)

    text = "Buy RAM"
    fields = []
    fields.append("Payer:")
    fields.append(helpers.eos_name_to_string(msg.payer))
    fields.append("Receiver:")
    fields.append(helpers.eos_name_to_string(msg.receiver))
    fields.append("Amount:")
    fields.append(helpers.eos_asset_to_string(msg.quantity))

    pages = list(chunks(fields, FOUR_FIELDS_PER_PAGE))

    paginator = paginate(show_lines_page, len(pages), FIRST_PAGE, pages, text)
    await ctx.wait(paginator)

def confirm_action_buyrambytes(ctx, msg: EosActionBuyRamBytes):
    await ctx.call(ButtonRequest(code=ButtonRequestType.ConfirmOutput), MessageType.ButtonAck)

    text = "Buy RAM"
    fields = []
    fields.append("Payer:")
    fields.append(helpers.eos_name_to_string(msg.payer))
    fields.append("Receiver:")
    fields.append(helpers.eos_name_to_string(msg.receiver))
    fields.append("Bytes:")
    fields.append(str(msg.bytes))

    pages = list(chunks(fields, FOUR_FIELDS_PER_PAGE))
    paginator = paginate(show_lines_page, len(pages), FIRST_PAGE, pages, text)

    await ctx.wait(paginator)

def confirm_action_delegate(ctx, msg: EosActionDelegate):
    await ctx.call(ButtonRequest(code=ButtonRequestType.ConfirmOutput), MessageType.ButtonAck)

    text = "Delegate"
    fields = []
    fields.append("Sender:")
    fields.append(helpers.eos_name_to_string(msg.sender))
    fields.append("Receiver:")
    fields.append(helpers.eos_name_to_string(msg.receiver))
    fields.append("CPU:")
    fields.append(helpers.eos_asset_to_string(msg.stake_cpu_quantity))
    fields.append("NET:")
    fields.append(helpers.eos_asset_to_string(msg.stake_net_quantity))

    if msg.transfer:
        fields.append("Transfer to:")
        fields.append(helpers.eos_name_to_string(msg.receiver))

    pages = list(chunks(fields, FOUR_FIELDS_PER_PAGE))
    paginator = paginate(show_lines_page, len(pages), FIRST_PAGE, pages, text)

    await ctx.wait(paginator)

def confirm_action_sellram(ctx, msg: EosActionSellRam):
    await ctx.call(ButtonRequest(code=ButtonRequestType.ConfirmOutput), MessageType.ButtonAck)

    text = "Sell RAM"
    fields = []
    fields.append("Receiver:")
    fields.append(helpers.eos_name_to_string(msg.account))
    fields.append("Bytes:")
    fields.append(str(msg.bytes))

    pages = list(chunks(fields, TWO_FIELDS_PER_PAGE))
    paginator = paginate(show_lines_page, len(pages), FIRST_PAGE, pages, text)

    await ctx.wait(paginator)

def confirm_action_undelegate(ctx, msg: EosActionUndelegate):
    await ctx.call(ButtonRequest(code=ButtonRequestType.ConfirmOutput), MessageType.ButtonAck)

    text = "Undelegate"
    fields = []
    fields.append("Sender:")
    fields.append(helpers.eos_name_to_string(msg.sender))
    fields.append("Receiver:")
    fields.append(helpers.eos_name_to_string(msg.receiver))
    fields.append("CPU:")
    fields.append(helpers.eos_asset_to_string(msg.unstake_cpu_quantity))
    fields.append("NET:")
    fields.append(helpers.eos_asset_to_string(msg.unstake_net_quantity))

    pages = list(chunks(fields, FOUR_FIELDS_PER_PAGE))
    paginator = paginate(show_lines_page, len(pages), FIRST_PAGE, pages, text)

    await ctx.wait(paginator)

def confirm_action_refund(ctx, msg: EosActionRefund):
    text = Text("Refund", ui.ICON_CONFIRM, icon_color=ui.GREEN)
    text.normal("Owner:")
    text.normal(helpers.eos_name_to_string(msg.owner))
    await require_confirm(ctx, text, ButtonRequestType.ConfirmOutput)

def confirm_action_voteproducer(ctx, msg: EosActionVoteProducer):
    if msg.proxy != 0 and not msg.producers:
        # PROXY
        text = Text("Vote for proxy", ui.ICON_CONFIRM, icon_color=ui.GREEN)
        text.normal("Voter:")
        text.normal(helpers.eos_name_to_string(msg.voter))
        text.normal("Proxy:")
        text.normal(helpers.eos_name_to_string(msg.proxy))
        await require_confirm(ctx, text, ButtonRequestType.ConfirmOutput)

    elif msg.producers:
        # PRODUCERS
        await ctx.call(ButtonRequest(code=ButtonRequestType.ConfirmOutput), MessageType.ButtonAck)
        producers = list(enumerate(msg.producers))
        pages = list(chunks(producers, FIVE_FIELDS_PER_PAGE))
        paginator = paginate(show_voter_page, len(pages), FIRST_PAGE, pages)
        await ctx.wait(paginator)

    else:
        # Cancel vote
        text = Text("Cancel vote", ui.ICON_CONFIRM, icon_color=ui.GREEN)
        text.normal("Voter:")
        text.normal(helpers.eos_name_to_string(msg.voter))
        await require_confirm(ctx, text, ButtonRequestType.ConfirmOutput)

def confirm_action_transfer(ctx, msg: EosActionTransfer):
    await ctx.call(ButtonRequest(code=ButtonRequestType.ConfirmOutput), MessageType.ButtonAck)

    text = "Transfer"
    fields = []
    fields.append("From:")
    fields.append(helpers.eos_name_to_string(msg.sender))
    fields.append("To:")
    fields.append(helpers.eos_name_to_string(msg.receiver))
    fields.append("Amount:")
    fields.append(helpers.eos_asset_to_string(msg.quantity))

    if msg.memo is not None:
        fields.append("Memo:")
        fields.append(msg.memo[:512])

    pages = list(chunks(fields, FOUR_FIELDS_PER_PAGE))

    paginator = paginate(show_lines_page, len(pages), FIRST_PAGE, pages, text)
    await ctx.wait(paginator)

def confirm_action_updateauth(ctx, msg: EosActionUpdateAuth):
    await ctx.call(ButtonRequest(code=ButtonRequestType.ConfirmOutput), MessageType.ButtonAck)

    text = "Update Auth"
    fields = []
    fields.append("Account:")
    fields.append(helpers.eos_name_to_string(msg.account))
    fields.append("Permission:")
    fields.append(helpers.eos_name_to_string(msg.permission))
    fields.append("Parent:")
    fields.append(helpers.eos_name_to_string(msg.parent))
    fields += authorization_fields(msg.auth)

    pages = list(chunks(fields, TWO_FIELDS_PER_PAGE))

    paginator = paginate(show_lines_page, len(pages), FIRST_PAGE, pages, text)
    await ctx.wait(paginator)

def confirm_action_deleteauth(ctx, msg: EosActionDeleteAuth):
    text = Text("Delete auth", ui.ICON_CONFIRM, icon_color=ui.GREEN)
    text.normal("Account:")
    text.normal(helpers.eos_name_to_string(msg.account))
    text.normal("Permission:")
    text.normal(helpers.eos_name_to_string(msg.permission))
    await require_confirm(ctx, text, ButtonRequestType.ConfirmOutput)

def confirm_action_linkauth(ctx, msg: EosActionLinkAuth):
    await ctx.call(ButtonRequest(code=ButtonRequestType.ConfirmOutput), MessageType.ButtonAck)

    text = "Link Auth"
    fields = []
    fields.append("Account:")
    fields.append(helpers.eos_name_to_string(msg.account))
    fields.append("Code:")
    fields.append(helpers.eos_name_to_string(msg.code))
    fields.append("Type:")
    fields.append(helpers.eos_name_to_string(msg.type))
    fields.append("Requirement:")
    fields.append(helpers.eos_name_to_string(msg.requirement))

    pages = list(chunks(fields, FOUR_FIELDS_PER_PAGE))
    paginator = paginate(show_lines_page, len(pages), FIRST_PAGE, pages, text)

    await ctx.wait(paginator)

def confirm_action_unlinkauth(ctx, msg: EosActionUnlinkAuth):
    await ctx.call(ButtonRequest(code=ButtonRequestType.ConfirmOutput), MessageType.ButtonAck)

    text = "Unlink Auth"
    fields = []
    fields.append("Account:")
    fields.append(helpers.eos_name_to_string(msg.account))
    fields.append("Code:")
    fields.append(helpers.eos_name_to_string(msg.code))
    fields.append("Type:")
    fields.append(helpers.eos_name_to_string(msg.type))

    pages = list(chunks(fields, FOUR_FIELDS_PER_PAGE))
    paginator = paginate(show_lines_page, len(pages), FIRST_PAGE, pages, text)

    await ctx.wait(paginator)

def confirm_action_newaccount(ctx, msg: EosActionNewAccount):
    await ctx.call(ButtonRequest(code=ButtonRequestType.ConfirmOutput), MessageType.ButtonAck)

    text = "New Account"
    fields = []
    fields.append("Creator:")
    fields.append(helpers.eos_name_to_string(msg.creator))
    fields.append("Name:")
    fields.append(helpers.eos_name_to_string(msg.name))
    fields += authorization_fields(msg.owner)
    fields += authorization_fields(msg.active)

    pages = list(chunks(fields, TWO_FIELDS_PER_PAGE))
    paginator = paginate(show_lines_page, len(pages), FIRST_PAGE, pages, text)

    await ctx.wait(paginator)

def confirm_action_unknown(ctx, action, checksum):
    await ctx.call(ButtonRequest(code=ButtonRequestType.ConfirmOutput), MessageType.ButtonAck)
    text = "Unknown Action"
    fields = []
    fields.append("Do it at your own risk")
    fields.append("Contract:")
    fields.append(helpers.eos_name_to_string(action.account))
    fields.append("Action Name:")
    fields.append(helpers.eos_name_to_string(action.name))

    fields.append("Checksum:")
    fields.append(hexlify(checksum).decode('ascii'))

    pages = list(chunks(fields, THREE_FIELDS_PER_PAGE))
    paginator = paginate(show_lines_page, len(pages), FIRST_PAGE, pages, text)

    await ctx.wait(paginator)

@ui.layout
async def show_lines_page(page: int, page_count: int, pages: list, header: str):
    lines = ["%s" % field for field in pages[page]]
    text = Text("{}".format(header), ui.ICON_CONFIRM, icon_color=ui.GREEN)
    text.mono(*lines)

    content = Scrollpage(text, page, page_count)
    if page + 1 == page_count:
        await ConfirmDialog(content)
    else:
        content.render()
        await animate_swipe()

@ui.layout
async def show_voter_page(page: int, page_count: int, pages: list):
    lines = ["%2d. %s" % (wi + 1, helpers.eos_name_to_string(producer)) for wi, producer in pages[page]]
    text = Text("Vote for producers", ui.ICON_CONFIRM, icon_color=ui.GREEN)
    text.mono(*lines)
    content = Scrollpage(text, page, page_count)

    if page + 1 == page_count:
        await ConfirmDialog(content)
    else:
        content.render()
        await animate_swipe()

def authorization_fields(auth):
    fields = []

    fields.append("Threshold:")
    fields.append(auth.threshold)

    for i, key in enumerate(auth.keys):
        _key = _public_key_to_wif(bytes(key.key))
        _weight = key.weight

        header = "Key #{}:".format(i + 1)
        w_header = "Key #{} Weight:".format(i + 1)
        fields.append(header)
        fields.append(_key)
        fields.append(w_header)
        fields.append(_weight)

    for i, account in enumerate(auth.accounts):
        _account = helpers.eos_name_to_string(account.account.actor)
        _permission = helpers.eos_name_to_string(account.account.permission)

        a_header = "Account #{}:".format(i + 1)
        p_header = "Acc Permission #{}:".format(i + 1)
        w_header = "Account #{} weight:".format(i + 1)

        fields.append(a_header)
        fields.append(_account)
        fields.append(p_header)
        fields.append(_permission)
        fields.append(w_header)
        fields.append(account.weight)

    for i, wait in enumerate(auth.waits):
        _wait = wait.wait_sec
        _weight = wait.weight

        header = "Delay #{}".format(i + 1)
        w_height = "Delay #{} weight:".format(i + 1)
        fields.append(header)
        fields.append("{} sec".format(_wait))
        fields.append(w_height)
        fields.append(_weight)

    return fields
