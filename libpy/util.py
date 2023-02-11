import os

################################
# Utilities
################################

class Reader:
    def __init__(self, str):
        self.str = str
        self.idx = 0

    def current(self):
        if self.idx < 0 or self.idx >= len(self.str):
            return None
        return self.str[self.idx]

    def next(self, amt = 1):
        self.idx += amt
        if self.idx < 0 or self.idx >= len(self.str):
            return None
        return self.str[self.idx]

    def prev(self, amt = 1):
        self.idx -= amt
        if self.idx < 0 or self.idx >= len(self.str):
            return None
        return self.str[self.idx]

    def peek(self, off):
        idx = self.idx + off
        if idx >= len(self.str) or idx < 0:
            return None
        return self.str[idx]

    def at(self, index):
        if index > 0:
            return self.str[index]
        else:
            idx = self.idx - abs(index)
            if idx >= len(self.str) or idx < 0:
                return None
            return self.str[idx]

    def collect(self, pred: function):
        str = ""
        while self.current() != None and pred(self.current()):
            str += self.current()
        return str

    def pcollect(self, pred: function):
        while self.current() != None and pred(self.current()):
            pass
        return str

def is_path_sep(char):
    return char == '\\' or char == '/'

def fix_path(pstr):
    seg      = ""
    segments = []
    reader = Reader(pstr)
    char   = reader.current()
    while char != None:
        # check for separator
        if is_path_sep(char):
            if len(seg) > 2 and seg[0] == '%':
                seg = os.getenv(seg[1:-1])
            segments.append(seg)
            seg = ""
        else:
            seg += char

        char = reader.next()

    # stitch to string
    result = ""
    for segment in segments:
        result += segment + "/"
    return result

# get index by position/offset
# into a list of length len
def get_idx_by_pos(len, pos):
    if pos < 0:
        return len + pos
    else:
        return pos