# GRUB-ISO-DIR

This is a simple script to `/etc/grub.d/` for read a directory containing bootable Linux ISO images and put them in menu entry.

## Install

```
sudo wget https://github.com/demitriusbelai/grub-iso-dir/raw/master/grub-iso-dir.py -O /etc/grub.d/40_isodir.py
```

## Configuration

Edit ```/etc/grub.d/40isodir.py``` and change the ```ISO_DIR``` variable value to path of the directory containing the ISO images.

## Updating grub.cfg

Run ```grub-mkconfig -o /boot/grub/grub.cfg```
