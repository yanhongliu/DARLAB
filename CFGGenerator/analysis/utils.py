import analysis.source

def prompt():
    try:
        lines = []
        while 1:
            lines.append(raw_input(">>>> "))
    except EOFError:
        pass
    return analysis.source.process("\n".join(lines))

# vim: tabstop=4 expandtab shiftwidth=4
