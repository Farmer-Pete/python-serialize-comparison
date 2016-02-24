#!/usr/bin/env python3
import io
import timeit
from collections import defaultdict
from typing import List

REPEATS = 10 
MIN_LENGTH = 10**5 # Hundred Thousand
MAX_LENGTH = 10**6 # One Million
STEPS = 10

class Test():

    def __init__(self): pass

    def serialize(self, data: List[int]) -> str:
        return self.module.dumps(data)

    def deserialize(self, data: str) -> List[int]:
        return self.module.loads(data)

    def getDeserializeInput(self, data: List[int]) -> str:
        return self.serialize(data)

    def initialize(self, dataLen: int) -> None:
        return

class Join(Test):
    def serialize(self, data: List[int]) -> str:
        return ','.join(repr(x) for x in data)

    def deserialize(self, data: str):
        return [int(x) for x in data.split(',')]

class CSV(Test):
    def serialize(self, data: List[int], f: io.StringIO) -> None:
        # Technically, I could move the reader/writer creation
        # out of these methods into the constructor. However,
        # the instantiation of the csv objects should have a
        # negligible impact on performance
        import csv
        f.seek(0)
        writer = csv.writer(f)
        writer.writerow(data)

    def deserialize(self, data: io.StringIO) -> List[int]:
        import csv
        data.seek(0)
        reader = csv.reader(data)
        return next(reader)

    def getDeserializeInput(self, data: List[int]) -> io.StringIO:
        f = io.StringIO()
        self.serialize(data, f)
        f.seek(0)
        return f

class Struct(Test):
    def __init__(self, dataLen: int):
        from struct import Struct
        self.module = Struct('l'*dataLen)

    def serialize(self, data: List[int]) -> str:
        return self.module.pack(*data)

    def deserialize(self, data: str) -> List[int]:
        return self.module.unpack(data)

    def getDeserializeInput(self, data: List[int]) -> str:
        return self.serialize(data)

class Pickle(Test):
    import pickle
    module = pickle

class Marshal(Test):
    import marshal
    module = marshal

class JSON(Test):
    import json
    module = json

class uJSON(Test):
    import ujson
    module = ujson

class BSON(Test):
    def serialize(self, data: List[int]) -> str:
        import bson
        return bson.dumps({'data':data})

    def deserialize(self, data: str) -> List[int]:
        import bson
        return bson.loads(data)['data']

class MsgPack(Test):
    import msgpack
    module = msgpack

def timer(method, **kwargs):
    def wrapper():
        method(**kwargs)
    return timeit.Timer(
            'method(**kwargs)',
            globals={'method':method, 'kwargs':kwargs}
        ).timeit(REPEATS) / REPEATS

def profile(data, cls):
    kwargs_serialize = {'data': data }
    kwargs_deserialize = {}

    if cls.__init__.__annotations__.get('dataLen') == int:
        obj = cls(dataLen=len(data))
    else:
        obj = cls()

    f = None

    if obj.serialize.__annotations__.get('f') == io.StringIO:
        kwargs_serialize['f'] = f = io.StringIO()

    serializedOutput = kwargs_deserialize['data'] = obj.getDeserializeInput(data)

    return (
        timer(obj.serialize, **kwargs_serialize),
        timer(obj.deserialize, **kwargs_deserialize),
        len(f.getvalue() if f else serializedOutput)
    )

def export(*args, data):
    print()
    print('[ %s ]' % ' '.join(args))
    print(
        JSON().serialize({
            cls.__name__: {
                'label': cls.__name__,
                'data': list(data[cls])
            } for cls in data
        })
    )

TESTS = [
    BSON,
    CSV,
    Join,
    JSON,
    Marshal,
    MsgPack,
    Pickle,
    Struct,
    uJSON
]

def main():
    results = {
        'times': {
            'serialize': defaultdict(list),
            'deserialize': defaultdict(list)
        },
        'sizes': defaultdict(list)
    }
    lengths = list(
        range(
            MIN_LENGTH,
            MAX_LENGTH+1,
            MAX_LENGTH//STEPS
        )
    )
    for i, length in enumerate(lengths, 1):
        data = list(range(length))
        for cls in TESTS:
            print(
                '[%s/%s] Testing %s @ %s ...' % (
                    i,
                    len(lengths),
                    cls.__name__,
                    '{:,}'.format(length)
                ),
                end='',
                flush=True
            )
            serializeTime, deserializeTime, dataSize = profile(data, cls)
            results['times']['serialize'][cls].append(serializeTime)
            results['times']['deserialize'][cls].append(deserializeTime)
            results['sizes'][cls].append(dataSize)
            print(' Done')

    for key in ('serialize', 'deserialize'):
        export(
            key, 'time',
            data = {
                cls: zip(lengths, results['times'][key][cls])
                for cls in TESTS
            }
        )

    export(
        'data size',
        data = {
            cls: zip(lengths, results['sizes'][cls])
            for cls in TESTS
        }
    )

if __name__ == '__main__':
    main()
