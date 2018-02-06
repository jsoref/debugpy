import json

from . import MESSAGE_TYPES, MESSAGE_TYPE_KEYS


def read(stream):
    """Return an instance based on the given bytes."""
    headers = {}
    for line in stream:
        if line == b'\r\n':
            break
        assert(line.endswith(b'\r\n'))
        line = line[:-2].decode('ascii')
        try:
            name, value = line.split(': ', 1)
        except ValueError:
            raise RuntimeError('invalid header line: {}'.format(line))
        headers[name] = value

    size = int(headers['Content-Length'])
    body = stream.read(size)

    data = json.loads(body.decode('utf-8'))

    msgtype = data['type']
    typekey = MESSAGE_TYPE_KEYS[msgtype]
    key = data[typekey]
    cls = MESSAGE_TYPES[msgtype][key]

    return cls.from_data(**data)


def as_bytes(msg):
    """Return the raw bytes for the message."""
    headers, body = _as_http_data(msg)
    headers = '\r\n'.join('{}: {}'.format(name, value)
                          for name, value in headers.items())
    return headers.encode('ascii') + b'\r\n\r\n' + body.encode('utf-8')


def _as_http_data(msg):
    payload = msg.as_data()
    body = json.dumps(payload)

    headers = {
        'Content-Length': len(body),
        'Content-Type': 'application/json',
    }
    return headers, body
