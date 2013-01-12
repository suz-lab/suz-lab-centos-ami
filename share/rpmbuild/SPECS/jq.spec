%define version 1.2

Summary: Command-line JSON processor
Name   : jq
Version: %{version}
Release: 0%{?dist}.suzlab_1
Source0: jq-%{version}.tar.gz
URL    : https://github.com/stedolan/jq
License: BSD
Group  : Applications/System

%description
jq is a command-line JSON processor

%prep

%setup

%build
echo "Building in: \"$(pwd)\""
make

%install
echo "Installing to: \"${RPM_BUILD_ROOT}\""
install -d -m 0755 ${RPM_BUILD_ROOT}/usr/bin
install -m 0755 jq ${RPM_BUILD_ROOT}/usr/bin

%clean
rm -rf ${RPM_BUILD_ROOT}

%files
%defattr(-,root,root)
%{_bindir}/jq

%changelog
* Sat Jan 12 2013 Hiroyasu Suzuki <suzuki@suz-lab.com> - 1.2-0_1
- Initial Release

%pre

%post
