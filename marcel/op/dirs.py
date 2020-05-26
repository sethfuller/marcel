# This file is part of Marcel.
# 
# Marcel is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation, either version 3 of the License, or at your
# option) any later version.
# 
# Marcel is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
# for more details.
# 
# You should have received a copy of the GNU General Public License
# along with Marcel.  If not, see <https://www.gnu.org/licenses/>.

import marcel.argsparser
import marcel.core


SUMMARY = '''
Write the entries in the directory stack to the output stream, top first.
'''


DETAILS = None


def dirs(env):
    return Dirs(env)


class DirsArgsParser(marcel.argsparser.ArgsParser):

    def __init__(self, env):
        super().__init__('dirs', env)
        self.add_flag_no_value('clear', '-c', '--clear')
        self.validate()


class Dirs(marcel.core.Op):

    def __init__(self, env):
        super().__init__(env)
        self.clear = None

    def __repr__(self):
        return f'dirs(clear={self.clear})'

    # BaseOp

    def receive(self, _):
        if self.clear:
            self.env().dir_state().reset_dir_stack()
        for dir in self.env().dir_state().dirs():
            self.send(dir)

    # Op

    def must_be_first_in_pipeline(self):
        return True

    def run_in_main_process(self):
        return True
