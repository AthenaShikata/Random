import struct
import os
import shutil
import hashlib

BACKUP_DIR = os.path.dirname(os.path.abspath(__file__))
OUTPUT_DIR = r'E:\temp\backup_extracted'


def read_mbdb_string(f):
    raw = f.read(2)
    if len(raw) < 2:
        return None
    length = struct.unpack('>H', raw)[0]
    if length == 0xFFFF:
        return ''
    data = f.read(length)
    if len(data) < length:
        return None
    try:
        return data.decode('utf-8', errors='replace')
    except Exception:
        return ''


def read_mbdb_bytes(f):
    raw = f.read(2)
    if len(raw) < 2:
        return None
    length = struct.unpack('>H', raw)[0]
    if length == 0xFFFF:
        return b''
    return f.read(length)


def parse_mbdb(mbdb_path):
    entries = []
    with open(mbdb_path, 'rb') as f:
        magic = f.read(4)
        if magic != b'mbdb':
            raise ValueError(f"Not a valid mbdb file (got magic: {magic!r})")
        f.read(2)  # version bytes

        while True:
            try:
                domain = read_mbdb_string(f)
                if domain is None:
                    break
                path = read_mbdb_string(f)
                if path is None:
                    break
                _linktarget = read_mbdb_string(f)
                _datahash   = read_mbdb_bytes(f)
                _unknown    = read_mbdb_bytes(f)

                mode      = struct.unpack('>H', f.read(2))[0]
                _inode    = struct.unpack('>Q', f.read(8))[0]
                _uid      = struct.unpack('>I', f.read(4))[0]
                _gid      = struct.unpack('>I', f.read(4))[0]
                _mtime    = struct.unpack('>I', f.read(4))[0]
                _atime    = struct.unpack('>I', f.read(4))[0]
                _ctime    = struct.unpack('>I', f.read(4))[0]
                filesize  = struct.unpack('>Q', f.read(8))[0]
                _protect  = struct.unpack('B',  f.read(1))[0]
                numprops  = struct.unpack('B',  f.read(1))[0]

                for _ in range(numprops):
                    read_mbdb_string(f)
                    read_mbdb_bytes(f)

                file_hash = hashlib.sha1(
                    f"{domain}-{path}".encode('utf-8')
                ).hexdigest()

                is_file = (mode & 0xE000) == 0x8000

                entries.append({
                    'domain':   domain,
                    'path':     path,
                    'filesize': filesize,
                    'is_file':  is_file,
                    'hash':     file_hash,
                })

            except struct.error:
                break

    return entries


def sanitize(name):
    """Replace characters that are illegal in Windows filenames."""
    for ch in r'\:*?"<>|':
        name = name.replace(ch, '_')
    return name


def main():
    mbdb_path = os.path.join(BACKUP_DIR, 'Manifest.mbdb')

    if not os.path.exists(mbdb_path):
        print(f"ERROR: Manifest.mbdb not found in {BACKUP_DIR}")
        print("Make sure this script is in the same folder as Manifest.mbdb")
        input("\nPress Enter to exit...")
        return

    print(f"Parsing Manifest.mbdb in: {BACKUP_DIR}")
    print(f"Output directory:         {OUTPUT_DIR}\n")

    try:
        entries = parse_mbdb(mbdb_path)
    except ValueError as e:
        print(f"ERROR: {e}")
        input("\nPress Enter to exit...")
        return

    total   = len(entries)
    files   = [e for e in entries if e['is_file']]
    print(f"Total entries:  {total}")
    print(f"Files to copy:  {len(files)}")
    print(f"Directories:    {total - len(files)}\n")

    os.makedirs(OUTPUT_DIR, exist_ok=True)

    copied  = 0
    missing = 0
    errors  = 0

    for i, entry in enumerate(files, 1):
        src = os.path.join(BACKUP_DIR, entry['hash'])

        # Output path: OUTPUT_DIR / domain / file_path
        # Each part is sanitized for Windows compatibility
        domain_safe = sanitize(entry['domain'])
        path_parts  = [sanitize(p) for p in entry['path'].replace('/', os.sep).split(os.sep)]
        dst = os.path.join(OUTPUT_DIR, domain_safe, *path_parts)

        # Progress every 100 files
        if i % 100 == 0 or i == len(files):
            print(f"  [{i}/{len(files)}] {entry['domain']}/{entry['path'][:60]}")

        if not os.path.exists(src):
            missing += 1
            continue

        try:
            os.makedirs(os.path.dirname(dst), exist_ok=True)
            shutil.copy2(src, dst)
            copied += 1
        except Exception as e:
            print(f"  [ERROR] {entry['path']} — {e}")
            errors += 1

    print(f"\n{'='*50}")
    print(f"Done.")
    print(f"  Copied:  {copied} files")
    if missing:
        print(f"  Missing: {missing} files (not present in backup)")
    if errors:
        print(f"  Errors:  {errors} files")
    print(f"\nExtracted to: {OUTPUT_DIR}")
    print(f"\nFolder structure:")
    print(f"  {OUTPUT_DIR}\\")
    print(f"    [AppDomain-com.mojang.minecraftpe]\\  ← Minecraft")
    print(f"    [AppDomain-...]\\                     ← Other apps")
    print(f"    [CameraRollDomain]\\                  ← Photos")
    print(f"    [MediaDomain]\\                       ← Music, ringtones")
    print(f"    [HomeDomain]\\                        ← Settings, preferences")
    input("\nPress Enter to exit...")


if __name__ == '__main__':
    main()
