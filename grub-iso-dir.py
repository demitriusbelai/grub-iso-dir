#!/usr/bin/python

# Path to directory cotaining ISO images
ISO_DIR = '/home/iso'


MOUNT_POINT = None
UUID = None
DEV = None

import os
import sys
import glob
import pipes
import subprocess

def find_device_uuid(path):
  global DEV
  dev = os.stat(path).st_dev
  block = os.path.basename(os.path.realpath(
            os.path.join('/sys/dev/block/',
              pipes.quote('%d:%s' % (os.major(dev), os.minor(dev))))))
  for uuid in glob.glob('/dev/disk/by-uuid/*'):
    if os.path.basename(os.path.realpath(uuid)) == block:
      DEV = os.path.realpath(uuid)
      return os.path.basename(uuid)

def find_mount_point(path):
  path = os.path.abspath(path)
  while not os.path.ismount(path):
    path = os.path.dirname(path)
  return path

def do_fedora(iso, cdlabel):
  print(
"""menuentry "%(cdlabel)s" --class fedora --class gnu-linux --class gnu --class os {
    set isofile="/%(isofile)s"
    search --no-floppy --fs-uuid --set=root %(uuid)s
    loopback loop $isofile
    linux (loop)/isolinux/vmlinuz root=live:CDLABEL=%(cdlabel)s iso-scan/filename=$isofile rd.live.image quiet
    initrd (loop)/isolinux/initrd.img
}
""" % {
    'cdlabel': cdlabel,
    'isofile': os.path.relpath(iso, MOUNT_POINT),
    'uuid': UUID,
  })

def do_opensuse(iso, cdlabel):
  print(
"""menuentry "%(cdlabel)s" --class fedora --class gnu-linux --class gnu --class os {
    set isofile="/%(isofile)s"
    search --no-floppy --fs-uuid --set=root %(uuid)s
    loopback loop $isofile
    linux (loop)/boot/x86_64/loader/linux root=live:CDLABEL=%(cdlabel)s iso-scan/filename=$isofile rd.live.image rd.live.overlay.persistent rd.live.overlay.cowfs=ext4 splash=silent quiet
    initrd (loop)/boot/x86_64/loader/initrd
}
""" % {
    'cdlabel': cdlabel,
    'isofile': os.path.relpath(iso, MOUNT_POINT),
    'uuid': UUID,
  })

def do_ubuntu(iso, cdlabel):
  print(
"""menuentry "%(cdlabel)s" --class fedora --class gnu-linux --class gnu --class os {
    set isofile="/%(isofile)s"
    search --no-floppy --fs-uuid --set=root %(uuid)s
    loopback loop $isofile
    linux (loop)/casper/vmlinuz boot=casper iso-scan/filename=$isofile noprompt noeject
    initrd (loop)/casper/initrd
}
""" % {
    'cdlabel': cdlabel,
    'isofile': os.path.relpath(iso, MOUNT_POINT),
    'uuid': UUID,
  })

if __name__ == '__main__':
  if not UUID:
    MOUNT_POINT = find_mount_point(ISO_DIR)
    UUID = find_device_uuid(MOUNT_POINT)

  print('Looking for Images in /%s on %s (%s)' % (os.path.relpath(ISO_DIR, MOUNT_POINT), DEV, UUID), file=sys.stderr)

  for iso in glob.glob(os.path.join(ISO_DIR, '*.iso')):
    if os.path.islink(iso):
        continue
    subproc = subprocess.Popen('blkid -o value -s LABEL %s' % pipes.quote(iso), shell=True, stdout=subprocess.PIPE)
    cdlabel = subproc.stdout.read().decode().strip()
    if 'fedora' in cdlabel.lower():
      print('Found %s - %s' % (iso, cdlabel), file=sys.stderr)
      do_fedora(iso, cdlabel)
    elif 'ubuntu' in cdlabel.lower():
      print('Found %s - %s' % (iso, cdlabel), file=sys.stderr)
      do_ubuntu(iso, cdlabel)
    elif 'opensuse' in cdlabel.lower():
      print('Found %s - %s' % (iso, cdlabel), file=sys.stderr)
      do_opensuse(iso, cdlabel)
    else:
      print('Found %s - %s - Not supported' % (iso, cdlabel), file=sys.stderr)
