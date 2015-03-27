# coding: utf-8

import contextlib
import os
import readline

from core import GLOBAL_ENV


class Completer(object):
    def complete(self, text, state):
        matches = []
        for k in GLOBAL_ENV.keys():
            if k.startswith(text):
                matches.append(k)
        try:
            return matches[state]
        except IndexError:
            return None


@contextlib.contextmanager
def completion(completer=None):
    if not completer:
        completer = Completer()

    readline.set_completer(completer.complete)
    readline.set_completer_delims('() ')

    history = os.path.expanduser("~/.zy-history")
    readline.parse_and_bind("set blink-matching-paren on")

    try:
        readline.read_history_file(history)
    except IOError:
        open(history, 'a').close()

    readline.parse_and_bind("tab: complete")
    yield
    readline.write_history_file(history)
