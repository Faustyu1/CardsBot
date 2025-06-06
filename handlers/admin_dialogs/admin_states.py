from aiogram.fsm.state import State, StatesGroup


class AdminSG(StatesGroup):
    menu = State()
    reset_season = State()
    statistics = State()
    update_users = State()
    export = State()
    choose_ref_action = State()


class PremiumSG(StatesGroup):
    premium_get_id = State()
    premium_get_date = State()
    premium_accept = State()
    error = State()
    all_good = State()


class BanSG(StatesGroup):
    get_id = State()
    error = State()
    user_is_banned = State()
    accept = State()
    all_ok = State()


class AddAdminSG(StatesGroup):
    get_id = State()
    error = State()
    user_is_banned = State()
    accept = State()
    all_ok = State()


class UnBanSG(StatesGroup):
    get_id = State()
    error = State()
    user_not_banned = State()
    accept = State()
    all_ok = State()


class DelSeasonSG(StatesGroup):
    accept_del = State()
    accept_2 = State()
    accept_3 = State()
    season_del = State()
    error = State()


class ChangeUsernameSG(StatesGroup):
    get_id = State()
    get_new_username = State()
    accept = State()
    changed = State()
    error = State()


class MailingSG(StatesGroup):
    choose_type = State()
    get_message = State()
    get_media = State()
    send_message = State()
    error = State()


class CreatePromoSG(StatesGroup):
    get_name = State()
    get_action = State()
    get_premium_days = State()
    get_channel = State()
    get_expiration_time = State()
    get_activation_limit = State()
    accept = State()
    all_ok = State()


class DeletePromoSG(StatesGroup):
    get_name = State()
    accept = State()
    all_ok = State()


class AddRefLinkSG(StatesGroup):
    get_link = State()
    all_ok = State()
    error = State()


class ViewRefLinkSG(StatesGroup):
    link_list = State()
    one_link = State()
