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

import contextlib
import html
import inspect
import json
import logging
import logging.handlers
import os
import re
import traceback
import typing

import pyrogram
import requests

from utils import config



def find_caller(
    stack: typing.Optional[typing.List[inspect.FrameInfo]] = None,
) -> typing.Any:
    """
    Attempts to find command in stack
    :param stack: Stack to search in
    :return: Command-caller or None
    """
    caller = next(
        (
            frame_info
            for frame_info in stack or inspect.stack()
            if hasattr(frame_info, "function")
        ),
        None,
    )

    if not caller:
        return next(
            (
                frame_info.frame.f_locals["func"]
                for frame_info in stack or inspect.stack()
                if hasattr(frame_info, "function")
                and frame_info.function == "future_dispatcher"
                and (
                    "CommandDispatcher"
                    in getattr(getattr(frame_info, "frame", None), "f_globals", {})
                )
            ),
            None,
        )

    return next(
        (
            getattr(cls_, caller.function, None)
            for cls_ in caller.frame.f_globals.values()
        ),
        None,
    )



class CustomException:
    def __init__(
        self,
        message: str,
        local_vars: str,
        full_stack: str,
        sysinfo: typing.Optional[
            typing.Tuple[object, Exception, traceback.TracebackException]
        ] = None,
    ):
        self.message = message
        self.local_vars = local_vars
        self.full_stack = full_stack
        self.sysinfo = sysinfo
        self.debug_url = None


    @classmethod
    def from_exc_info(
        cls,
        exc_type: object,
        exc_value: Exception,
        tb: traceback.TracebackException,
        stack: typing.Optional[typing.List[inspect.FrameInfo]] = None,
    ) -> "CustomException":
        def to_hashable(dictionary: dict) -> dict:
            dictionary = dictionary.copy()
            for key, value in dictionary.items():
                if isinstance(value, dict):
                    dictionary[key] = to_hashable(value)
                else:
                    try:
                        if (
                            getattr(getattr(value, "__class__", None), "__name__", None)
                            == "Database"
                        ):
                            dictionary[key] = "<Database>"
                        elif isinstance(
                            value,
                            (pyrogram.Client),
                        ):
                            dictionary[key] = f"<{value.__class__.__name__}>"
                        elif len(str(value)) > 512:
                            dictionary[key] = f"{str(value)[:512]}..."
                        else:
                            dictionary[key] = str(value)
                    except Exception:
                        dictionary[key] = f"<{value.__class__.__name__}>"

            return dictionary

        full_stack = traceback.format_exc().replace(
            "Traceback (most recent call last):\n", ""
        )

        line_regex = r'  File "(.*?)", line ([0-9]+), in (.+)'

        def format_line(line: str) -> str:
            filename_, lineno_, name_ = re.search(line_regex, line).groups()
            with contextlib.suppress(Exception):
                filename_ = os.path.basename(filename_)

            return (
                f"👉 <code>{html.escape(filename_)}:{lineno_}</code> <b>in</b>"
                f" <code>{html.escape(name_)}</code>"
            )

        filename, lineno, name = next(
            (
                re.search(line_regex, line).groups()
                for line in reversed(full_stack.splitlines())
                if re.search(line_regex, line)
            ),
            (None, None, None),
        )

        full_stack = "\n".join(
            [
                (
                    format_line(line)
                    if re.search(line_regex, line)
                    else f"<code>{html.escape(line)}</code>"
                )
                for line in full_stack.splitlines()
            ]
        )

        with contextlib.suppress(Exception):
            filename = os.path.basename(filename)

        caller = find_caller(stack or inspect.stack())
        cause_mod = (
            "🪬 <b>Possible cause: method"
            f" </b><code>{html.escape(caller.__name__)}</code><b> of module"
            f" </b><code>{html.escape(caller.__self__.__class__.__name__)}</code>\n"
            if caller and hasattr(caller, "__self__") and hasattr(caller, "__name__")
            else ""
        )

        return CustomException(
            message=(
                f"<b>🚫 Error!</b>\n{cause_mod}\n<b>🗄 Where:</b>"
                f" <code>{html.escape(filename)}:{lineno}</code><b>"
                f" in </b><code>{html.escape(name)}</code>\n<b>❓ What:</b>"
                f" <code>{html.escape(''.join(traceback.format_exception_only(exc_type, exc_value)).strip())}</code>"
            ),
            local_vars=(
                f"<code>{html.escape(json.dumps(to_hashable(tb.tb_frame.f_locals), indent=4))}</code>"
            ),
            full_stack=full_stack,
            sysinfo=(exc_type, exc_value, tb),
        )


class TelegramErrorHandler(logging.Handler):
    def __init__(self):
        super().__init__()

    def emit(self, record: logging.LogRecord):
        print(record.levelno, type(record.levelno))
        if record.levelno < 40:
            formatted_message = f"<code>[{record.levelname}] [{html.escape(str(record.name))}:{html.escape(str(record.lineno))}]\n>>> {html.escape(str(record.getMessage()))}</code>"
        else:
            if record.exc_info:
                exc = CustomException.from_exc_info(*record.exc_info)
                full_err = '\n'.join(exc.full_stack.splitlines()[:-1])
                min_err = exc.full_stack.splitlines()[-1]
            else:
                full_err = f"<code>No traceback available.</code>"
                min_err = f"<code>UnknownError: {html.escape(str(record.getMessage()))}</code>"
            source = f"🎯 <b>Source: <code>&lt;external {html.escape(str(record.pathname))}&gt;:{html.escape(str(record.lineno))}</code> in <code>{html.escape(str(record.funcName))}</code></b>"
            formatted_message = (
                f"{source}\n"
                f"❓ <b>Error:</b> {min_err}\n"
                f"💭 <b>Message:</b> <code>{html.escape(str(record.msg))}</code>\n\n"
                f"🪐 <b>Full traceback:</b>\n"
                f"{str(full_err)}"
            )
        
        a = requests.post(
            f"https://api.telegram.org/bot{config['token']}/sendMessage",
            json={
                "chat_id": config['debug_chat'],
                "text": formatted_message,
                "parse_mode": "HTML"
            }
        )
        if not a.json()['ok']:
            print(a.json())


"""def init_logger():
    formatter = logging.Formatter(
        fmt="[%(asctime)s] [%(levelname)s] [%(name)s.%(funcName)s:%(lineno)d]\n>>> %(message)s\n",
        datefmt="%Y-%m-%d %H:%M:%S",
        style="%"
    )
    rotating_handler = logging.handlers.RotatingFileHandler(
        filename="logs.log", mode="w+", encoding="utf-8"
    )
    rotating_handler.setFormatter(formatter)
    tg_handler = TelegramErrorHandler()
    tg_handler.setLevel(logging.ERROR)
    logging.getLogger().addHandler(TelegramErrorHandler())
    logging.getLogger().addHandler(rotating_handler)

    for logger_name in logging.root.manager.loggerDict:
        logger = logging.getLogger(logger_name)
        if not logger.handlers:
            logger.setLevel(logging.INFO)
            logger.addHandler(TelegramErrorHandler())
            logger.addHandler(rotating_handler)"""