from __future__ import print_function

import code
import platform
import sys

from core import parse, zy_eval, to_zy_str
from completer import completion


class CommandRunner(object):
    def run(self, command):
        if command.strip():
            val = zy_eval(parse(command.replace('\n', ' ')))
            if val:
                print(to_zy_str(val))


class ZyREPL(code.InteractiveConsole):
    def __init__(self, runner, locals=None, filename="<input>"):
        self.runner = runner
        code.InteractiveConsole.__init__(self, locals=locals, filename=filename)

    def runsource(self, source, filename='<input>', symbol=None):
        try:
            if source.count('(') == source.count(')'):
                self.runner.run(source)
            else:
                return True
        except SystemExit:
            raise
        except:
            self.showtraceback()
        return False


def run_repl(zy_repl):
    sys.ps1 = "=> "
    sys.ps2 = "... "
    with completion():
        zy_repl.interact(
            "{appname} {version} using {py}({build}) {pyversion} on {os}".format(
                appname='Zy',
                build=platform.python_build()[0],
                os=platform.system(),
                py=platform.python_implementation(),
                pyversion=platform.python_version(),
                version='0.0.2',
            )
        )


def main(args=None):
    runner = CommandRunner()

    if len(args) == 1:
        run_repl(ZyREPL(runner))
    else:
        import codecs
        with codecs.open(args[1], 'r', 'utf-8') as f:
            source = ''
            for line in f.xreadlines():
                source += line
                if source.count('(') == source.count(')'):
                    runner.run(source)
                    source = ''
    return 0


if __name__ == '__main__':
    sys.exit(main(sys.argv))
