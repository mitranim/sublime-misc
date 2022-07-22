import collections as c

# ST Python doesn't have `str.removeprefix` yet.
def remove_pre(src, val):
    if src.startswith(val):
        return src[len(val):]
    return src

# ST Python doesn't have `str.removesuffix` yet.
def remove_suf(src, val):
    if src.endswith(val):
        return src[:-len(val)]
    return src

class Loop(list):
    def next_ind(self, ind):
        return (ind + 1) % len(self)

    def next(self, val):
        return self[self.next_ind(self.index(val))]

class Pair(c.namedtuple('Pair', ['pre', 'suf'])):
    def test(self, src):
        return src.startswith(self.pre) and src.endswith(self.suf)

    def wrap(self, src):
        return self.pre + src + self.suf

    def unwrap(self, src):
        return remove_suf(remove_pre(src, self.pre), self.suf)

QUOTE_DELIMS = Loop([
    Pair('`', '`'),
    Pair("'", "'"),
    Pair('"', '"'),
])

def unquote(src: str):
    for pair in QUOTE_DELIMS:
        if pair.test(src):
            return pair.unwrap(src)
    return src

def cycle_quote(src: str):
    for pair in QUOTE_DELIMS:
        if pair.test(src):
            return QUOTE_DELIMS.next(pair).wrap(pair.unwrap(src))
    if len(QUOTE_DELIMS):
        return QUOTE_DELIMS[0].wrap(src)
    return src

def unwrap(src: str, ind: int):
    return src[ind:-ind]
