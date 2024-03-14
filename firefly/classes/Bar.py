def bar(percent, digits = 10):
    bar = ''
    for i in range(digits):
        if (i * 10 <= percent):
            bar += '#'
        else:
            bar += '-'
    return "[" +bar + "] "+"% 3s" % str(round(percent))+"%"