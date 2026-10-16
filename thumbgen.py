#!/usr/bin/env python3
"""Generate SFTP video thumbnails for Shaheen Files (v3.21+).

Usage: python3 thumbgen.py <videos_dir> <stage_dir> <ffmpeg_path>

Walks <videos_dir>, extracts one frame per video with ffmpeg, and saves it
as <stage_dir>/<key>.jpg where key = hex(Java String.hashCode(remote_path)).

The remote path MUST match exactly what the app's SFTP browser shows
(e.g. /media/mycloud/videos/x.mp4), otherwise the app won't pick it up.

After generation, transfer the .jpg files to the phone's /sdcard/ThumbStage/
and open the app once -- it imports them automatically.
"""
import os, sys, subprocess


def jhash(s):
    """Java String.hashCode() -> Integer.toHexString(), incl. surrogate pairs."""
    h = 0
    for ch in s:
        o = ord(ch)
        if o > 0xFFFF:
            o -= 0x10000
            h = (31 * h + (0xD800 + (o >> 10))) & 0xFFFFFFFF
            h = (31 * h + (0xDC00 + (o & 0x3FF))) & 0xFFFFFFFF
        else:
            h = (31 * h + o) & 0xFFFFFFFF
    return format(h, 'x')


def main():
    if len(sys.argv) != 4:
        print('usage: python3 thumbgen.py <videos_dir> <stage_dir> <ffmpeg_path>')
        sys.exit(2)
    viddir, stage, ff = sys.argv[1], sys.argv[2], sys.argv[3]
    os.makedirs(stage, exist_ok=True)
    exts = ('.mp4', '.mkv', '.avi', '.mov', '.webm',
            '.3gp', '.ts', '.m4v', '.flv', '.wmv')
    n = skip = 0
    for root, dirs, files in os.walk(viddir):
        if 'ThumbStage' in root or '/tools' in root:
            continue
        for fn in files:
            if not fn.lower().endswith(exts):
                continue
            p = os.path.join(root, fn)
            out = os.path.join(stage, jhash(p) + '.jpg')
            if os.path.exists(out):
                skip += 1
                continue
            r = subprocess.run([ff, '-y', '-v', 'error', '-ss', '1',
                                '-i', p, '-vframes', '1', '-s', '320x320', out])
            if r.returncode == 0:
                n += 1
                if n % 25 == 0:
                    print('...', n, flush=True)
            else:
                print('FAILED:', p, flush=True)
    print('done', n, 'skipped', skip, flush=True)


main()
