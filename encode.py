import sys
fname = sys.argv[1]
with open(fname, 'rb') as fin:
    siz = 64
    data = fin.read(siz)
    while data != b"":
        print("echo -ne '"+("".join("\\x%02x" % i for i in data))+("'>>%s"%fname))
        # read next
        data = fin.read(siz)
