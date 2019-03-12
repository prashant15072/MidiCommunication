import pickle

def parse_cfg(cfgfile):
    file = open(cfgfile, 'r')
    lines = file.read().split('\n')  # store the lines in a list
    lines = [x for x in lines if len(x) > 0]  # get read of the empty lines
    lines = [x for x in lines if x[0] != '#']
    lines = [x.rstrip().lstrip() for x in lines]

    block = {}

    for line in lines:
        key, value = line.split("=")
        block[key.rstrip()] = value.lstrip()

    # print block
    return block


def picklestoreData(fileName,data):

    dbfile = open(fileName, 'wb')

    # source, destination
    pickle.dump(data, dbfile)
    dbfile.close()


def pickleloadData(fileName):

    dbfile = open(fileName, 'rb')
    db = pickle.load(dbfile)
    return db