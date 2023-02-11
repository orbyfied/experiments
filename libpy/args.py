from util import *

################################
# CLI
################################

# the pos value to signal the argument
# should be appended to the end
POS_APPEND_BACK = 0xFFFFFFFF

class ArgError(RuntimeError):
    def __init__(self, *args: object) -> None:
        super().__init__(*args)

# simple arg repr
class Arg:
    # create a simple named arg
    def new(name: str, char: str, ty: type):
        return Arg(name, char, ty, None, None)
    # create a simple positional arg
    def new_positional(name: str, ty: type):
        return Arg(name, None, ty, None, POS_APPEND_BACK)
    # create a positional arg at the specified idx/pos
    def new_positional_at(name: str, ty: type, pos: int):
        return Arg(name, None, ty, None, pos)
    # create a switch arg
    def new_switch(name: str, char: str, ty: type, switch_handler: function):
        return Arg(name, char, ty, switch_handler, None)

    def __init__(self, name: str, char: str, ty: type, sw_handler: function, pos: int):
        self.name       = name
        self.char       = char
        self.ty         = ty
        self.sw_handler = sw_handler
        self.pos        = pos

# a parser for a type
class ArgParser: pass
class TypeParser:
    def __init__(self, ty: type, pfunc: function):
        self.ty = ty
        self.pfunc = pfunc

    # abstract: parses the type
    def parse(self, parser: ArgParser, arg: Arg, reader: Reader):
        return self.pfunc(parser, arg, reader)

# arg parser
class ArgParser:
    def __init__(self):
        self.arg_map  = { } # args by name
        self.pos_args = [ ] # positioned list of args
        self.by_char  = { } # args by char
        self.types    = { } # type parsers

    def define_type(self, ty: TypeParser):
        self.types[ty.ty] = ty

    def add(self, arg: Arg):
        self.arg_map[arg.name] = arg
        if arg.char != None:
            self.by_char[arg.char] = arg
        if arg.pos != None:
            if arg.pos == POS_APPEND_BACK:
                self.pos_args.append(arg)
            else:
                self.pos_args.insert(get_idx_by_pos(len(self.pos_args), arg.pos), arg)

    def parse_val(self, arg: Arg, reader: Reader):
        try:
            return arg.ty.parse(self, arg, reader)
        except ArgError as e:
            print("arg: error occured parsing " + arg.name + ": " + e)
            raise ArgError("arg parse failed")

    def parse(self, str: str, out: dict):
        if not out:
            out = { }

        pIdx = 0 # positional arg index
        reader = Reader(str) # string reader
        c = None # char

        while reader.current() != None:
            # collect whitespace
            reader.pcollect(lambda c : c.isspace())

            c = reader.current()

            # check for flags
            if c == '-':
                # check for named
                if reader.next() == '-':
                    # collect name
                    reader.next()
                    name = reader.collect(lambda c : c != ' ' and c != '=')

                    arg = self.arg_map[name]
                    if not arg:
                        raise ArgError("unknown arg by name " + name)

                    # check for explicit value
                    # or spaced value
                    # otherwise handle switch
                    val = None
                    if not arg.sw_handler or reader.current() == '=':
                        reader.next()
                        val = self.parse_val(arg, reader)
                    else: # switch
                        val = arg.sw_handler(self, arg)

                    # put val
                    out[arg.name] = val
                else:
                    while reader.current() != None and reader.current() != ' ':
                        arg = self.arg_map[reader.current()]
                        if not arg:
                            raise ArgError("unknown arg by char '" + reader.current() + "'")

                        # check switch
                        if not arg.sw_handler:
                            reader.next()
                            val = self.parse_val(arg, reader)
                            out[arg.name] = val
                            break
                        else:
                            out[arg.name] = arg.sw_handler(self, arg)
                            reader.next()
            else:
                # handle positional arg
                arg = self.pos_args[pIdx]
                pIdx += 1
                val = self.parse_val(arg, reader)
                out[arg.name] = val

        return out