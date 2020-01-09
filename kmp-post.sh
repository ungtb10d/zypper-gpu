%ifarch %ix86
arch=i386
%endif
%ifarch x86_64
arch=x86_64
%endif
%ifarch aarch64
arch=aarch64
%endif
flavor=%1
kver=$(make -sC /usr/src/linux-obj/$arch/$flavor kernelrelease)
RES=0
make -C /usr/src/linux-obj/$arch/$flavor \
     modules \
     M=/usr/src/kernel-modules/nvidia-%{-v*}-$flavor \
     SYSSRC=/lib/modules/$kver/source \
     SYSOUT=/usr/src/linux-obj/$arch/$flavor || RES=1
pushd /usr/src/kernel-modules/nvidia-%{-v*}-$flavor 
make -f Makefile \
     nv-linux.o \
     SYSSRC=/lib/modules/$kver/source \
     SYSOUT=/usr/src/linux-obj/$arch/$flavor || RES=1
popd
install -m 755 -d /lib/modules/%2-$flavor/updates
install -m 644 /usr/src/kernel-modules/nvidia-%{-v*}-$flavor/nvidia*.ko \
	/lib/modules/%2-$flavor/updates
depmod %2-$flavor

%{_sbindir}/update-alternatives --install /usr/lib/nvidia/alternate-install-present alternate-install-present /usr/lib/nvidia/alternate-install-present-$flavor 11

# Create symlinks for udev so these devices will get user ACLs by logind later (bnc#1000625)
mkdir -p /run/udev/static_node-tags/uaccess
mkdir -p /usr/lib/tmpfiles.d
ln -snf /dev/nvidiactl /run/udev/static_node-tags/uaccess/nvidiactl 
ln -snf /dev/nvidia-uvm /run/udev/static_node-tags/uaccess/nvidia-uvm
ln -snf /dev/nvidia-modeset /run/udev/static_node-tags/uaccess/nvidia-modeset
cat >  /usr/lib/tmpfiles.d/nvidia-logind-acl-trick.conf << EOF
L /run/udev/static_node-tags/uaccess/nvidiactl - - - - /dev/nvidiactl
L /run/udev/static_node-tags/uaccess/nvidia-uvm - - - - /dev/nvidia-uvm
L /run/udev/static_node-tags/uaccess/nvidia-modeset - - - - /dev/nvidia-modeset
EOF
devid=-1
for dev in $(ls -d /sys/bus/pci/devices/*); do 
  vendorid=$(cat $dev/vendor)
  if [ "$vendorid" == "0x10de" ]; then 
    class=$(cat $dev/class)
    classid=${class%%00}
    if [ "$classid" == "0x0300" -o "$classid" == "0x0302" ]; then 
      devid=$((devid+1))
      ln -snf /dev/nvidia${devid} /run/udev/static_node-tags/uaccess/nvidia${devid}
      echo "L /run/udev/static_node-tags/uaccess/nvidia${devid} - - - - /dev/nvidia${devid}" >> /usr/lib/tmpfiles.d/nvidia-logind-acl-trick.conf
    fi
  fi
done

echo
echo "Modprobe blacklist files have been created at /etc/modprobe.d to \
prevent Nouveau from loading. This can be reverted by deleting \
/etc/modprobe.d/nvidia-*.conf."
echo
echo "*** Reboot your computer and verify that the NVIDIA graphics driver \
can be loaded. ***"
echo

# Let all initrds get generated by regenerate-initrd-posttrans
mkdir -p /run/regenerate-initrd
touch /run/regenerate-initrd/all

# Recreate initrd without KMS if required (sle11)
# Only touch config, if the use of KMS is enabled in initrd;
if grep -q NO_KMS_IN_INITRD=\"no\" /etc/sysconfig/kernel; then
  sed -i 's/NO_KMS_IN_INITRD.*/NO_KMS_IN_INITRD="yes"/g' /etc/sysconfig/kernel
fi

# groups are now dynamic
if [ -f /etc/modprobe.d/50-nvidia-default.conf ]; then
  VIDEOGID=`getent group video | cut -d: -f3`
  sed -i "s/33/$VIDEOGID/" /etc/modprobe.d/50-nvidia-default.conf
fi

#needed to move this to specfile after running weak-modules2 (boo#1145316)
#exit $RES
