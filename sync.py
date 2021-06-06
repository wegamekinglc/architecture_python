import hashlib
import os
import shutil
from pathlib import Path


BLOCK_SIZE = 65536


def hash_file(path):
    hash_func = hashlib.sha1()
    with path.open("rb") as file:
        buf = file.read(BLOCK_SIZE)
        while buf:
            hash_func.update(buf)
            buf = file.read(BLOCK_SIZE)
    return hash_func.hexdigest()


def read_paths_and_hashes(root):
    hashes = {}
    for folder, _, files in os.walk(root):
        for fn in files:
            hashes[hash_file(Path(folder) / fn)] = fn
    return hashes


def determine_actions(source_hashes, dest_hashes, source_folder, dest_folder):
    for sha, file_name in source_hashes.items():
        if sha not in dest_hashes:
            source_path = Path(source_folder) / file_name
            dest_path = Path(dest_folder) / file_name
            yield "COPY", source_path, dest_path
        elif dest_hashes[sha] != file_name:
            old_dest_path = Path(dest_folder) / dest_hashes[sha]
            new_dest_path = Path(dest_folder) / file_name
            yield "MOVE", old_dest_path, new_dest_path

    for sha, file_name in dest_hashes.items():
        if sha not in source_hashes:
            yield "DELETE", dest_folder / file_name


def sync(source, dest):
    source_hashes = read_paths_and_hashes(source)
    dest_hashes = read_paths_and_hashes(dest)

    actions = determine_actions(source_hashes,
                                dest_hashes,
                                source,
                                dest)

    for action, *paths in actions:
        if action == "COPY":
            shutil.copy(*paths)
        elif action == "MOVE":
            shutil.move(*paths)
        elif action == "DELETE":
            os.remove(paths[0])
