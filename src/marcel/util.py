import collections.abc
import grp
import io
import pathlib
import pickle
import pwd
import shutil
import sys
import time
import traceback


def username(uid):
    try:
        return pwd.getpwuid(uid).pw_name
    except KeyError:
        return str(uid)


def groupname(gid):
    try:
        return grp.getgrgid(gid).gr_name
    except KeyError:
        return str(gid)


def is_sequence(x):
    return isinstance(x, collections.abc.Sequence)


def is_sequence_except_string(x):
    return isinstance(x, collections.abc.Sequence) and not isinstance(x, str)


def is_generator(x):
    return isinstance(x, collections.abc.Generator)


def is_file(x):
    # Why not isinstance: Importing osh.file results in circular imports
    return x.__class__.__name__ == 'File'


def is_executable(x):
    return shutil.which(x) is not None


def normalize_output(x):
    return tuple(x) if is_sequence_except_string(x) else (x,)


def normalize_path(x):
    x = pathlib.Path(x)
    if x.as_posix().startswith('~'):
        x = x.expanduser()
    return x



def clone(x):
    try:
        buffer = io.BytesIO()
        pickler = pickle.Pickler(buffer)
        pickler.dump(x)
        buffer.seek(0)
        unpickler = pickle.Unpickler(buffer)
        copy = unpickler.load()
        return copy
    except Exception as e:
        print('Cloning error: ({}) {}'.format(type(e), e), file=sys.__stderr__)
        print_stack()


def print_stack(file=None):
    if file is None:
        file = sys.__stderr__
    exception_type, exception, trace = sys.exc_info()
    print('Caught {}: {}'.format(exception_type, exception), file=file)
    traceback.print_tb(trace, file=file)


def colorize(s, color):
    # Those /001 and /002 codes seem to fix bug 2.
    # https://stackoverflow.com/questions/9468435/how-to-fix-column-calculation-in-python-readline-if-using-color-prompt
    return (s
            if color is None else
            '\001\033[{}m\002\001\033[38;5;{}m\002{}\001\033[0m\002'.format(
                1 if color.bold else 0,
                color.code,
                s))


class Stack:

    def __init__(self):
        self.contents = []

    def push(self, x):
        self.contents.append(x)

    def top(self):
        return self.contents[-1]

    def pop(self):
        top = self.top()
        self.contents = self.contents[:-1]
        return top

    def is_empty(self):
        return len(self.contents) == 0


class Trace:

    def __init__(self, tracefile):
        self.path = pathlib.Path(tracefile)
        self.path.touch(mode=0o666, exist_ok=True)
        self.path.unlink()
        self.file = self.path.open(mode='w')

    def write(self, line):
        print('{}: {}'.format(time.time(), line), file=self.file, flush=True)

    def close(self):
        self.file.close()