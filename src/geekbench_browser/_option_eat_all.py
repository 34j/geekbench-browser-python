from typing import Any

import click
from click import Context, OptionParser
from click.parser import ParsingState


class OptionEatAll(click.Option):
    def __init__(self, *args: Any, **kwargs: Any):
        self.save_other_options = kwargs.pop("save_other_options", True)
        nargs = kwargs.pop("nargs", -1)
        if nargs != -1:
            raise ValueError(f"nargs, if set, must be -1 not {nargs}")
        super().__init__(*args, **kwargs)

    def add_to_parser(self, parser: OptionParser, ctx: Context) -> None:
        def parser_process(value: str, state: ParsingState) -> None:
            # method to hook to the parser.process
            done = False
            values = [value]
            if self.save_other_options:
                # grab everything up to the next option
                while state.rargs and not done:
                    for prefix in self._eat_all_parser.prefixes:
                        if state.rargs[0].startswith(prefix):
                            done = True
                    if not done:
                        values.append(state.rargs.pop(0))
            else:
                # grab everything remaining
                values += state.rargs
                state.rargs[:] = []

            # call the actual process
            self._previous_parser_process(tuple(values), state)

        retval = super().add_to_parser(parser, ctx)
        for name in self.opts:
            our_parser = parser._long_opt.get(name) or parser._short_opt.get(name)
            if our_parser:
                self._eat_all_parser = our_parser
                self._previous_parser_process = our_parser.process
                our_parser.process = parser_process
                break
        return retval
