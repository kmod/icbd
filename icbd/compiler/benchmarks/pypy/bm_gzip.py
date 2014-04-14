import os
import time
import shutil
import tempfile
import tarfile

DJANGO_DIR = os.path.join(os.path.dirname(__file__), os.pardir,
                          'unladen_swallow', 'lib', 'django')

def _bootstrap():
    fd, archive = tempfile.mkstemp()
    os.close(fd)
    with tarfile.open(archive, 'w:gz') as targz:
        targz.add(DJANGO_DIR)
    return archive

def bench(archive):
    dest = tempfile.mkdtemp()
    try:
        with tarfile.open(archive) as targz:
            targz.extractall(dest)
    finally:
        shutil.rmtree(dest)

def main(n):
    archive = _bootstrap()
    try:
        times = []
        for k in range(n):
            t0 = time.time()
            bench(archive)
            times.append(time.time() - t0)
        return times
    finally:
        os.remove(archive)

if __name__ == '__main__':
    import util, optparse
    parser = optparse.OptionParser(
        usage="%prog [options]",
        description="Test the performance of the GZip decompression benchmark")
    util.add_standard_options_to(parser)
    options, args = parser.parse_args()

    util.run_benchmark(options, options.num_runs, main)
