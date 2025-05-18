#          █▄▀ ▄▀█ █▀▄▀█ █▀▀ █▄▀ █  █ █▀█ █▀█
#          █ █ █▀█ █ ▀ █ ██▄ █ █ ▀▄▄▀ █▀▄ █▄█ ▄
#                © Copyright 2024
#            ✈ https://t.me/kamekuro

# 🔒 Licensed under CC-BY-NC-ND 4.0 unless otherwise specified.
# 🌐 https://creativecommons.org/licenses/by-nc-nd/4.0
# + attribution
# + non-commercial
# + no-derivatives

# You CANNOT edit, distribute or redistribute and use for any purpose this file without direct permission from the author.
# All source code is provided for review only.

import logging
import typing

import pyrogram

import utils
from . import filters as flts


logger = logging.getLogger(__name__)


class Router():
    def __init__(self, name: str, description: str = "", is_for_all: bool = False) -> None:
        self._app = None
        self._decorators_storage: list = []
        self.name = name
        if not description:
            description = f"Router [{self.name}]"
        self.is_for_all = is_for_all
        self.description = description


    def set_client(self, client: pyrogram.Client) -> None:
        self._app = client
        for decorator in self._decorators_storage:
            self._app.add_handler(
                    *decorator
            )


    def on_callback_query(self, filters=None, group: int = 0) -> typing.Callable:
        """Decorator for handling callback queries.

        This does the same thing as :meth:`~pyrogram.Client.add_handler` using the
        :obj:`~pyrogram.handlers.CallbackQueryHandler`.

        Parameters:
            filters (:obj:`~pyrogram.filters`, *optional*):
                Pass one or more filters to allow only a subset of callback queries to be passed
                in your function.

            group (``int``, *optional*):
                The group identifier, defaults to 0.
        """

        def decorator(func: typing.Callable) -> typing.Callable:
            if self._app is not None:
                self._app.add_handler(
                    pyrogram.handlers.CallbackQueryHandler(func, filters), group
                )
            else:
                self._decorators_storage.append((pyrogram.handlers.CallbackQueryHandler(func, filters), group))

            return func

        return decorator


    def on_chat_boost(self, filters=None, group: int = 0) -> typing.Callable:
        """Decorator for handling applied chat boosts.

        This does the same thing as :meth:`~pyrogram.Client.add_handler` using the
        :obj:`~pyrogram.handlers.ChatBoostHandler`.

        Parameters:
            filters (:obj:`~pyrogram.filters`, *optional*):
                Pass one or more filters to allow only a subset of callback queries to be passed
                in your function.

            group (``int``, *optional*):
                The group identifier, defaults to 0.

        """
        # pyrogram.handlers.ChatBoostHandler on_chat_boost

        def decorator(func: typing.Callable) -> typing.Callable:
            if self._app is not None:
                self._app.add_handler(
                    pyrogram.handlers.ChatBoostHandler(func, filters), group
                )
            else:
                self._decorators_storage.append((pyrogram.handlers.ChatBoostHandler(func, filters), group))

            return func

        return decorator


    def on_chat_join_request(self, filters=None, group: int = 0) -> typing.Callable:
        """Decorator for handling chat join requests.

        This does the same thing as :meth:`~pyrogram.Client.add_handler` using the
        :obj:`~pyrogram.handlers.ChatJoinRequestHandler`.

        Parameters:
            filters (:obj:`~pyrogram.filters`, *optional*):
                Pass one or more filters to allow only a subset of updates to be passed in your function.

            group (``int``, *optional*):
                The group identifier, defaults to 0.
        """

        def decorator(func: typing.Callable) -> typing.Callable:
            if self._app is not None:
                self._app.add_handler(
                    pyrogram.handlers.ChatJoinRequestHandler(func, filters), group
                )
            else:
                self._decorators_storage.append((pyrogram.handlers.ChatJoinRequestHandler(func, filters), group))
            return func

        return decorator


    def on_chat_member_updated(self, filters=None, group: int = 0) -> typing.Callable:
        """Decorator for handling event changes on chat members.

        This does the same thing as :meth:`~pyrogram.Client.add_handler` using the
        :obj:`~pyrogram.handlers.ChatMemberUpdatedHandler`.

        Parameters:
            filters (:obj:`~pyrogram.filters`, *optional*):
                Pass one or more filters to allow only a subset of updates to be passed in your function.

            group (``int``, *optional*):
                The group identifier, defaults to 0.
        """

        def decorator(func: typing.Callable) -> typing.Callable:
            if self._app is not None:
                self._app.add_handler(
                    pyrogram.handlers.ChatMemberUpdatedHandler(func, filters), group
                )
            else:
                self._decorators_storage.append((pyrogram.handlers.ChatMemberUpdatedHandler(func, filters), group))
            return func

        return decorator


    def on_chosen_inline_result(self, filters=None, group: int = 0) -> typing.Callable:
        """Decorator for handling chosen inline results.

        This does the same thing as :meth:`~pyrogram.Client.add_handler` using the
        :obj:`~pyrogram.handlers.ChosenInlineResultHandler`.

        Parameters:
            filters (:obj:`~pyrogram.filters`, *optional*):
                Pass one or more filters to allow only a subset of chosen inline results to be passed
                in your function.

            group (``int``, *optional*):
                The group identifier, defaults to 0.
        """

        def decorator(func: typing.Callable) -> typing.Callable:
            if self._app is not None:
                self._app.add_handler(
                    pyrogram.handlers.ChosenInlineResultHandler(func, filters), group
                )
            else:
                self._decorators_storage.append((pyrogram.handlers.ChosenInlineResultHandler(func, filters), group))
            return func

        return decorator


    def on_deleted_messages(self, filters=None, group: int = 0) -> typing.Callable:
        """Decorator for handling deleted messages.

        This does the same thing as :meth:`~pyrogram.Client.add_handler` using the
        :obj:`~pyrogram.handlers.DeletedMessagesHandler`.

        Parameters:
            filters (:obj:`~pyrogram.filters`, *optional*):
                Pass one or more filters to allow only a subset of messages to be passed
                in your function.

            group (``int``, *optional*):
                The group identifier, defaults to 0.
        """
        filters = (filters &~ pyrogram.filters.business) if filters else ~pyrogram.filters.business

        def decorator(func: typing.Callable) -> typing.Callable:
            if self._app is not None:
                self._app.add_handler(
                    pyrogram.handlers.DeletedMessagesHandler(func, filters), group
                )
            else:
                self._decorators_storage.append((pyrogram.handlers.DeletedMessagesHandler(func, filters), group))
            return func

        return decorator


    def on_deleted_business_messages(self, filters=None, group: int = 0) -> typing.Callable:
        """Decorator for handling deleted business messages.

        This does the same thing as :meth:`~pyrogram.Client.add_handler` using the
        :obj:`~pyrogram.handlers.DeletedMessagesHandler`.

        Parameters:
            filters (:obj:`~pyrogram.filters`, *optional*):
                Pass one or more filters to allow only a subset of messages to be passed
                in your function.

            group (``int``, *optional*):
                The group identifier, defaults to 0.
        """

        f = pyrogram.filters.business
        filters = filters&f if filters else f

        def decorator(func: typing.Callable) -> typing.Callable:
            if self._app is not None:
                self._app.add_handler(
                    pyrogram.handlers.DeletedMessagesHandler(func, filters), group
                )
            else:
                self._decorators_storage.append((pyrogram.handlers.DeletedMessagesHandler(func, filters), group))
            return func

        return decorator


    def on_disconnect(self) -> typing.Callable:
        """Decorator for handling disconnections.

        This does the same thing as :meth:`~pyrogram.Client.add_handler` using the
        :obj:`~pyrogram.handlers.DisconnectHandler`.
        """

        def decorator(func: typing.Callable) -> typing.Callable:
            if self._app is not None:
                self._app.add_handler(
                    pyrogram.handlers.DisconnectHandler(func)
                )
            else:
                self._decorators_storage.append((pyrogram.handlers.DisconnectHandler(func)))
            return func

        return decorator


    def on_edited_message(self, filters=None, group: int = 0) -> typing.Callable:
        """Decorator for handling edited messages.

        This does the same thing as :meth:`~pyrogram.Client.add_handler` using the
        :obj:`~pyrogram.handlers.EditedMessageHandler`.

        Parameters:
            filters (:obj:`~pyrogram.filters`, *optional*):
                Pass one or more filters to allow only a subset of messages to be passed
                in your function.

            group (``int``, *optional*):
                The group identifier, defaults to 0.
        """
        filters = (filters &~ pyrogram.filters.business) if filters else ~pyrogram.filters.business

        def decorator(func: typing.Callable) -> typing.Callable:
            if self._app is not None:
                self._app.add_handler(
                    pyrogram.handlers.EditedMessageHandler(func, filters), group
                )
            else:
                self._decorators_storage.append((pyrogram.handlers.EditedMessageHandler(func, filters), group))
            return func

        return decorator


    def on_edited_business_message(self, filters=None, group: int = 0) -> typing.Callable:
        """Decorator for handling edited business messages.

        This does the same thing as :meth:`~pyrogram.Client.add_handler` using the
        :obj:`~pyrogram.handlers.EditedMessageHandler`.

        Parameters:
            filters (:obj:`~pyrogram.filters`, *optional*):
                Pass one or more filters to allow only a subset of messages to be passed
                in your function.

            group (``int``, *optional*):
                The group identifier, defaults to 0.
        """

        f = pyrogram.filters.business
        filters = filters&f if filters else f

        def decorator(func: typing.Callable) -> typing.Callable:
            if self._app is not None:
                self._app.add_handler(
                    pyrogram.handlers.EditedMessageHandler(func, filters), group
                )
            else:
                self._decorators_storage.append((pyrogram.handlers.EditedMessageHandler(func, filters), group))
            return func

        return decorator


    def on_inline_query(self, filters=None, group: int = 0) -> typing.Callable:
        """Decorator for handling inline queries.

        This does the same thing as :meth:`~pyrogram.Client.add_handler` using the
        :obj:`~pyrogram.handlers.InlineQueryHandler`.

        Parameters:
            filters (:obj:`~pyrogram.filters`, *optional*):
                Pass one or more filters to allow only a subset of inline queries to be passed
                in your function.

            group (``int``, *optional*):
                The group identifier, defaults to 0.
        """

        def decorator(func: typing.Callable) -> typing.Callable:
            if self._app is not None:
                self._app.add_handler(
                    pyrogram.handlers.InlineQueryHandler(func, filters), group
                )
            else:
                self._decorators_storage.append((pyrogram.handlers.InlineQueryHandler(func, filters), group))
            return func

        return decorator


    def on_message_reaction_count(self, filters=None, group: int = 0) -> typing.Callable:
        """Decorator for handling anonymous reaction changes on messages.

        This does the same thing as :meth:`~pyrogram.Client.add_handler` using the
        :obj:`~pyrogram.handlers.MessageReactionCountHandler`.

        Parameters:
            filters (:obj:`~pyrogram.filters`, *optional*):
                Pass one or more filters to allow only a subset of updates to be passed in your function.

            group (``int``, *optional*):
                The group identifier, defaults to 0.
        """

        def decorator(func: typing.Callable) -> typing.Callable:
            if self._app is not None:
                self._app.add_handler(
                    pyrogram.handlers.MessageReactionCountHandler(func, filters), group
                )
            else:
                self._decorators_storage.append((pyrogram.handlers.MessageReactionCountHandler(func, filters), group))
            return func

        return decorator


    def on_message_reaction(self, filters=None, group: int = 0) -> typing.Callable:
        """Decorator for handling reaction changes on messages.

        This does the same thing as :meth:`~pyrogram.Client.add_handler` using the
        :obj:`~pyrogram.handlers.MessageReactionHandler`.

        Parameters:
            filters (:obj:`~pyrogram.filters`, *optional*):
                Pass one or more filters to allow only a subset of updates to be passed in your function.

            group (``int``, *optional*):
                The group identifier, defaults to 0.
        """

        def decorator(func: typing.Callable) -> typing.Callable:
            if self._app is not None:
                self._app.add_handler(
                    pyrogram.handlers.MessageReactionHandler(func, filters), group
                )
            else:
                self._decorators_storage.append((pyrogram.handlers.MessageReactionHandler(func, filters), group))
            return func

        return decorator


    def on_message(self, filters=None, group: int = 0) -> typing.Callable:
        """Decorator for handling new messages.

        This does the same thing as :meth:`~pyrogram.Client.add_handler` using the
        :obj:`~pyrogram.handlers.MessageHandler`.

        Parameters:
            filters (:obj:`~pyrogram.filters`, *optional*):
                Pass one or more filters to allow only a subset of messages to be passed
                in your function.

            group (``int``, *optional*):
                The group identifier, defaults to 0.
        """
        filters = (filters &~ pyrogram.filters.business) if filters else ~pyrogram.filters.business

        def decorator(func: typing.Callable) -> typing.Callable:
            if self._app is not None:
                self._app.add_handler(
                    pyrogram.handlers.MessageHandler(func, filters), group
                )
            else:
                self._decorators_storage.append((pyrogram.handlers.MessageHandler(func, filters), group))
            return func

        return decorator


    def on_business_message(self, filters=None, group: int = 0) -> typing.Callable:
        """Decorator for handling new business messages.

        This does the same thing as :meth:`~pyrogram.Client.add_handler` using the
        :obj:`~pyrogram.handlers.MessageHandler`.

        Parameters:
            filters (:obj:`~pyrogram.filters`, *optional*):
                Pass one or more filters to allow only a subset of messages to be passed
                in your function.

            group (``int``, *optional*):
                The group identifier, defaults to 0.
        """

        f = pyrogram.filters.business
        filters = filters&f if filters else f

        def decorator(func: typing.Callable) -> typing.Callable:
            if self._app is not None:
                self._app.add_handler(
                    pyrogram.handlers.MessageHandler(func, filters), group
                )
            else:
                self._decorators_storage.append((pyrogram.handlers.MessageHandler(func, filters), group))
            return func

        return decorator


    def on_start(self, group: int = 0) -> typing.Callable:
        """Decorator for handling «start» messages.

        This does the same thing as :meth:`~pyrogram.Client.add_handler` using the
        :obj:`~pyrogram.handlers.MessageHandler`.

        Parameters:
            group (``int``, *optional*):
                The group identifier, defaults to 0.
        """

        filters = flts.text(["/start", "/старт", "!start", "!старт"])
        def decorator(func: typing.Callable) -> typing.Callable:
            if self._app is not None:
                self._app.add_handler(
                    pyrogram.handlers.MessageHandler(func, filters), group
                )
            else:
                self._decorators_storage.append((pyrogram.handlers.MessageHandler(func, filters), group))
            return func

        return decorator


    def on_poll(self, filters=None, group: int = 0) -> typing.Callable:
        """Decorator for handling poll updates.

        This does the same thing as :meth:`~pyrogram.Client.add_handler` using the
        :obj:`~pyrogram.handlers.PollHandler`.

        Parameters:
            filters (:obj:`~pyrogram.filters`, *optional*):
                Pass one or more filters to allow only a subset of polls to be passed
                in your function.

            group (``int``, *optional*):
                The group identifier, defaults to 0.
        """

        def decorator(func: typing.Callable) -> typing.Callable:
            if self._app is not None:
                self._app.add_handler(
                    pyrogram.handlers.PollHandler(func, filters), group
                )
            else:
                self._decorators_storage.append((pyrogram.handlers.PollHandler(func, filters), group))
            return func

        return decorator


    def on_pre_checkout_query(self, filters=None, group: int = 0) -> typing.Callable:
        """Decorator for handling pre-checkout queries.

        This does the same thing as :meth:`~pyrogram.Client.add_handler` using the
        :obj:`~pyrogram.handlers.PreCheckoutQueryHandler`.

        Parameters:
            filters (:obj:`~pyrogram.filters`, *optional*):
                Pass one or more filters to allow only a subset of callback queries to be passed
                in your function.

            group (``int``, *optional*):
                The group identifier, defaults to 0.
        """

        def decorator(func: typing.Callable) -> typing.Callable:
            if self._app is not None:
                self._app.add_handler(
                    pyrogram.handlers.PreCheckoutQueryHandler(func, filters), group
                )
            else:
                self._decorators_storage.append((pyrogram.handlers.PreCheckoutQueryHandler(func, filters), group))
            return func

        return decorator


    def on_purchased_paid_media(self, filters=None, group: int = 0) -> typing.Callable:
        """Decorator for handling purchased paid media.

        This does the same thing as :meth:`~pyrogram.Client.add_handler` using the
        :obj:`~pyrogram.handlers.PurchasedPaidMediaHandler`.

        Parameters:
            filters (:obj:`~pyrogram.filters`, *optional*):
                Pass one or more filters to allow only a subset of updates to be passed in your function.

            group (``int``, *optional*):
                The group identifier, defaults to 0.
        """

        def decorator(func: typing.Callable) -> typing.Callable:
            if self._app is not None:
                self._app.add_handler(
                    pyrogram.handlers.PurchasedPaidMediaHandler(func, filters), group
                )
            else:
                self._decorators_storage.append((pyrogram.handlers.PurchasedPaidMediaHandler(func, filters), group))
            return func

        return decorator


    def on_raw_update(self, group: int = 0) -> typing.Callable:
        """Decorator for handling raw updates.

        This does the same thing as :meth:`~pyrogram.Client.add_handler` using the
        :obj:`~pyrogram.handlers.RawUpdateHandler`.

        Parameters:
            group (``int``, *optional*):
                The group identifier, defaults to 0.
        """

        def decorator(func: typing.Callable) -> typing.Callable:
            if self._app is not None:
                self._app.add_handler(
                    pyrogram.handlers.RawUpdateHandler(func), group
                )
            else:
                self._decorators_storage.append((pyrogram.handlers.RawUpdateHandler(func), group))
            return func

        return decorator


    def on_shipping_query(self, filters=None, group: int = 0) -> typing.Callable:
        """Decorator for handling shipping queries.

        This does the same thing as :meth:`~pyrogram.Client.add_handler` using the
        :obj:`~pyrogram.handlers.ShippingQueryHandler`.

        Parameters:
            filters (:obj:`~pyrogram.filters`, *optional*):
                Pass one or more filters to allow only a subset of callback queries to be passed
                in your function.

            group (``int``, *optional*):
                The group identifier, defaults to 0.
        """

        def decorator(func: typing.Callable) -> typing.Callable:
            if self._app is not None:
                self._app.add_handler(
                    pyrogram.handlers.ShippingQueryHandler(func, filters), group
                )
            else:
                self._decorators_storage.append((pyrogram.handlers.ShippingQueryHandler(func, filters), group))
            return func

        return decorator


    def on_story(self, filters=None, group: int = 0) -> typing.Callable:
        """Decorator for handling new stories.

        This does the same thing as :meth:`~pyrogram.Client.add_handler` using the
        :obj:`~pyrogram.handlers.StoryHandler`.

        Parameters:
            filters (:obj:`~pyrogram.filters`, *optional*):
                Pass one or more filters to allow only a subset of stories to be passed
                in your function.

            group (``int``, *optional*):
                The group identifier, defaults to 0.
        """

        def decorator(func: typing.Callable) -> typing.Callable:
            if self._app is not None:
                self._app.add_handler(
                    pyrogram.handlers.StoryHandler(func, filters), group
                )
            else:
                self._decorators_storage.append((pyrogram.handlers.StoryHandler(func, filters), group))
            return func

        return decorator


    def on_user_status(self, filters=None, group: int = 0) -> typing.Callable:
        """Decorator for handling user status updates.
        This does the same thing as :meth:`~pyrogram.Client.add_handler` using the
        :obj:`~pyrogram.handlers.UserStatusHandler`.

        Parameters:
            filters (:obj:`~pyrogram.filters`, *optional*):
                Pass one or more filters to allow only a subset of UserStatus updated to be passed in your function.

            group (``int``, *optional*):
                The group identifier, defaults to 0.
        """

        def decorator(func: typing.Callable) -> typing.Callable:
            if self._app is not None:
                self._app.add_handler(
                    pyrogram.handlers.UserStatusHandler(func, filters), group
                )
            else:
                self._decorators_storage.append((pyrogram.handlers.UserStatusHandler(func, filters), group))
            return func

        return decorator