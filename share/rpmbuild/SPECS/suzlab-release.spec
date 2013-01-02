Name: suzlab-release
Version: 6 
Release: 1
Summary: YUM configuration for SUZ-LAB Repository
Group: System Environment/Base
License: GPL
URL: http://www.suz-lab.com/
Source0: suz-lab.repo
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch: noarch
Requires: redhat-release >= %{version}
%description
%prep
%setup -q -c -T
install -pm 644 %{SOURCE0} .
%build
%install
rm -rf $RPM_BUILD_ROOT
install -dm 755 $RPM_BUILD_ROOT%{_sysconfdir}/yum.repos.d
install -pm 644 %{SOURCE0} $RPM_BUILD_ROOT%{_sysconfdir}/yum.repos.d
%clean
rm -rf $RPM_BUILD_ROOT
%files
%defattr(-,root,root,-)
%config(noreplace) /etc/yum.repos.d/*
%changelog
* Wed Jan 02 2013 Hiroyasu Suzuki <suzuki@suz-lab.com> - 6-1
- Initial Package for CentOS 6
