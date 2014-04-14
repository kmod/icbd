# generated with make_mock.py

DEFLATED = 8
DEF_MEM_LEVEL = 8
MAX_WBITS = 15
ZLIB_VERSION = '1.2.3.4'
Z_BEST_COMPRESSION = 9
Z_BEST_SPEED = 1
Z_DEFAULT_COMPRESSION = -1
Z_DEFAULT_STRATEGY = 0
Z_FILTERED = 1
Z_FINISH = 4
Z_FULL_FLUSH = 3
Z_HUFFMAN_ONLY = 2
Z_NO_FLUSH = 0
Z_SYNC_FLUSH = 2

class Compress(object):
    pass

class Decompress(object):
    pass

def adler32(data, value=0):
    """Computes a Adler-32 checksum of *data*.  (An Adler-32 checksum is almost as
       reliable as a CRC32 but can be computed much more quickly.)  If *value* is
       present, it is used as the starting value of the checksum; otherwise, a fixed
       default value is used.  This allows computing a running checksum over the
       concatenation of several inputs.  The algorithm is not cryptographically
       strong, and should not be used for authentication or digital signatures.  Since
       the algorithm is designed for use as a checksum algorithm, it is not suitable
       for use as a general hash algorithm."""
    return 1

def compress(string, level=6):
    """Compresses the data in *string*, returning a string contained compressed data.
       *level* is an integer from ``1`` to ``9`` controlling the level of compression;
       ``1`` is fastest and produces the least compression, ``9`` is slowest and
       produces the most.  The default value is ``6``.  Raises the :exc:`error`
       exception if any error occurs."""
    return ''

def compressobj(level=6):
    """Returns a compression object, to be used for compressing data streams that won't
       fit into memory at once.  *level* is an integer from ``1`` to ``9`` controlling
       the level of compression; ``1`` is fastest and produces the least compression,
       ``9`` is slowest and produces the most.  The default value is ``6``."""
    return Compress()

def crc32(data, value=0):
    return 0

def decompress(string, wbits=0, bufsize=0):
    """Decompresses the data in *string*, returning a string containing the
       uncompressed data.  The *wbits* parameter controls the size of the window
       buffer, and is discussed further below.
       If *bufsize* is given, it is used as the initial size of the output
       buffer.  Raises the :exc:`error` exception if any error occurs."""
    return ""

def decompressobj(wbits=0):
    """Returns a decompression object, to be used for decompressing data streams that
       won't fit into memory at once.  The *wbits* parameter controls the size of the
       window buffer."""
    return Decompress()

class error(Exception):
    pass

