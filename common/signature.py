import os
import hashlib

def md5_hash(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def hash_directory(path, ignore_dirs=[], extensions=[]):
    digest = hashlib.sha1()
    for root, dirs, files in os.walk(path):
        if os.path.basename(root) in ignore_dirs:
            continue
        for names in files:
            if len(extensions) > 0 and os.path.splitext(names)[1] not in extensions:
                continue
            file_path = os.path.join(root, names)
            # Hash the path and add to the digest to account for empty files/directories
            digest.update(hashlib.sha1(file_path[len(path):].encode()).digest())
            # Per @pt12lol - if the goal is uniqueness over repeatability, this is an alternative method using 'hash'
            # digest.update(str(hash(file_path[len(path):])).encode())
            if os.path.isfile(file_path):
                with open(file_path, 'rb') as f_obj:
                    while True:
                        buf = f_obj.read(1024 * 1024)
                        if not buf:
                            break
                        digest.update(buf)
    return digest.hexdigest()
