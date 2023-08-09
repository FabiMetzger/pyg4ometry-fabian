import hashlib as _hl
import difflib as _dl


def md5_file(fname):
    hash_md5 = _hl.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def diffFiles(file1, file2):
    with open(file1) as f1, open(file2) as f2:
        diff = _dl.unified_diff(f1.readlines(), f2.readlines(), fromfile=file1, tofile=file2)

        for line in diff:
            print(line)
