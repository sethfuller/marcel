"""C{rm [FILENAME ...]}

FILENAME                   Filename or glob pattern.

Files (including directories) are removed. They can be specified in one of two ways:

1) Specify one or more FILENAMEs, (or glob patterns).

2) Specify no FILENAMEs, in which case the files to be removed are piped in from the preceding
command in the pipeline. Each incoming objects must be a 1-tuple containing a C{File}.

E.g. to remove all the .pyc files in the current directory:

    C{rm *.pyc}

or

    C{ls *.pyc | rm}
"""

import shutil

import marcel.core
import marcel.env
import marcel.object.error
import marcel.object.file
import marcel.op.filenames


def rm():
    return Rm()


class RmArgParser(marcel.core.ArgParser):

    def __init__(self):
        super().__init__('rm')
        self.add_argument('filename', nargs='*')


class Rm(marcel.core.Op):

    argparser = RmArgParser()

    def __init__(self):
        super().__init__()
        self.filename = None

    def __repr__(self):
        return 'rm({})'.format(self.filename)

    # BaseOp

    def doc(self):
        return __doc__

    def setup_1(self):
        pass

    def receive(self, x):
        if len(self.filename) > 0:
            # Remove specified files
            paths = marcel.op.filenames.normalize_paths(self.filename)
            roots = marcel.op.filenames.roots(marcel.env.ENV.pwd(), paths)
            for root in roots:
                self.remove(root)
        else:
            # Remove files passed in.
            if len(x) != 1 or not isinstance(x[0], marcel.object.file.File):
                raise marcel.exception.KillAndResumeException('rm input must be a 1-tuple containing a File')
            self.remove(x[0])

    # Op

    def arg_parser(self):
        return Rm.argparser

    def must_be_first_in_pipeline(self):
        return len(self.filename) > 0

    # For use by this class

    def remove(self, root):
        try:
            if root.is_dir():
                shutil.rmtree(root)
            else:  # This works for files and symlinks
                root.unlink()
        except PermissionError as e:
            self.send(marcel.object.error.Error(e))
        except FileNotFoundError:
            pass
