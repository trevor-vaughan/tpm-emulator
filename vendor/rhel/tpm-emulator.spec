%define kernel_release %(ls -v /lib/modules | head -1)
%define kernel_release_short %(ls -v /lib/modules | head -1 | rev | cut -f3- -d'.' | rev)
%define destdir /opt/%{name}

Name:           tpm-emulator
Version:        0.7.4
Release:        1%{?dist}
Summary:        A Software-based TPM and MTM Emulator

License:        GPL-2.0
URL:            https://github.com/PeterHuewe/tpm-emulator
Source0:        tpm-emulator-%{version}.tar.gz

BuildRequires:  cmake
BuildRequires:  gmp-devel
BuildRequires:  kernel
BuildRequires:  kernel-devel
BuildRequires:  openssl
BuildRequires:  openssl-devel
Requires:       trousers
Requires:       tpm-emulator-kmod

%package -n tpm-emulator-kmod-%{kernel_release_short}
Summary:        The kernel module for the Software-based TPM and MTM Emulator
License:        GPL-2.0
BuildRequires:  kernel
BuildRequires:  kernel-devel
Requires:       kernel = %{kernel_release_short}
Provides:       tpm-emulator-kmod = %{kernel_release}

%description -n tpm-emulator-kmod-%{kernel_release_short}

tpmd_dev - a kernel module that provides the device /dev/tpm for
backward compatibility and forwards the received commands to tpmd

%package docs
Summary: Documentation for the TPM Emulator
License: GPL-2.0

%description docs

Documentation for the TPM Emulator

%description

The tpm emulator package comprises four main parts:

a) tpmd - a user-space application that implements the actual emulator
   and can be accessed by means of Unix domain sockets (Unix) or
   named pipes (Windows).

b) tpmd_dev - a kernel module that provides the device /dev/tpm for
   backward compatibility and forwards the received commands to tpmd

c) tddl - a TSS conformant device driver library for the emulator.

%prep
%setup -q

%build

if [ ! -d 'build' ]; then
  mkdir build
fi

cd build

cmake ../ -DCMAKE_INSTALL_PREFIX=/

make KERNEL_RELEASE=%{kernel_release} \
  KERNEL_BUILD=/lib/modules/%{kernel_release}/build \
  ARCH=%{_build_arch}

cd ..

%install
rm -rf %{buildroot}

mkdir -p %{buildroot}/etc/udev/rules.d
mkdir -p %{buildroot}/lib
mkdir -p %{buildroot}/etc/ld.so.conf.d
mkdir -p %{buildroot}/%{destdir}/bin
mkdir -p %{buildroot}/%{destdir}/lib
mkdir -p %{buildroot}/%{destdir}/include

cp -r vendor/rhel/init.d %{buildroot}/etc

make -C ./build \
  KERNEL_RELEASE=%{kernel_release} \
  KERNEL_BUILD=/lib/modules/%{kernel_release}/build \
  ARCH=%{_build_arch} \
  DESTDIR=%{buildroot}/%{destdir} \
  install

rm -rf %{buildroot}/usr

# Removing EL7 garbage
rm -f %{buildroot}/%{destdir}/lib/modules/*/*modules.*

mv %{buildroot}/%{destdir}/etc/udev/rules.d/*.rules %{buildroot}/etc/udev/rules.d
mv %{buildroot}/%{destdir}/lib/modules %{buildroot}/lib

echo "%{destdir}/lib" > %{buildroot}/etc/ld.so.conf.d/%{name}.conf

chmod o-rwx %{buildroot}/%{destdir}/bin/tpmd

%files
%defattr(-,root,root)
/etc/init.d/tpm-emulator
/etc/udev/rules.d/80-tpmd_dev.rules
/etc/ld.so.conf.d/%{name}.conf
%{destdir}/bin/tpmd
%{destdir}/include/tddl.h
%{destdir}/lib/libtddl.so.1.2.0.7
%{destdir}/lib/libtddl.so.1.2
%{destdir}/lib/libtddl.so
%{destdir}/lib/libtddl.a

%files -n tpm-emulator-kmod-%{kernel_release_short}
/lib/modules/%{kernel_release}/extra/tpmd_dev.ko

%files docs
%doc AUTHORS ChangeLog LICENSE README

%post -n tpm-emulator-kmod-%{kernel_release_short}
#!/bin/sh

if [ -f /sbin/depmod ]; then
  /sbin/depmod %{kernel_release}
fi

if [ -f /bin/systemctl ]; then
  /bin/systemctl daemon-reload
fi

%changelog
* Mon Dec 28 2015 Trevor Vaughan <tvaughan@onyxpoint.com>
- Initial Packaging for EL systems.
