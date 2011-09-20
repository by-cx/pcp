def size_format(b):
    sizes_int = [1, 1024, 1024 ** 2, 1024 ** 3, 1024 ** 4, 1024 ** 5, 1024 ** 6]
    sizes_s = ["B", "kB", "MB", "GB", "TB", "PB"]
    i = 0
    for size in sizes_s:
        if b < sizes_int[i + 1]:
            return "%.2f %s" % (float(b) / float(sizes_int[i]), size)
        i += 1
    return "%.2f %s" % (float(b) / float(sizes_int[i]), size)


def sc(s, color="nc"):
    """Shell Color
     """

    colors = {
        "red": '\x1b[0;31m',
        "red2": '\x1b[1;31m',
        "blue": '\x1b[0;34m',
        "blue2": '\x1b[1;34m',
        "cyan": '\x1b[0;36m',
        "cyan2": '\x1b[1;36m',
        "nc": '\x1b[0m', # No Color
    }

    return "%s%s%s" % (colors[color], s, colors["nc"])
