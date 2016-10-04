%ifarch %ix86
arch=i386
%endif
%ifarch x86_64
arch=x86_64
%endif
flavor=%1
kver=$(make -sC /usr/src/linux-obj/$arch/$flavor kernelrelease)
make -C /usr/src/linux-obj/$arch/$flavor \
     modules \
     M=/usr/src/kernel-modules/nvidia-%{-v*}-$flavor \
     SYSSRC=/lib/modules/$kver/source \
     SYSOUT=/usr/src/linux-obj/$arch/$flavor
pushd /usr/src/kernel-modules/nvidia-%{-v*}-$flavor 
make -f Makefile \
     nv-linux.o \
     SYSSRC=/lib/modules/$kver/source \
     SYSOUT=/usr/src/linux-obj/$arch/$flavor
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
cat >  /usr/lib/tmpfiles.d/nvidia-logind-acl-trick.conf << EOF
L /run/udev/static_node-tags/uaccess/nvidiactl - - - - /dev/nvidiactl
L /run/udev/static_node-tags/uaccess/nvidia-uvm - - - - /dev/nvidia-uvm
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
