#
# spec file for package nvidia-gfxG05
#
# Copyright (c) 2017 SUSE LINUX Products GmbH, Nuernberg, Germany.
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

# Please submit bugfixes or comments via http://bugs.opensuse.org/
#

# kABI symbols are no longer generated with openSUSE >= 13.1, since they
# became useless with zypper's 'multiversion' feature enabled for the kernel
# as default (multiple kernels can be installed at the same time; with
# different kABI symbols of course!). So it has been decided to match on the
# uname output of the kernel only. We cannot use that one for NVIDIA, since we
# only build against GA kernel. So let's get rid of this requirement.
#
%global __requires_exclude kernel-uname-r*
%global __gfx_gnum gfxG05

%if "%{?kernel_mode:%{kernel_mode}}%{!?kernel_mode:0}" == "open"
%define is_open 1
%define __basename nvidia-open-%{__gfx_gnum}
%define __pkg_summary NVIDIA open kernel module driver for GeForce RTX 2000 series and newer
%define __pkg_description_line open-source NVIDIA kernel module driver
%define __pkg_description_next RTX 2000
%else
%define is_open 0
%define __basename nvidia-%{__gfx_gnum}
%define __pkg_summary NVIDIA graphics driver kernel module for GeForce 600 series and newer
%define __pkg_description_line closed-source NVIDIA graphics driver kernel module
%define __pkg_description_next 600
%endif

Name:           %{__basename}
Version:        450.66
Release:        0
License:        SUSE-NonFree
Summary:        %{__pkg_summary}
URL:            https://www.nvidia.com/object/unix.html
Group:          System/Kernel
Source1:        http://download.nvidia.com/XFree86/Linux-x86_64/%{version}/NVIDIA-Linux-x86_64-%{version}.run
Source3:        preamble
Source4:        pci_ids-%{version}
Source5:        pci_ids-%{version}.new
Source6:        generate-service-file.sh
Source7:        README
Source8:        kmp-filelist
Source9:        kmp-filelist-old
Source10:       kmp-post.sh
Source11:       kmp-post-old.sh
Source12:       my-find-supplements
Source13:       kmp-preun.sh
Source14:       kmp-preun-old.sh
Source15:       kmp-pre.sh
Source16:       alternate-install-present
Source17:       kmp-postun-old.sh
Source18:       kmp-postun.sh
Source19:       modprobe.nvidia
Source20:       modprobe.nvidia.install.non_uvm
Source21:       modprobe.nvidia.install
Source22:       kmp-trigger.sh
Source23:       kmp-trigger-old.sh
Source24:       http://download.nvidia.com/XFree86/Linux-aarch64/%{version}/NVIDIA-Linux-aarch64-%{version}.run
NoSource:       1
NoSource:       6
NoSource:       7
Patch1:         n_kernel_write.patch
Patch2:         kernel-5.9.patch
BuildRequires:  kernel-source
BuildRequires:  kernel-syms
%ifarch x86_64
%if 0%{?sle_version} >= 120400 && !0%{?is_opensuse} 
BuildRequires:  kernel-syms-azure
%endif
%endif
BuildRequires:  module-init-tools
BuildRequires:  update-alternatives
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
ExclusiveArch:  %ix86 x86_64 aarch64
# patch the kmp template
%if 0%{?suse_version} > 1100
%define kmp_template -t
%define kmp_filelist kmp-filelist
%define kmp_post kmp-post.sh
%define kmp_preun kmp-preun.sh
%define kmp_pre kmp-pre.sh
%define kmp_postun kmp-postun.sh
%define kmp_trigger kmp-trigger.sh
%else
%define kmp_template -s
%define kmp_filelist kmp-filelist-old
%define kmp_post kmp-post-old.sh
%define kmp_preun kmp-preun-old.sh
%define kmp_pre kmp-pre.sh
%define kmp_postun kmp-postun-old.sh
%define kmp_trigger kmp-trigger-old.sh
%endif
%if 0%{!?kmp_template_name:1}
%if 0%{?suse_version} > 1010
%define kmp_template_name /usr/lib/rpm/kernel-module-subpackage
%else
%define kmp_template_name /usr/lib/rpm/rpm-suse-kernel-module-subpackage
%endif
%endif
# Tumbleweed uses %triggerin instead of %post script in order to generate
# and install kernel module
%if 0%{?suse_version} >= 1550 && 0%{?is_opensuse}
%(sed -e '/^%%preun\>/ r %_sourcedir/%kmp_preun' -e '/^%%pre\>/ r %_sourcedir/%kmp_pre' -e '/^%%postun\>/ r %_sourcedir/%kmp_postun' -e '/^Provides: multiversion(kernel)/d' %kmp_template_name >%_builddir/nvidia-kmp-template)
%(cp %_builddir/nvidia-kmp-template %_builddir/nvidia-kmp-template.old)
# if %pre scriptlet sample missing in template
%(grep -q "^%pre -n" %_builddir/nvidia-kmp-template || (echo "%pre -n %%{-n*}-kmp-%1" >> %_builddir/nvidia-kmp-template; cat %_sourcedir/%kmp_pre >> %_builddir/nvidia-kmp-template))
%(echo "%triggerin -n %%{-n*}-kmp-%1 -- kernel-default-devel" >> %_builddir/nvidia-kmp-template)
%(cat %_sourcedir/%kmp_preun               >> %_builddir/nvidia-kmp-template)
%(cat %_sourcedir/%kmp_trigger             >> %_builddir/nvidia-kmp-template)
# Let all initrds get generated by regenerate-initrd-posttrans
# if kernel-<flavor>-devel gets updated
%(echo "%%{?regenerate_initrd_posttrans}"  >> %_builddir/nvidia-kmp-template)
%ifarch %ix86
%(echo "%triggerin -n %%{-n*}-kmp-%1 -- kernel-pae-devel" >> %_builddir/nvidia-kmp-template)
%(cat %_sourcedir/%kmp_preun               >> %_builddir/nvidia-kmp-template)
%(cat %_sourcedir/%kmp_trigger             >> %_builddir/nvidia-kmp-template)
# Let all initrds get generated by regenerate-initrd-posttrans
# if kernel-<flavor>-devel gets updated
%(echo "%%{?regenerate_initrd_posttrans}"  >> %_builddir/nvidia-kmp-template)
%endif
%else
%(sed -e '/^%%post\>/ r %_sourcedir/%kmp_post' -e '/^%%preun\>/ r %_sourcedir/%kmp_preun' -e '/^%%pre\>/ r %_sourcedir/%kmp_pre' -e '/^%%postun\>/ r %_sourcedir/%kmp_postun' -e '/^Provides: multiversion(kernel)/d' %kmp_template_name >%_builddir/nvidia-kmp-template)
%(cp %_builddir/nvidia-kmp-template %_builddir/nvidia-kmp-template.old)
# moved from %kmp_post snippet to this place (boo#1145316)
%(sed -i '/^%%posttrans/i \
exit $RES' %_builddir/nvidia-kmp-template)
# if %pre scriptlet sample missing in template
%(grep -q "^%pre -n" %_builddir/nvidia-kmp-template || (echo "%pre -n %%{-n*}-kmp-%1" >> %_builddir/nvidia-kmp-template; cat %_sourcedir/%kmp_pre >> %_builddir/nvidia-kmp-template))
# Leap 42.3/sle12-sp3 needs this to recompile module after having
# uninstalled drm-kmp package (%triggerpostun)
%if 0%{?suse_version} < 1320 && 0%{?sle_version} >= 120300
%(echo "%triggerpostun -n %%{-n*}-kmp-%1 -- drm-kmp-default" >> %_builddir/nvidia-kmp-template)
%(cat %_sourcedir/%kmp_preun               >> %_builddir/nvidia-kmp-template)
%(cat %_sourcedir/%kmp_post                >> %_builddir/nvidia-kmp-template)
%(echo 'nvr=%%{-n*}-kmp-%1-%_this_kmp_version-%%{-r*}' >> %_builddir/nvidia-kmp-template)
%(echo 'wm2=/usr/lib/module-init-tools/weak-modules2' >> %_builddir/nvidia-kmp-template)
%(echo 'if [ -x $wm2 ]; then' >> %_builddir/nvidia-kmp-template)
%(echo '    %%{-b:KMP_NEEDS_MKINITRD=1} INITRD_IN_POSTTRANS=1 /bin/bash -${-/e/} $wm2 --add-kmp $nvr' >> %_builddir/nvidia-kmp-template)
%(echo 'fi' >> %_builddir/nvidia-kmp-template)
# moved from %kmp_post snippet to this place (boo#1145316)
%(echo 'exit $RES' >> %_builddir/nvidia-kmp-template)
# Let all initrds get generated by regenerate-initrd-posttrans
# if drm-kmp-default gets uninstalled
%(echo "%%{?regenerate_initrd_posttrans}"  >> %_builddir/nvidia-kmp-template)
%endif
%endif
%define x_flavors kdump um debug xen xenpae
%if 0%{!?nvbuild:1}
%define kver %(for dir in /usr/src/linux-obj/*/*/; do make %{?jobs:-j%jobs} -s -C "$dir" kernelversion; break; done |perl -ne '/(\\d+)\\.(\\d+)\\.(\\d+)?/&&printf "%%d%%02d%%03d\\n",$1,$2,$3')
%if %kver >= 206027
%if %kver < 206031
%define x_flavors kdump um debug
%endif
%endif
%endif
%kernel_module_package %kmp_template %_builddir/nvidia-kmp-template -p %_sourcedir/preamble -f %_sourcedir/%kmp_filelist -x %x_flavors

# supplements no longer depend on the driver
%if (0%{?sle_version} >= 150100 || 0%{?suse_version} >= 1550)
%define pci_id_file %_sourcedir/pci_ids-%version
%else
%define pci_id_file %_sourcedir/pci_ids-%version.new
%endif
# rpm 4.14.1 changed again (boo#1087460)
%define __kmp_supplements %_sourcedir/my-find-supplements %pci_id_file
# rpm 4.9+ using the internal dependency generators
%define __ksyms_supplements %_sourcedir/my-find-supplements %pci_id_file %name
# older rpm
%define __find_supplements %_sourcedir/my-find-supplements %pci_id_file %name

# get rid of ksyms on Leap 15.1/15.2; for weird reasons they are not generated on TW
%define __kmp_requires %{nil}

%description
This package provides the %{__pkg_description_line} NVIDIA graphics driver kernel
for GeForce %{__pkg_description_next} series and newer GPUs.

%package KMP
License:        SUSE-NonFree
Summary:        %{__pkg_summary}
Group:          System/Kernel
%if 0%{?is_open} == 1
Conflicts:      nvidia-%{__gfx_gnum}
Provides:       nvidia-%{__gfx_gnum}-kmp = %{version}
Provides:       nvidia-%{__gfx_gnum}-kmp-default = %{version}
%else
Conflicts:      nvidia-open-%{__gfx_gnum}
%endif

%description KMP
This package provides the %{__pkg_description_line} NVIDIA graphics driver kernel
for GeForce %{__pkg_description_next} series and newer GPUs.

%prep
echo "kver = %kver"
%setup -T -c %{name}-%{version}
%ifarch x86_64
sh %{SOURCE1} -x --target NVIDIA-Linux-x86_64-%{version}
pushd NVIDIA-Linux-x86*-%{version}*/
%endif
%ifarch aarch64
sh %{SOURCE24} -x --target NVIDIA-Linux-aarch64-%{version}
pushd NVIDIA-Linux-aarch64*-%{version}*/
%endif
# apply patches here ...
%if 0%{?sle_version} >= 120400
%if 0%{?sle_version} < 150200
%patch1 -p0
%endif
%endif
%if 0%{?suse_version} >=  1550
%patch2 -p1
%endif
find . -name "*.orig" -delete
popd
#rm -rf NVIDIA-Linux-x86*-%{version}-*/usr/src/nv/precompiled
mkdir -p source/%{version}

# use kernel-open variant
%if 0%{?is_open} == 1
%ifarch x86_64
cp -R NVIDIA-Linux-x86*-%{version}*/kernel-open/* source/%{version} || :
%endif
%ifarch aarch64
cp -R NVIDIA-Linux-aarch64*-%{version}*/kernel-open/* source/%{version} || :
%endif
# use legacy variant
%else
%ifarch x86_64
cp -R NVIDIA-Linux-x86*-%{version}*/kernel/* source/%{version} || :
%endif
%ifarch aarch64
cp -R NVIDIA-Linux-aarch64*-%{version}*/kernel/* source/%{version} || :
%endif
%endif

pushd source/%{version}
 # mark support as external
 echo "nvidia.ko external" > Module.supported
# IDs have already been added to G03 when we no longer built/published G05
# for sle11 (bnc#920799). Since we now build/publish it again for sle11
# (bnc#929127), we need to make sure that IDs are not registered for both
# driver series G03 and G05. So remove them from G05.
%if 0%{?suse_version} < 1120
 for id in 0x1340 0x1341 \
           0x1380 0x1381 0x1382 \
           0x1390 0x1391 0x1392 0x1393 \
           0x13BA 0x13BB; do
   sed -i /${id}/d %_sourcedir/pci_ids-%{version}
   sed -i /${id}/d %_sourcedir/pci_ids-%{version}.new
 done
%endif
 #already in G03 (meanwhile appears in G05 output after fixing script for ID generation)
 for id in 0x0FEC; do
   sed -i /${id}/d %_sourcedir/pci_ids-%{version}
   sed -i /${id}/d %_sourcedir/pci_ids-%{version}.new
 done
 chmod 755 %_sourcedir/my-find-supplements*
popd
mkdir obj
%ifnarch aarch64
sed -i -e 's,-o "$ARCH" = "x86_64",-o "$ARCH" = "x86_64" -o "$ARCH" = "x86",' source/*/conftest.sh
%endif

%build
export EXTRA_CFLAGS='-DVERSION=\"%{version}\"'
%if 0%{?suse_version} >= 1550
# Runtime:
# nvidia_uvm: module uses symbols from proprietary module nvidia, inheriting taint.
#
# Buildtime:
# When switching from "Dual MIT/GPL" license to "MIT" license for nvidia-uvm module:
# FATAL: modpost: GPL-incompatible module nvidia-uvm.ko uses GPL-only symbol '__mmu_notifier_register'
#
# So let's disable it for now ...
export NV_EXCLUDE_KERNEL_MODULES=nvidia-uvm
%endif
export NV_EXCLUDE_KERNEL_MODULES=nvidia-peermem
for flavor in %flavors_to_build; do
    src=/lib/modules/$(make %{?jobs:-j%jobs} -siC %{kernel_source $flavor} kernelrelease)/source
    %if 0%{?suse_version} <= 1020
    export SYSSRC=$src
    %endif
    rm -rf obj/$flavor
    cp -r source obj/$flavor
    make %{?jobs:-j%jobs} -C /usr/src/linux-obj/%_target_cpu/$flavor modules M=$PWD/obj/$flavor/%{version} SYSSRC="$src" SYSOUT=/usr/src/linux-obj/%_target_cpu/$flavor
    pushd $PWD/obj/$flavor/%{version}
    make %{?jobs:-j%jobs} -f Makefile nv-linux.o SYSSRC="$src" SYSOUT=/usr/src/linux-obj/%_target_cpu/$flavor
    popd
done

%install
### do not sign the ghost .ko file, it is generated on target system anyway
export BRP_PESIGN_FILES=""
export INSTALL_MOD_PATH=%{buildroot}
export INSTALL_MOD_DIR=updates
%if 0%{?suse_version} >= 1550
# Runtime:
# nvidia_uvm: module uses symbols from proprietary module nvidia, inheriting taint.
#
# Buildtime:
# When switching from "Dual MIT/GPL" license to "MIT" license for nvidia-uvm module:
# FATAL: modpost: GPL-incompatible module nvidia-uvm.ko uses GPL-only symbol '__mmu_notifier_register'
#
# So let's disable it for now ...
export NV_EXCLUDE_KERNEL_MODULES=nvidia-uvm
%endif
export NV_EXCLUDE_KERNEL_MODULES=nvidia-peermem
for flavor in %flavors_to_build; do
    export SYSSRC=/lib/modules/$(make %{?jobs:-j%jobs} -siC %{kernel_source $flavor} kernelrelease)/source
    make %{?jobs:-j%jobs} -C /usr/src/linux-obj/%_target_cpu/$flavor modules_install M=$PWD/obj/$flavor/%{version}
    #install -m 644 $PWD/obj/$flavor/%{version}/{nv-linux.o,nv-kernel.o} \
    #  %{buildroot}/lib/modules/*-$flavor/updates
    mkdir -p %{buildroot}/usr/src/kernel-modules/nvidia-%{version}-${flavor}
    cp -r source/%{version}/* %{buildroot}/usr/src/kernel-modules/nvidia-%{version}-${flavor}
done
mkdir -p %{buildroot}%{_sysconfdir}/modprobe.d
mkdir -p %{buildroot}/usr/lib/nvidia/
for flavor in %flavors_to_build; do
  echo "blacklist nouveau" > %{buildroot}%{_sysconfdir}/modprobe.d/nvidia-$flavor.conf
  # make it with flavor name or rpmlint complains about not making it conflict
  cp %{SOURCE16} %{buildroot}/usr/lib/nvidia/alternate-install-present-${flavor}
  touch %{buildroot}/usr/lib/nvidia/alternate-install-present
  mkdir -p %{buildroot}/etc/dracut.conf.d
  cat  > %{buildroot}/etc/dracut.conf.d/60-nvidia-$flavor.conf << EOF
omit_drivers+=" nvidia nvidia-drm nvidia-modeset nvidia-uvm nvidia-peermem "
EOF
  %if 0%{?suse_version} > 1100
  mkdir -p %{buildroot}%{_sysconfdir}/modprobe.d
  %if 0%{?suse_version} < 1120
  modfile=%{buildroot}%{_sysconfdir}/modprobe.d/51-nvidia-$flavor.conf
  %else
  modfile=%{buildroot}%{_sysconfdir}/modprobe.d/50-nvidia-$flavor.conf
  %endif
  %ifarch x86_64 aarch64
  modscript=$RPM_SOURCE_DIR/modprobe.nvidia.install
  %else
  modscript=$RPM_SOURCE_DIR/modprobe.nvidia.install.non_uvm
  %endif
  install -m 644 $RPM_SOURCE_DIR/modprobe.nvidia $modfile
  # on sle11 "options nvidia" line is already in 
  # /etc/modprobe.d/50-nvidia.conf owned by xorg-x11-server package
  %if 0%{?suse_version} < 1120
  sed -i 's/^options nvidia.*//g' $modfile
  %endif
  echo -n "install nvidia " >> $modfile 
  tail -n +3 $modscript | awk '{ printf "%s ", $0 }' >> $modfile
  %endif
done
%changelog
