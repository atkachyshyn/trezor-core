from apps.eos import consts, updaters
from apps.eos.actions import layout


async def process_action(ctx, sha, action):
    updaters.hashupdate_action_common(sha, action.common)
    if action.buy_ram is not None:
        await layout.confirm_action_buyram(ctx, action.buy_ram)
        updaters.hashupdate_action_buyram(sha, action.buy_ram)
    elif action.buy_ram_bytes is not None:
        await layout.confirm_action_buyrambytes(ctx, action.buy_ram_bytes)
        updaters.hashupdate_action_buyrambytes(sha, action.buy_ram_bytes)
    elif action.sell_ram is not None:
        await layout.confirm_action_sellram(ctx, action.sell_ram)
        updaters.hashupdate_action_sellram(sha, action.sell_ram)
    elif action.delegate is not None:
        await layout.confirm_action_delegate(ctx, action.delegate)
        updaters.hashupdate_action_delegate(sha, action.delegate)
    elif action.undelegate is not None:
        await layout.confirm_action_undelegate(ctx, action.undelegate)
        updaters.hashupdate_action_undelegate(sha, action.undelegate)
    elif action.refund is not None:
        await layout.confirm_action_refund(ctx, action.refund)
        updaters.hashupdate_action_refund(sha, action.refund)
    elif action.transfer is not None:
        await layout.confirm_action_transfer(ctx, action.transfer)
        updaters.hashupdate_action_transfer(sha, action.transfer)
    elif action.vote_producer is not None:
        await layout.confirm_action_voteproducer(ctx, action.vote_producer)
        updaters.hashupdate_action_voteproducer(sha, action.vote_producer)
    elif action.update_auth is not None:
        await layout.confirm_action_updateauth(ctx, action.update_auth)
        updaters.hashupdate_action_updateauth(sha, action.update_auth)
    elif action.delete_auth is not None:
        await layout.confirm_action_deleteauth(ctx, action.delete_auth)
        updaters.hashupdate_action_deleteauth(sha, action.delete_auth)
    elif action.link_auth is not None:
        await layout.confirm_action_linkauth(ctx, action.link_auth)
        updaters.hashupdate_action_linkauth(sha, action.link_auth)
    elif action.unlink_auth is not None:
        await layout.confirm_action_unlinkauth(ctx, action.unlink_auth)
        updaters.hashupdate_action_unlinkauth(sha, action.unlink_auth)
    elif action.new_account is not None:
        await layout.confirm_action_newaccount(ctx, action.new_account)
        updaters.hashupdate_action_newaccount(sha, action.new_account)
    elif action.unknown is not None:
        await layout.confirm_action_unknown(ctx, action.common.name, action.unknown)
        updaters.hashupdate_action_unknown(sha, action.unknown)
    else:
        raise ValueError("Unknown action")
