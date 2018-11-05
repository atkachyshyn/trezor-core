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
from trezor.messages import EosActionUnknown


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
FOUR_FIELDS_PER_PAGE = 4
FIVE_FIELDS_PER_PAGE = 5


def confirm_action_buyram(ctx, msg: EosActionBuyRam):
    await ctx.call(ButtonRequest(code=ButtonRequestType.ConfirmOutput), MessageType.ButtonAck)
    text = "Buy RAM"
    payer_txt = "Payer:"
    payer = (helpers.eos_name_to_string(msg.payer))
    receiver_txt = "Receiver:"
    receiver = (helpers.eos_name_to_string(msg.receiver))
    amount_txt = ("Amount:")
    amount = (helpers.eos_asset_to_string(msg.quantity))

    fields = [payer_txt, payer, receiver_txt, receiver, amount_txt, amount]

    pages = list(chunks(fields, FOUR_FIELDS_PER_PAGE))

    paginator = paginate(show_lines_page, len(pages), FIRST_PAGE, pages, text)
    await ctx.wait(paginator)

def confirm_action_buyrambytes(ctx, msg: EosActionBuyRamBytes):
    await ctx.call(ButtonRequest(code=ButtonRequestType.ConfirmOutput), MessageType.ButtonAck)

    text = "Buy RAM"
    payer_txt = "Payer:"
    payer = (helpers.eos_name_to_string(msg.payer))
    receiver_txt = "Receiver:"
    receiver = (helpers.eos_name_to_string(msg.receiver))
    amount_txt = "Bytes:"
    amount = str(msg.bytes)

    fields = [payer_txt, payer, receiver_txt, receiver, amount_txt, amount]

    pages = list(chunks(fields, FOUR_FIELDS_PER_PAGE))

    paginator = paginate(show_lines_page, len(pages), FIRST_PAGE, pages, text)
    await ctx.wait(paginator)

def confirm_action_delegate(ctx, msg: EosActionDelegate):
    await ctx.call(ButtonRequest(code=ButtonRequestType.ConfirmOutput), MessageType.ButtonAck)

    text = "Delegate"
    sender_txt = "Sender:"
    sender = (helpers.eos_name_to_string(msg.sender))
    receiver_txt = "Receiver:"
    receiver = (helpers.eos_name_to_string(msg.receiver))
    cpu_txt = "CPU:"
    cpu = (helpers.eos_asset_to_string(msg.cpu_quantity))
    net_txt = "NET:"
    net = (helpers.eos_asset_to_string(msg.net_quantity))

    fields = [sender_txt, sender, receiver_txt, receiver, cpu_txt, cpu, net_txt, net]

    if msg.transfer:
        transfer_txt = "Transfer to:"
        transfer = (helpers.eos_name_to_string(msg.receiver))
        fields.append(transfer_txt)
        fields.append(transfer)

    pages = list(chunks(fields, FOUR_FIELDS_PER_PAGE))
    paginator = paginate(show_lines_page, len(pages), FIRST_PAGE, pages, text)

    await ctx.wait(paginator)

def confirm_action_sellram(ctx, msg: EosActionSellRam):
    await ctx.call(ButtonRequest(code=ButtonRequestType.ConfirmOutput), MessageType.ButtonAck)

    text = "Sell RAM"
    receiver_txt = "Receiver:"
    receiver = (helpers.eos_name_to_string(msg.account))
    amount_txt = "Bytes:"
    amount = str(msg.bytes)
    
    fields = [receiver_txt, receiver, amount_txt, amount]
    pages = list(chunks(fields, TWO_FIELDS_PER_PAGE))
    paginator = paginate(show_lines_page, len(pages), FIRST_PAGE, pages, text)

    await ctx.wait(paginator)

def confirm_action_undelegate(ctx, msg: EosActionUndelegate):
    await ctx.call(ButtonRequest(code=ButtonRequestType.ConfirmOutput), MessageType.ButtonAck)

    text = "Undelegate"
    sender_txt = "Sender:" 
    sender = (helpers.eos_name_to_string(msg.sender))
    receiver_txt = "Receiver:"
    receiver = (helpers.eos_name_to_string(msg.receiver))
    cpu_txt = "CPU:"
    cpu = (helpers.eos_asset_to_string(msg.cpu_quantity))
    net_txt = "NET:"
    net = (helpers.eos_asset_to_string(msg.net_quantity))

    fields = [sender_txt, sender, receiver_txt, receiver, cpu_txt, cpu, net_txt, net]
    pages = list(chunks(fields, FOUR_FIELDS_PER_PAGE))
    paginator = paginate(show_lines_page, len(pages), FIRST_PAGE, pages, text)

    await ctx.wait(paginator)

def confirm_action_refund(ctx, msg: EosActionRefund):
    text = Text("Refund", ui.ICON_CONFIRM, icon_color=ui.GREEN)
    text.normal("Owner:")
    text.normal(helpers.eos_name_to_string(msg.owner))
    await require_confirm(ctx, text, ButtonRequestType.ConfirmOutput)

def confirm_action_voteproducer(ctx, msg: EosActionVoteProducer):
    if msg.proxy != 0 and len(msg.producers) == 0:
        # PROXY
        text = Text("Vote for proxy", ui.ICON_CONFIRM, icon_color=ui.GREEN)
        text.normal("Voter:")
        text.normal(helpers.eos_name_to_string(msg.voter))
        text.normal("Proxy:")
        text.normal(helpers.eos_name_to_string(msg.proxy))
        await require_confirm(ctx, text, ButtonRequestType.ConfirmOutput)

    elif len(msg.producers) > 0:
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
    sender_txt = "Sender:"
    sender = (helpers.eos_name_to_string(msg.sender))
    receiver_txt = "Receiver"
    receiver = (helpers.eos_name_to_string(msg.receiver))
    amount_txt = "Amount:"
    amount = (helpers.eos_asset_to_string(msg.quantity))

    fields = [sender_txt, sender, receiver_txt, receiver, amount_txt, amount]

    if msg.memo is not None:
        memo_txt = "Memo:"
        memo = (msg.memo[:512])
        fields.append(memo_txt)
        fields.append(memo)

    pages = list(chunks(fields, FOUR_FIELDS_PER_PAGE))

    paginator = paginate(show_lines_page, len(pages), FIRST_PAGE, pages, text)
    await ctx.wait(paginator)

def confirm_action_updateauth(ctx, msg: EosActionUpdateAuth):
    await ctx.call(ButtonRequest(code=ButtonRequestType.ConfirmOutput), MessageType.ButtonAck)

    text = "Update Auth"
    account_txt = "Account:"
    account = (helpers.eos_name_to_string(msg.account))
    permission_txt = "Permission:"
    permission = (helpers.eos_name_to_string(msg.permission))
    parent_txt = "Parent:"
    parent = (helpers.eos_name_to_string(msg.parent))

    fields = [account_txt, account, permission_txt, permission, parent_txt, parent]
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
    account_txt = "Account:"
    account = (helpers.eos_name_to_string(msg.account))
    code_txt = "Code:"
    code = (helpers.eos_name_to_string(msg.code))
    type_txt = "Type:"
    msg_type = (helpers.eos_name_to_string(msg.type))
    requirement_txt = "Requirement:"
    requirement = (helpers.eos_name_to_string(msg.requirement))
    
    fields = [account_txt, account, code_txt, code, type_txt, msg_type, requirement_txt, requirement]
    pages = list(chunks(fields, FOUR_FIELDS_PER_PAGE))
    paginator = paginate(show_lines_page, len(pages), FIRST_PAGE, pages, text)

    await ctx.wait(paginator)

def confirm_action_unlinkauth(ctx, msg: EosActionUnlinkAuth):
    await ctx.call(ButtonRequest(code=ButtonRequestType.ConfirmOutput), MessageType.ButtonAck)

    text = "Unlink Auth"
    account_txt = "Account:"
    account = (helpers.eos_name_to_string(msg.account))
    code_txt = "Code:"
    code = (helpers.eos_name_to_string(msg.code))
    type_txt = "Type:"
    msg_type = (helpers.eos_name_to_string(msg.type))

    fields = [account_txt, account, code_txt, code, type_txt, msg_type]
    pages = list(chunks(fields, FOUR_FIELDS_PER_PAGE))
    paginator = paginate(show_lines_page, len(pages), FIRST_PAGE, pages, text)

    await ctx.wait(paginator)

def confirm_action_newaccount(ctx, msg: EosActionNewAccount):
    await ctx.call(ButtonRequest(code=ButtonRequestType.ConfirmOutput), MessageType.ButtonAck)

    text = "New Account"
    creator_txt = "Creator:"
    creator = (helpers.eos_name_to_string(msg.creator))
    name_txt = "Name:"
    name = (helpers.eos_name_to_string(msg.name))

    fields = [creator_txt, creator, name_txt, name]
    fields += authorization_fields(msg.owner)
    fields += authorization_fields(msg.active)

    pages = list(chunks(fields, TWO_FIELDS_PER_PAGE))
    paginator = paginate(show_lines_page, len(pages), FIRST_PAGE, pages, text)

    await ctx.wait(paginator)

def confirm_action_unknown(ctx, name, msg: EosActionUnknown):
    # TODO: DO it properly
    text = Text("{} Action".format(helpers.eos_name_to_string(name)), ui.ICON_CONFIRM, icon_color=ui.GREEN)
    text.normal("do it at your own risk") 
    await require_confirm(ctx, text, ButtonRequestType.ConfirmOutput)

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
