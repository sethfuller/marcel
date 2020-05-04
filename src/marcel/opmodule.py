import importlib
import inspect

import marcel.op


class OpModule:

    def __init__(self, op_name, env):
        self._op_name = op_name
        self._env = env
        self._api = None  # For creating op instances from the api
        self._constructor = None
        self._arg_parser = None
        self._arg_parser_function = None
        op_module = importlib.import_module(f'marcel.op.{op_name}')
        # Locate items in module needed during the lifecycle of an op.
        for k, v in op_module.__dict__.items():
            if k == op_name:
                self._api = v
            else:
                isclass = inspect.isclass(v)
                if isclass:
                    parents = inspect.getmro(v)
                    if isclass and marcel.core.Op in parents:
                        # The op class, e.g. Ls
                        self._constructor = v
                    elif isclass and marcel.core.ArgParser in parents:
                        # The arg parser class, e.g. LsArgParser
                        self._arg_parser_function = v
        assert self._constructor is not None, op_name
        # arg parser not always present, e.g. for gather

    def op_name(self):
        return self._op_name

    def api_function(self):
        return self._api

    def create_op(self):
        return self._constructor()

    def arg_parser(self):
        if self._arg_parser is None:
            self._arg_parser = self._arg_parser_function(self._env)
        return self._arg_parser

    # The operator's help info is formatted when the arg parser is created. When the screen
    # size changes, this info has to be reformatted.
    def reformat_help(self):
        self._arg_parser = None


def import_op_modules(env):
    op_modules = {}
    for op_name in marcel.op.public:
        op_modules[op_name] = OpModule(op_name, env)
    env.op_modules = op_modules
    return op_modules
