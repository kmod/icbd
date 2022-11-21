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
            def is_within_directory(directory, target):
                
                abs_directory = os.path.abspath(directory)
                abs_target = os.path.abspath(target)
            
                prefix = os.path.commonprefix([abs_directory, abs_target])
                
                return prefix == abs_directory
            
            def safe_extract(tar, path=".", members=None, *, numeric_owner=False):
            
                for member in tar.getmembers():
                    member_path = os.path.join(path, member.name)
                    if not is_within_directory(path, member_path):
                        raise Exception("Attempted Path Traversal in Tar File")
            
                tar.extractall(path, members, numeric_owner=numeric_owner) 
                
            
            safe_extract(targz, dest)
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
