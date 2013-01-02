#% define beta_tag rc1
%define patchlevel .2
%define baseversion 4.1

Version: %{baseversion}%{patchlevel}
Name: bash
Summary: The GNU Bourne Again shell
Release: 9%{?dist}
Group: System Environment/Shells
License: GPLv3+
Url: http://www.gnu.org/software/bash
Source0: ftp://ftp.gnu.org/gnu/bash/bash-%{baseversion}.tar.gz

# For now there isn't any doc
#Source2: ftp://ftp.gnu.org/gnu/bash/bash-doc-%{version}.tar.gz

Source1: dot-bashrc
Source2: dot-bash_profile
Source3: dot-bash_logout

# Official upstream patches
Patch001: ftp://ftp.gnu.org/pub/gnu/bash/bash-4.1-patches/bash41-001
Patch002: ftp://ftp.gnu.org/pub/gnu/bash/bash-4.1-patches/bash41-002

# Other patches
Patch101: bash-2.02-security.patch
Patch102: bash-2.03-paths.patch
Patch103: bash-2.03-profile.patch
Patch104: bash-2.05a-interpreter.patch
Patch105: bash-2.05b-debuginfo.patch
Patch106: bash-2.05b-manso.patch
Patch107: bash-2.05b-pgrp_sync.patch
Patch108: bash-2.05b-readline-oom.patch
Patch109: bash-2.05b-xcc.patch
Patch110: bash-3.2-audit.patch
Patch112: bash-3.2-ssh_source_bash.patch
Patch113: bash-bashbug.patch
Patch115: bash-infotags.patch
Patch116: bash-requires.patch
Patch117: bash-setlocale.patch
Patch118: bash-tty-tests.patch


# 484809, check if interp section is NOBITS
Patch123: bash-4.0-nobits.patch

# 605137, Same CFLAGS in examples' Makefile for all arches
Patch124: bash-4.1-examples.patch

# 618289, don't segfault when trying to bind int variable to array
# with bad array subsrcipt
Patch125: bash-4.1-bind_int_variable.patch

# 664468, Builtins like echo and printf won't report errors
# when output does not succeed due to EPIPE
Patch126: bash-4.1-broken_pipe.patch

# 619704, Manpages clarifications
Patch127: bash-4.1-manpage.patch

# 800473, Don't call malloc in signal handler
Patch128: bash-4.1-defer-sigchld-trap.patch

Requires(post): ncurses-libs
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires: texinfo bison
BuildRequires: ncurses-devel
BuildRequires: autoconf, gettext

%description
The GNU Bourne Again shell (Bash) is a shell or command language
interpreter that is compatible with the Bourne shell (sh). Bash
incorporates useful features from the Korn shell (ksh) and the C shell
(csh). Most sh scripts can be run by bash without modification.

%package doc
Summary: Documentation files for %{name}
Group: Development/Languages
Requires: %{name} = %{version}-%{release}

%description doc
This package contains documentation files for %{name}.

%define pkgdocdir %{_datadir}/doc/%{name}-%{version}

%prep
#%setup -q -a 2
%setup -q -n %{name}-%{baseversion}

# Official upstream patches
%patch001 -p0 -b .001
%patch002 -p0 -b .002

# Other patches
%patch101 -p1 -b .security
%patch102 -p1 -b .paths
%patch103 -p1 -b .profile
%patch104 -p1 -b .interpreter
%patch105 -p1 -b .debuginfo
%patch106 -p1 -b .manso
%patch107 -p1 -b .pgrp_sync
%patch108 -p1 -b .readline_oom
%patch109 -p1 -b .xcc
%patch110 -p1 -b .audit
%patch112 -p1 -b .ssh_source_bash
%patch113 -p1 -b .bashbug
%patch115 -p1 -b .infotags
%patch116 -p1 -b .requires
%patch117 -p1 -b .setlocale
%patch118 -p1 -b .tty_tests
%patch123 -p1 -b .nobits
%patch124 -p1 -b .examples
%patch125 -p1 -b .bind_int_variable
%patch126 -p1 -b .broken_pipe
%patch127 -p1 -b .manpage
%patch128 -p1 -b .defer-sigchld-trap

echo %{version} > _distribution
echo %{release} > _patchlevel

%build
autoconf
%configure --with-bash-malloc=no --with-afs

# Recycles pids is neccessary. When bash's last fork's pid was X
# and new fork's pid is also X, bash has to wait for this same pid.
# Without Recycles pids bash will not wait.

# For -fwrapv option see https://www.securecoding.cert.org/confluence/display/seccode/INT32-C.+Ensure+that+operations+on+signed+integers+do+not+result+in+overflow
# Bash needs to be fixed.
make "CFLAGS=$CFLAGS -fwrapv" "CPPFLAGS=-D_GNU_SOURCE -DRECYCLES_PIDS `getconf LFS_CFLAGS`"
%check
make check

%install
rm -rf $RPM_BUILD_ROOT

if [ -e autoconf ]; then
  # Yuck. We're using autoconf 2.1x.
  export PATH=.:$PATH
fi

# Fix bug #83776
perl -pi -e 's,bashref\.info,bash.info,' doc/bashref.info

make DESTDIR=$RPM_BUILD_ROOT install

mkdir -p $RPM_BUILD_ROOT/etc

# make manpages for bash builtins as per suggestion in DOC/README
pushd doc
sed -e '
/^\.SH NAME/, /\\- bash built-in commands, see \\fBbash\\fR(1)$/{
/^\.SH NAME/d
s/^bash, //
s/\\- bash built-in commands, see \\fBbash\\fR(1)$//
s/,//g
b
}
d
' builtins.1 > man.pages
for i in echo pwd test kill; do
  perl -pi -e "s,$i,,g" man.pages
  perl -pi -e "s,  , ,g" man.pages
done

install -c -m 644 builtins.1 ${RPM_BUILD_ROOT}%{_mandir}/man1/builtins.1

for i in `cat man.pages` ; do
  echo .so man1/builtins.1 > ${RPM_BUILD_ROOT}%{_mandir}/man1/$i.1
  chmod 0644 ${RPM_BUILD_ROOT}%{_mandir}/man1/$i.1
done

# remove backup files so they will not be in bash-doc
for i in bashbug requires manpage; do
  rm -rf *.$i
done
popd

# Link bash man page to sh so that man sh works.
ln -s bash.1 ${RPM_BUILD_ROOT}%{_mandir}/man1/sh.1

# Not for printf, true and false (conflict with coreutils)
rm -f $RPM_BUILD_ROOT/%{_mandir}/man1/printf.1
rm -f $RPM_BUILD_ROOT/%{_mandir}/man1/true.1
rm -f $RPM_BUILD_ROOT/%{_mandir}/man1/false.1

pushd $RPM_BUILD_ROOT
mkdir ./bin
mv ./usr/bin/bash ./bin
ln -sf bash ./bin/sh
rm -f .%{_infodir}/dir
popd
mkdir -p $RPM_BUILD_ROOT/etc/skel
install -c -m644 %SOURCE1 $RPM_BUILD_ROOT/etc/skel/.bashrc
install -c -m644 %SOURCE2 $RPM_BUILD_ROOT/etc/skel/.bash_profile
install -c -m644 %SOURCE3 $RPM_BUILD_ROOT/etc/skel/.bash_logout
LONG_BIT=$(getconf LONG_BIT)
mv $RPM_BUILD_ROOT%{_bindir}/bashbug \
   $RPM_BUILD_ROOT%{_bindir}/bashbug-"${LONG_BIT}"

# Fix missing sh-bangs in example scripts (bug #225609).
for script in \
  examples/scripts/krand.bash \
  examples/scripts/bcsh.sh \
  examples/scripts/precedence \
  examples/scripts/shprompt
do
  cp "$script" "$script"-orig
  echo '#!/bin/bash' > "$script"
  cat "$script"-orig >> "$script"
  rm -f "$script"-orig
done

%find_lang %{name}

# copy doc to /usr/share/doc
mkdir -p $RPM_BUILD_ROOT/%{pkgdocdir}
for file in COPYING CHANGES COMPAT NEWS NOTES POSIX doc examples
do
  cp -r "$file" $RPM_BUILD_ROOT/%{pkgdocdir}
done
%clean
rm -rf $RPM_BUILD_ROOT

# ***** bash doesn't use install-info. It's always listed in %{_infodir}/dir
# to prevent prereq loops

# post is in lua so that we can run it without any external deps.  Helps
# for bootstrapping a new install.
# Jesse Keating 2009-01-29 (code from Ignacio Vazquez-Abrams)
%post -p <lua>
bashfound = false;
shfound = false;
 
f = io.open("/etc/shells", "r");
if f == nil
then
  f = io.open("/etc/shells", "w");
else
  repeat
    t = f:read();
    if t == "/bin/bash"
    then
      bashfound = true;
    end
    if t == "/bin/sh"
    then
      shfound = true;
    end
  until t == nil;
end
f:close()
 
f = io.open("/etc/shells", "a");
if not bashfound
then
  f:write("/bin/bash\n")
end
if not shfound
then
  f:write("/bin/sh\n")
end
f:close()

%postun
if [ "$1" = 0 ]; then
    /bin/grep -v '^/bin/bash$' < /etc/shells | \
      /bin/grep -v '^/bin/sh$' > /etc/shells.new
    /bin/mv /etc/shells.new /etc/shells
fi

%files -f %{name}.lang
%defattr(-,root,root)
%config(noreplace) /etc/skel/.b*
/bin/sh
/bin/bash
%doc %{pkgdocdir}/COPYING
%attr(0755,root,root) %{_bindir}/bashbug-*
%{_infodir}/bash.info*
%{_mandir}/*/*
%{_mandir}/*/..1*

%files doc
%defattr(-, root, root)
%doc %{pkgdocdir}

# For now there isn't any doc
#%doc doc/*.ps doc/*.0 doc/*.html doc/article.txt

%changelog
* Thu Apr 19 2012 Roman Rakus <rrakus@redhat.com> - 4.1.2-9
- Don't call malloc in signal handler
  Resolves: #800473

* Thu Jan 27 2011 Roman Rakus <rrakus@redhat.com> - 4.1.2-8
- Don't include backup file in bash-doc
  Resolves: #619704

* Thu Jan 27 2011 Roman Rakus <rrakus@redhat.com> - 4.1.2-7
- Compile with -fwrapv option to satisfy rpmdiff.
  Resolves: #619704

* Wed Jan 26 2011 Roman Rakus <rrakus@redhat.com> - 4.1.2-6
- Few man pages clarifications
  Resolves: #619704

* Thu Jan 06 2011 Roman Rakus <rrakus@redhat.com> - 4.1.2-5
- Builtins like echo and printf won't report errors
  when output does not succeed due to EPIPE
  Resolves: #664468

* Wed Dec 01 2010 Roman Rakus <rrakus@redhat.com> - 4.1.2-4
- don't segfault when trying to bind int variable to array
  with bad array subsrcipt
  Resolves: #618289

* Tue Jun 22 2010 Roman Rakus <rrakus@redhat.com> - 4.1.2-3
- Same CFLAGS in examples' Makefile for all arches
  Resolves: #605137

* Fri Jan 22 2010 Roman Rakus <rrakus@redhat.com>  4.1.2-2
- Corrected patch for fuzz=0
  Resolves: #542692

* Fri Jan 22 2010 Roman Rakus rrakus@redhat.com 4.1.2-1
- rebase to 4.1
- Patch level 2
  Resolves #542692
- Include COPYING in bash base rpm
  Resolves #553250

* Fri Jan 08 2010 Roman Rakus rrakus@redhat.com 4.0.35-3
- Include COPYING in doc dir
  Resolves #553250

* Fri Dec 11 2009 Roman Rakus <rrakus@redhat.com> - 4.0.35-1
- Don't segfault when TERM=eterm* and EMACS is unset (#530911)
- patch level 35

* Wed Sep 16 2009 Roman Rakus <rrakus@redhat.com> - 4.0.33-1
- Patch level 33
- spec file cleanup

* Fri Sep 04 2009 Roman Rakus <rrakus@redhat.com> - 4.0.28-3
- check if interp section is NOBITS
- define Recycles pids

* Wed Aug 26 2009 Roman Rakus <rrakus@redhat.com> - 4.0.28-2
- alloc memory for key in creation associative array (#518644)

* Tue Jul 28 2009 Roman Rakus <rrakus@redhat.com> - 4.0.28-1
- Upstream patch level 28

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.0.24-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Tue May 19 2009 Roman Rakus <rrakus@redhat.com> - 4.0.24-1
- Upstream patch level 24

* Wed Apr 22 2009 Roman Rakus <rrakus@redhat.com> - 4.0.16-1
- better to use patch level in version tag like vim do

* Tue Apr 21 2009 Roman Rakus <rrakus@redhat.com> - 4.0-7.16
- Use patch level in Release tag

* Wed Apr 08 2009 Roman Rakus <rrakus@redhat.com> - 4.0-6
- Official upstream patch level 16

* Mon Mar 30 2009 Roman Rakus <rrakus@redhat.com> - 4.0-5
- Split documentation, use bash-doc package
  Resolves: #492447

* Sat Mar 21 2009 Lubomir Rintel <lkundrak@v3.sk> - 4.0-4
- Add full URLs to upstream patches
- Don't uselessly use %%version macro

* Wed Mar 11 2009 Roman Rakus <rrakus@redhat.com> - 4.0-3
- Official upstream patch level 10

* Wed Feb 25 2009 Roman Rakus <rrakus@redhat.com> - 4.0-2
- Save parser state in pcomplete.
  Resolves: #487257

* Tue Feb 24 2009 Roman Rakus <rrakus@redhat.com> - 4.0-1
- Release of bash-4.0

* Mon Feb 23 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.0-0.5.rc1
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Wed Feb 11 2009 Roman Rakus <rrakus@redhat.com> - 4.0-0.4.rc1
- Fix handling pipelines with `set -e'
  Resolves: #483385

* Thu Jan 29 2009 Roman Rakus <rrakus@redhat.com> - 4.0-0.3.rc1
- No more debug output
  Resolves: #483002

* Wed Jan 28 2009 Jesse Keating <jkeating@redhat.com> - 4.0-0.2.rc1
- Replace post code with lua to be able to not have external deps

* Mon Jan 26 2009 Roman Rakus <rrakus@redhat.com> - 4.0-0.1.rc1
- Fixed release tag

* Wed Jan 21 2009 Roman Rakus <rrakus@redhat.com> - 4.0-rc1.1
- Bump to upstream bash-4.0-rc1

* Mon Dec 15 2008 Roman Rakus <rrakus@redhat.com> - 3.2-33
- fc builtin fix
  Resolves: #438841

* Mon Dec 15 2008 Roman Rakus <rrakus@redhat.com> - 3.2-32
- Enabling auditing
  Resolves: #476216

* Tue Dec 09 2008 Roman Rakus <rrakus@redhat.com> - 3.2-31
- Patchlevel 48

* Thu Dec 04 2008 Roman Rakus <rrakus@redhat.com> - 3.2-30
- Added check for `command_not_found_handler' shell function
  Resolves: #432579

* Tue Oct 28 2008 Jesse Keating <jkeating@redhat.com> - 3.2-29
- Add the Requires(post) back for ncurses-libs, so that rpm knows
  where to break the loop.  The post actually does require the curses
  libs for the sh calls.  Could consider doing this in LUA and not have
  any external deps.

* Thu Oct 23 2008 Roman Rakus <rrakus@redhat.com> - 3.2-28
- Removing Requires for mktemp and ncurses, which cause
  dependencing loop
- Enabling #define SSH_SOURCE_BASHRC, because ssh changed.
  Resolves: #458839
- Catch signals right after calling execve()
  Resolves: #455548

* Thu Jul 17 2008 Roman Rakus <rrakus@redhat.com> - 3.2-27
- Changes in man page - #442018, #445692, #446625, #453409
- Changed patches to satisfy fuzz=0

* Thu Jun  5 2008 Roman Rakus <rrakus@redhat.com> - 3.2-26
- Patchlevel 39

* Tue Jun  3 2008 Roman Rakus <rrakus@redhat.com> - 3.2-25
- #449512 - reverting back last change - don't use glob library

* Wed May 28 2008 Roman Rakus <rrakus@redhat.com> - 3.2-24
- #217359 - use posix glob library

* Thu May 22 2008 Roman Rakus <rrakus@redhat.com> - 3.2-23
- #446420 - COMP_WORDBREAKS settings now works

* Fri Feb 29 2008 Tomas Janousek <tjanouse@redhat.com> - 3.2-22
- drop /usr/bin/clear from /etc/skel/.bash_logout as suggested by #429406

* Wed Feb 20 2008 Fedora Release Engineering <rel-eng@fedoraproject.org> - 3.2-21
- Autorebuild for GCC 4.3

* Mon Jan 14 2008 Tomas Janousek <tjanouse@redhat.com> - 3.2-20
- Added bash32-026 upstream official patch
- Added bash32-027 upstream official patch (#249987)
- Added bash32-028 upstream official patch
- Added bash32-029 upstream official patch (#286861)
- Added bash32-030 upstream official patch
- Added bash32-031 upstream official patch (#358231)
- Added bash32-032 upstream official patch
- Added bash32-033 upstream official patch
- Fix insert command repeating in vi mode (#190350)

* Tue Nov 06 2007 Tomas Janousek <tjanouse@redhat.com> - 3.2-19
- fix cursor position when prompt has one invisible character (#358231)
- dropped examples/loadables/ from docs, since it wasn't possible to build them
  anyway (#174380)
- fix #286861: Wrong input confuses bash's arithmetic unit permanently
- fix #344411: $RANDOM stays the same when job executed in the background

* Fri Aug 31 2007 Pete Graner <pgraner@redhat.com> - 3.2-18
- Added bash32-021 upstream official patch
- Added bash32-025 upstream official patch
- Added bash32-024 upstream official patch
- Added bash32-023 upstream official patch
- Added bash32-022 upstream official patch

* Wed Aug 29 2007 Pete Graner <pgraner@redhat.com> - 3.2-17
- Added bash32-018 upstream official patch
- Added bash32-020 upstream official patch
- Added bash32-019 upstream official patch

* Thu Aug 23 2007 Pete Graner <pgraner@redhat.com> - 3.2-16
- Rebuild

* Mon Aug 20 2007 Pete Graner <pgraner@redhat.com> - 3.2-15
- Update to the Improve bash $RANDOM pseudo RNG (bug #234906) 
  now works with subshells and make $RANDOM on demand thus reducing the 
  amount of AVCs thrown.

* Thu Aug 16 2007 Pete Graner <pgraner@redhat.com> - 3.2-15
- Changed spec file License to GPLv2+

* Wed Aug 15 2007 Pete Graner <pgraner@redhat.com> - 3.2-13
- Improve bash $RANDOM pseudo RNG (bug #234906)

* Fri Jul 20 2007 Tim Waugh <twaugh@redhat.com> 3.2-12
- Quote environment variables in the post scriptlet to prevent upgrade
  failures (bug #249005).

* Thu Jul  5 2007 Tim Waugh <twaugh@redhat.com> 3.2-11
- Patchlevel 17 (bug #241647).

* Wed Jul  4 2007 Tim Waugh <twaugh@redhat.com> 3.2-10
- Clarification in the ulimit man page (bug #220657).

* Mon Feb 12 2007 Tim Waugh <twaugh@redhat.com> 3.2-9
- Rebuild to link with libtinfo instead of libncurses.

* Wed Feb  7 2007 Tim Waugh <twaugh@redhat.com> 3.2-8
- Avoid %%makeinstall (bug #225609).

* Tue Feb  6 2007 Tim Waugh <twaugh@redhat.com> 3.2-7
- Reinstated this change:
  - Post requires ncurses (bug #224567).
- Reverted this change:
  - Added triggers for install-info (bug #225609).

* Tue Feb  6 2007 Tim Waugh <twaugh@redhat.com> 3.2-6
- Reverted this change:
  - Post requires ncurses (bug #224567).

* Mon Feb  5 2007 Tim Waugh <twaugh@redhat.com> 3.2-5
- Added triggers for install-info (bug #225609).
- Use full path to utilities in scriptlets (bug #225609).
- Fix missing sh-bangs in example scripts (bug #225609).
- Post requires ncurses (bug #224567).
- Removed Prefix tag (bug #225609).
- Fixed BuildRoot tag (bug #225609).
- Removed trailing full-stop from summary (bug #225609).
- Spec file is now UTF-8 (bug #225609).
- Removed obsolete Obsoletes (bug #225609).
- Moved 'make check' to new 'check' section (bug #225609).
- Removed uses of RPM_SOURCE_DIR (bug #225609).
- Fixed macros in changelog (bug #225609).
- Changed tabs to spaces (bug #225609).

* Tue Jan 23 2007 Tim Waugh <twaugh@redhat.com> 3.2-4
- Slightly better .bash_logout (bug #223960).

* Fri Jan 19 2007 Tim Waugh <twaugh@redhat.com> 3.2-3
- Back out rmatch change introduced in 3.2 (bug #220087).

* Tue Jan 16 2007 Miroslav Lichvar <mlichvar@redhat.com> 3.2-2
- Link with ncurses.

* Fri Dec 15 2006 Tim Waugh <twaugh@redhat.com> 3.2-1
- Build requires autoconf and gettext.
- 3.2.  No longer need aq, login, ulimit, sighandler or read-memleak
  patches.

* Wed Jul 12 2006 Tim Waugh <twaugh@redhat.com> 3.1-17
- Fixed 'tags out of date' problem with 'info bash' (bug #150118).

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 3.1-16.1
- rebuild

* Wed Jun 28 2006 Tim Waugh <twaugh@redhat.com> 3.1-16
- Removed 'unset USERNAME' from default .bash_profile (bug #196735).

* Thu Jun 15 2006 Tim Waugh <twaugh@redhat.com> 3.1-15
- Updated requires patch to the ALT version.

* Wed May 31 2006 Tim Waugh <twaugh@redhat.com> 3.1-14
- More sighandler fixes, this time hypothetical.

* Thu May 26 2006 Tim Waugh <twaugh@redhat.com> 3.1-13
- Another fix for the sighandler patch (bug #192297).

* Thu Apr 13 2006 Tim Waugh <twaugh@redhat.com> 3.1-12
- Patchlevel 17.

* Tue Apr  4 2006 Tim Waugh <twaugh@redhat.com> 3.1-11
- Patchlevel 16.

* Thu Mar 23 2006 Tim Waugh <twaugh@redhat.com> 3.1-10
- Patchlevel 14.

* Thu Mar  2 2006 Tim Waugh <twaugh@redhat.com> 3.1-9
- Fixed duplicate documentation of ulimit '-x' option introduced by
  ulimit patch (bug #183596).

* Tue Feb 21 2006 Tim Waugh <twaugh@redhat.com> 3.1-8
- Patchlevel 10.

* Thu Feb 16 2006 Tim Waugh <twaugh@redhat.com> 3.1-7
- Patchlevel 8.

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 3.1-6.2
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 3.1-6.1
- rebuilt for new gcc4.1 snapshot and glibc changes

* Sun Feb  5 2006 Tim Waugh <twaugh@redhat.com> 3.1-6
- Patchlevel 7.

* Wed Jan 18 2006 Tim Waugh <twaugh@redhat.com>
- Removed inaccuracies from %%description (bug #178189).

* Fri Jan 13 2006 Tim Waugh <twaugh@redhat.com> 3.1-5
- Fix 'exec -l /bin/bash'.

* Thu Jan 12 2006 Tim Waugh <twaugh@redhat.com> 3.1-4
- Fix sighandler patch bug (bug #177545).

* Tue Jan 10 2006 Tim Waugh <twaugh@redhat.com> 3.1-3
- Patchlevel 5.

* Fri Jan  6 2006 Tim Waugh <twaugh@redhat.com> 3.1-2
- No longer need loadables, mbinc or shellfunc patches.
- Use literal single-quote in bash man page where appropriate (bug #177051).

* Mon Jan  2 2006 Tim Waugh <twaugh@redhat.com> 3.1-1
- 3.1.
- No longer need ia64, utf8, multibyteifs, jobs, sigpipe,
  read-e-segfault, manpage, crash, pwd, afs, subshell patches.
- Remove wrap patch for now.
- Use upstream patch to fix arrays.

* Thu Dec 15 2005 Tim Waugh <twaugh@redhat.com> 3.0-41
- Missed another loop for improved sighandler patch (bug #169231).

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Thu Dec  8 2005 Tim Waugh <twaugh@redhat.com> 3.0-40
- Fix read memleak when reading from non-blocking fd (bug #173283).
- Missed another loop for improved sighandler patch (bug #169231).

* Wed Dec  7 2005 Tim Waugh <twaugh@redhat.com> 3.0-39
- Missed a loop for improved sighandler patch (bug #169231).

* Tue Dec  6 2005 Tim Waugh <twaugh@redhat.com> 3.0-38
- Test out improved sighandler patch (bug #169231).

* Tue Nov 22 2005 Tim Waugh <twaugh@redhat.com> 3.0-37
- Applied patch from upstream to fix parsing problem (bug #146638).

* Wed Nov  9 2005 Tim Waugh <twaugh@redhat.com> 3.0-36
- Added Url: tag (bug #172770).
- Do not explicitly gzip info pages (bug #172770).
- Fix permissions on bashbug (bug #172770).

* Thu Oct  6 2005 Tim Waugh <twaugh@redhat.com> 3.0-35
- Fixed memory allocation bug in multibyteifs patch (bug #169996).

* Fri Sep 23 2005 Tim Waugh <twaugh@redhat.com>
- Use 'volatile' in sighandler patch.

* Wed Sep 21 2005 Tim Waugh <twaugh@redhat.com> 3.0-34
- Avoid writing history files during signal handling (bug #163235).

* Mon Aug  8 2005 Tim Waugh <twaugh@redhat.com> 3.0-33
- Fixed multibyte IFS handling for invalid input (bug #165243).

* Mon Aug  8 2005 Tim Waugh <twaugh@redhat.com> 3.0-32
- Fixed 'LC_ALL=C export LC_ALL' behaviour (bug #165249).

* Thu Jun 23 2005 Tim Waugh <twaugh@redhat.com>
- Added ulimit support for RLIMIT_NICE and RLIMIT_RTPRIO (bug #157049).

* Wed Jun  8 2005 Tim Waugh <twaugh@redhat.com>
- Move a comment in dot-bashrc (bug #159522).

* Tue May 10 2005 Tim Waugh <twaugh@redhat.com> 3.0-31
- Small fix for multibyteifs patch to prevent segfault (bug #157260).

* Wed Apr 20 2005 Tim Waugh <twaugh@redhat.com>
- Fixed AFS support for output redirection, so that the correct errors
  are reported for other filesystems (bug #155373).

* Tue Mar 15 2005 Tim Waugh <twaugh@redhat.com> 3.0-30
- Fix PS1 expansion crash when PWD is unset (bg #151116).

* Wed Mar  2 2005 Tim Waugh <twaugh@redhat.com> 3.0-29
- Rebuild for new GCC.

* Thu Feb 17 2005 Tim Waugh <twaugh@redhat.com> 3.0-28
- Define _GNU_SOURCE in CPPFLAGS (bug #147573).

* Mon Feb 14 2005 Tim Waugh <twaugh@redhat.com>
- Reverted this change:
  - Added code to /etc/skel/.bash_logout to support the gpm selection buffer
    invalidation on virtual terminals (bug #115493).

* Mon Jan 31 2005 Tim Waugh <twaugh@redhat.com> 3.0-27
- Applied upstream patch to fix a potential NULL dereference.

* Fri Jan 28 2005 Tim Waugh <twaugh@redhat.com> 3.0-26
- Fixed job handling bug (bug #145124).

* Sun Dec  5 2004 Tim Waugh <twaugh@redhat.com> 3.0-25
- Applied patch from Florian La Roche to fix CPPFLAGS quoting in spec file.

* Tue Nov 30 2004 Tim Waugh <twaugh@redhat.com>
- Fixed typo in man page (spotted on bug-bash).

* Thu Nov 18 2004 Tim Waugh <twaugh@redhat.com> 3.0-24
- Use upstream patch to fix bug #139575 and bug #139306.

* Thu Nov 18 2004 Tim Waugh <twaugh@redhat.com> 3.0-23
- Fixed last patch to avoid regressions (bug #139575).

* Mon Nov 15 2004 Tim Waugh <twaugh@redhat.com> 3.0-22
- Fixed prompt wrapping code to cope with zero-length prompts (bug #139306).

* Thu Nov 11 2004 Tim Waugh <twaugh@redhat.com> 3.0-21
- Added code to /etc/skel/.bash_logout to support the gpm selection buffer
  invalidation on virtual terminals (bug #115493).

* Wed Nov 10 2004 Tim Waugh <twaugh@redhat.com> 3.0-20
- Patchlevel 16.

* Mon Nov  1 2004 Tim Waugh <twaugh@redhat.com>
- Patchlevel 15.

* Tue Oct 19 2004 Tim Waugh <twaugh@redhat.com> 3.0-17
- Patchlevel 14.
- No longer need brace patch.

* Wed Sep 29 2004 Tim Waugh <twaugh@redhat.com> 3.0-16
- Apply patch from Chet Ramey to fix brace expansion.

* Fri Sep 24 2004 Tim Waugh <twaugh@redhat.com> 3.0-15
- Minor fix for job handling.

* Mon Sep 13 2004 Tim Waugh <twaugh@redhat.com>
- Add bashbug back in (with suffix).

* Mon Sep 13 2004 Tim Waugh <twaugh@redhat.com>
- Remove bash2.

* Fri Sep 10 2004 Tim Waugh <twaugh@redhat.com> 3.0-14
- Don't run tests that read from /dev/tty.
- Patchlevel 13.

* Wed Sep  8 2004 Tim Waugh <twaugh@redhat.com> 3.0-13
- Check for EINVAL from waitpid() and avoid WCONTINUED in that case.
- Fixed jobs4 test.
- Applied experimental upstream patch for trap compatibility.
- Re-make documentation to reflect source changes.

* Tue Sep  7 2004 Tim Waugh <twaugh@redhat.com> 3.0-12
- Remove 'bashbug' from the documentation, because we don't ship it due
  to biarch concerns.

* Thu Sep  2 2004 Tim Waugh <twaugh@redhat.com> 3.0-11
- Fixed multibyte parameter length expansion.

* Tue Aug 31 2004 Tim Waugh <twaugh@redhat.com> 3.0-9
- Fix ulimits patch from Ulrich Drepper (bug #129800).

* Fri Aug 27 2004 Tim Waugh <twaugh@redhat.com> 3.0-8
- Provide support for new limits (bug #129800).

* Thu Aug 26 2004 Tim Waugh <twaugh@redhat.com> 3.0-7
- Use upstream patch for last fix.

* Thu Aug 26 2004 Tim Waugh <twaugh@redhat.com> 3.0-6
- Fixed history saved-line handling.

* Tue Aug 24 2004 Tim Waugh <twaugh@redhat.com>
- Fixed multibyte IFS handling.

* Wed Aug 18 2004 Tim Waugh <twaugh@redhat.com>
- Applied bug-bash list patch to fix pipefail.

* Tue Aug 17 2004 Tim Waugh <twaugh@redhat.com> 3.0-5
- Make trap usage string show POSIX usage (bug #128938).
- Updated ${x[@]:1} expansion fix from bug-bash list.
- Updated patch to fix unset array crash (from bug-bash list).

* Sun Aug 15 2004 Tim Waugh <twaugh@redhat.com>
- Fix ${x[@]:1} expansion (William Park, bug-bash list).

* Tue Aug 10 2004 Tim Waugh <twaugh@redhat.com> 3.0-4
- Fix vi-change-char behaviour at EOL (bug #129526).

* Mon Aug  9 2004 Tim Waugh <twaugh@redhat.com> 3.0-3
- Applied bug-bash list patch to fix multiline PS1 prompting (bug #129382).

* Wed Aug  4 2004 Tim Waugh <twaugh@redhat.com> 3.0-2
- Fixed brace expansion (bug #129128).
- Build with AFS support again, since bug #86514 seems fixed upstream
  (bug #129094).

* Tue Aug  3 2004 Tim Waugh <twaugh@redhat.com>
- Fixed crash when unsetting an unset array (from bug-bash list).

* Wed Jul 28 2004 Tim Waugh <twaugh@redhat.com> 3.0-1
- 3.0.

* Wed Jul 21 2004 Tim Waugh <twaugh@redhat.com> 2.05b-44
- Don't report SIGPIPE errors (bug #128274).

* Thu Jul  8 2004 Tim Waugh <twaugh@redhat.com> 2.05b-43
- Fixed command substitution problem (bug #127242).

* Mon Jun 28 2004 Tim Waugh <twaugh@redhat.com> 2.05b-42
- Fixed multibyte variable substitution patch (bug #126399).

* Thu Jun 17 2004 Karsten Hopp <karsten@redhat.de> 2.05b-41 
- remove bashbug script/docs to avoid conflicting files in
  biarch installs.

* Tue Jun 15 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Fri Jun  4 2004 Tim Waugh <twaugh@redhat.com>
- Build requires bison (bug #125307).

* Wed Jun  2 2004 Tim Waugh <twaugh@redhat.com> 2.05b-39
- Build requires libtermcap-devel (bug #125068).

* Wed May 19 2004 Tim Waugh <twaugh@redhat.com>
- Don't ship empty %%{_libdir}/bash (bug #123556).

* Thu Mar 11 2004 Tim Waugh <twaugh@redhat.com> 2.05b-38
- Apply patch from Nalin Dahyabhai fixing an overread.

* Tue Mar 02 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Fri Feb 13 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Thu Jan 22 2004 Tim Waugh <twaugh@redhat.com> 2.05b-36
- Fix the bug causing bindings to need reparsing .inputrc (bug #114101).

* Mon Jan  5 2004 Tim Waugh <twaugh@redhat.com> 2.05b-35
- Fix parameter expansion in multibyte locales (bug #112657).
- Run 'make check'.

* Tue Dec  9 2003 Tim Waugh <twaugh@redhat.com> 2.05b-34
- Build requires texinfo (bug #111171).

* Fri Nov 28 2003 Tim Waugh <twaugh@redhat.com> 2.05b-33
- Speed up UTF-8 command-line redrawing in the common case (bug #102353,
  bug #110777).

* Thu Nov  6 2003 Tim Waugh <twaugh@redhat.com> 2.05b-32
- Apply upstream patches (bug #109269 among others).

* Fri Oct 31 2003 Tim Waugh <twaugh@redhat.com>
- Fix bash.info (bug #83776).

* Tue Oct 28 2003 Tim Waugh <twaugh@redhat.com> 2.05b-31
- Add bash205b-007 patch to fix bug #106876.

* Thu Oct 23 2003 Tim Waugh <twaugh@redhat.com> 2.05b-30
- Rebuilt.

* Thu Sep 18 2003 Tim Waugh <twaugh@redhat.com> 2.05b-29.1
- Rebuilt.

* Thu Sep 18 2003 Tim Waugh <twaugh@redhat.com> 2.05b-29
- Avoid crashing on multibyte input when locale is set incorrectly
  (bug #74266).

* Fri Sep  5 2003 Tim Waugh <twaugh@redhat.com> 2.05b-28.1
- Rebuilt.

* Fri Sep  5 2003 Tim Waugh <twaugh@redhat.com> 2.05b-28
- Avoid built-in malloc implementation (bug #103768).

* Wed Sep  3 2003 Tim Waugh <twaugh@redhat.com> 2.05b-27.1
- Rebuilt.

* Wed Sep  3 2003 Tim Waugh <twaugh@redhat.com> 2.05b-27
- LFS support (bug #103627).

* Thu Jul 31 2003 Tim Waugh <twaugh@redhat.com> 2.05b-26.1
- Rebuilt.

* Thu Jul 31 2003 Tim Waugh <twaugh@redhat.com> 2.05b-26
- Merge bash-doc into main package (bug #100632).

* Wed Jun 04 2003 Elliot Lee <sopwith@redhat.com> 2.05b-25
- rebuilt

* Mon May 12 2003 Tim Waugh <twaugh@redhat.com> 2.05b-24
- Fix completion display when multibyte or control characters are to be
  shown (bug #90201).

* Tue Mar 26 2003 Tim Waugh <twaugh@redhat.com> 2.05b-23
- Fix a warning message (bug #79629).
- Don't remove generated source during build, for debuginfo package.
- Don't build with AFS support (bug #86514).

* Tue Mar 25 2003 Tim Waugh <twaugh@redhat.com> 2.05b-22
- Really fix bug #78455.

* Tue Mar 11 2003 Tim Waugh <twaugh@redhat.com> 2.05b-21
- Don't explicitly strip binaries (bug #85995).

* Tue Feb 11 2003 Tim Waugh <twaugh@redhat.com> 2.05b-20
- Really fix bug #83331 for good.

* Mon Feb 10 2003 Tim Waugh <twaugh@redhat.com> 2.05b-19
- Fix builtins.1.

* Fri Feb  7 2003 Tim Waugh <twaugh@redhat.com> 2.05b-18
- Actually apply the patch (bug #83331).

* Wed Feb  5 2003 Tim Waugh <twaugh@redhat.com> 2.05b-17
- Fix history/UTF-8 bug (bug #83331).

* Sun Jan 26 2003 Tim Waugh <twaugh@redhat.com> 2.05b-16
- More tab-completion fixing (bug #72512).

* Wed Jan 22 2003 Tim Powers <timp@redhat.com> 2.05b-15
- rebuilt

* Wed Jan 15 2003 Tim Waugh <twaugh@redhat.com> 2.05b-14
- Force pgrp synchronization (bug #81653).

* Thu Dec 05 2002 Elliot Lee <sopwith@redhat.com> 2.05b-13
- (patch26) Don't call 'size' in makefile. Pointless, and interferes with 
  cross compiles.

* Tue Dec  3 2002 Tim Waugh <twaugh@redhat.com> 2.05b-12
- Prevent prompt overwriting output (bug #74383).

* Wed Nov 27 2002 Tim Waugh <twaugh@redhat.com> 2.05b-11
- Fix '-rbash' (bug #78455).

* Thu Nov 21 2002 Tim Waugh <twaugh@redhat.com> 2.05b-10
- Rebuild.

* Wed Nov 20 2002 Elliot Lee <sopwith@redhat.com>
- Use the configure macro instead of calling ./configure directly

* Wed Nov 13 2002 Tim Waugh <twaugh@redhat.com>
- Revert previous change.

* Wed Nov 13 2002 Tim Waugh <twaugh@redhat.com> 2.05b-8
- PreReq libtermcap.

* Fri Oct 18 2002 Tim Waugh <twaugh@redhat.com> 2.05b-7
- Add readline-init patch (bug #74925).

* Wed Oct 16 2002 Tim Waugh <twaugh@redhat.com> 2.05b-6
- Add the (4) patches from ftp.gnu.org (bug #75888, bug #72512).
- Ship '.' man page, which doesn't get picked up by glob.
- Don't install files not shipped when building.
- Locale shell variables fix (bug #74701).

* Fri Aug 23 2002 Tim Powers <timp@redhat.com> 2.05b-5
- re-bzip the docs, something was corrupted

* Thu Aug 22 2002 Tim Waugh <twaugh@redhat.com> 2.05b-4
- Fix history substitution modifiers in UTF-8 (bug #70294, bug #71186).
- Fix ADVANCE_CHAR at end of string (bug #70819).
- docs: CWRU/POSIX.NOTES no longer exists, but ship POSIX.

* Wed Aug 07 2002 Phil Knirsch <pknirsch@redhat.com> 2.05b-3
- Fixed out of memory problem with readline.

* Tue Jul 23 2002 Phil Knirsch <pknirsch@redhat.com> 2.05b-2
- Added symlink for sh.1 in man1 section so that man sh works (#44039).

* Mon Jul 22 2002 Phil Knirsch <pknirsch@redhat.com> 2.05b-1
- Update to 2.05b

* Wed Jul 10 2002 Phil Knirsch <pknirsch@redhat.com> 2.05a-16
- Fixed readline utf8 problem (#68313).

* Fri Jun 21 2002 Tim Powers <timp@redhat.com> 2.05a-15
- automated rebuild

* Thu May 23 2002 Tim Powers <timp@redhat.com> 2.05a-14
- automated rebuild

* Fri Apr 12 2002 Tim Powers <timp@redhat.com> 2.05a-13
- don't build the stuff in examples/loadables. It breaks FHS
  compliance

* Fri Apr  5 2002 Bernhard Rosenkraenzer <bero@redhat.com> 2.05a-12
- Fix the fix for #62418

* Thu Apr  4 2002 Bernhard Rosenkraenzer <bero@redhat.com> 2.05a-11
- Fix kill builtin (#62418)

* Mon Mar 25 2002 Trond Eivind Glomsrød <teg@redhat.com> 2.0.5a-10
- Get rid of completion subpackage
- Use %%{_tmppath}

* Mon Mar 11 2002 Bernhard Rosenkraenzer <bero@redhat.com> 2.05a-9
- Add patch from Ulrich Drepper to get better error messages when trying
  to launch an application with a bad ELF interpreter (e.g. libc5 ld.so)
  (#60870)

* Fri Feb 22 2002 Bernhard Rosenkraenzer <bero@redhat.com> 2.05a-8
- Update completion

* Wed Jan 30 2002 Bernhard Rosenkraenzer <bero@redhat.com> 2.05a-7
- Update completion stuff and move it to a separate package

* Sat Jan 26 2002 Bernhard Rosenkraenzer <bero@redhat.com> 2.05a-6
- Add patches from Ian Macdonald <ian@caliban.org>

* Wed Jan 23 2002 Bernhard Rosenkraenzer <bero@redhat.com> 2.05a-5
- Add programmable completion (optional)

* Thu Jan 17 2002 Bernhard Rosenkraenzer <bero@redhat.com> 2.05a-4
- Fix mailcheck (#57792)

* Tue Jan 15 2002 Bernhard Rosenkraenzer <bero@redhat.com> 2.05a-3
- Fix autoconf mess
- Build --with-afs, some users may be using it

* Wed Jan 09 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Thu Nov 22 2001 Bernhard Rosenkraenzer <bero@redhat.com> 2.05a-2
- Fix conflict with sh-utils (printf builtin manpage vs. printf binary manpage)
  (#56590)

* Tue Nov 20 2001 Bernhard Rosenkraenzer <bero@redhat.com> 2.05a-1
- 2.05a

* Wed Oct 10 2001 Florian La Roche <Florian.LaRoche@redhat.de>
- disable s390x fix, not needed anymore

* Mon Oct  1 2001 Bernhard Rosenkraenzer <bero@redhat.com> 2.05-9
- Add patch from readline 4.2-3 to bash's internal libreadline

* Mon Jul  9 2001 Bernhard Rosenkraenzer <bero@redhat.com> 2.05-8
- Merge Pekka Savola's patch (RFE#47762)

* Mon Jul  2 2001 Pekka Savola <pekkas@netcore.fi>
- Add IPv6 patch from PLD (only redirection to /dev/{tcp,udp}/host/port
  support)

* Sun Jun 24 2001 Bernhard Rosenkraenzer <bero@redhat.com> 2.05-7
- Add some bugfix patches from the maintainer

* Mon Jun 11 2001 Florian La Roche <Florian.LaRoche@redhat.de>
- added patch for s390x from <oliver.paukstadt@millenux.com>

* Wed May 23 2001 Bernhard Rosenkraenzer <bero@redhat.com> 2.05-5
- Don't set BASH_ENV in .bash_profile, it causes .bashrc to be sourced
  twice in interactive non-login shells.
- s/Copyright/License/

* Fri May  5 2001 Bernhard Rosenkraenzer <bero@redhat.com> 2.05-4
- Fix tempfile creation in bashbug

* Wed May  2 2001 Preston Brown <pbrown@redhat.com> 2.05-3
- bashrc moved to setup package

* Tue Apr 24 2001 Bernhard Rosenkraenzer <bero@redhat.com> 2.05-2
- bash comes with its own copy of readline... Add the patches we're
  applying in the readline package.

* Tue Apr 24 2001 Bernhard Rosenkraenzer <bero@redhat.com> 2.05-1
- Update to 2.05
- Change PROMPT_COMMAND in bashrc for xterms
  to something less space consuming (#24159)
- Provide plugs for alternate prompt commands (#30634), but don't
  default to them

* Mon Mar 19 2001 Preston Brown <pbrown@redhat.com>
- add default aliases for 'dir' and 'df' to have human readable output

* Wed Feb 28 2001 Matt Wilson <msw@redhat.com>
- don't Prereq: /sbin/install-info!

* Tue Feb 27 2001 Preston Brown <pbrown@redhat.com>
- noreplace config files
- don't own /etc/skel directory

* Wed Feb 22 2001 Harald Hoyer <harald@redhat.de>
- changed /etc/bashrc to work with backspace = 0177 (rxvt)

* Wed Feb 07 2001 Florian La Roche <Florian.LaRoche@redhat.de>
- changed /etc/skel/.bash_profile to "unset USERNAME"

* Mon Feb  5 2001 Yukihiro Nakai <ynakai@redhat.com>
- Delete Japanese resources from dot-bashrc
  and move them to each package.

* Fri Dec 15 2000 Yukihiro Nakai <ynakai@redhat.com>
- Add Japanese resource to dot-bashrc

* Mon Dec 11 2000 Bernhard Rosenkraenzer <bero@redhat.com>
- rebuild to get rid of 0777 doc dirs

* Thu Nov 16 2000 Bernhard Rosenkraenzer <bero@redhat.com>
- restore the ^Hs in documentation, they're highlighting sequences
  for less (#20654) 

* Fri Sep 15 2000 Florian La Roche <Florian.LaRoche@redhat.de>
- bash-2.04-export.patch is reported to fix compilation
  of older glibc-2.1 sources

* Tue Aug 22 2000 Matt Wilson <msw@redhat.com>
- fixed the summary of bash-doc to use %%{version} instead of "2.03"

* Tue Aug  8 2000 Bill Nottingham <notting@redhat.com>
- 'exit' in bashrc is very bad.

* Tue Aug  8 2000 Bernhard Rosenkraenzer <bero@redhat.com>
- minor bashrc fix (Bug #8518)

* Mon Jul 17 2000 Bernhard Rosenkraenzer <bero@redhat.com>
- Don't use tput etc. in bashrc if /usr isn't available (Bug #14116)

* Wed Jul 12 2000 Prospector <bugzilla@redhat.com>
- automatic rebuild

* Thu Jun 22 2000 Bill Nottingham <notting@redhat.com>
- fix for some IA-64 issues from Stephane Eranian

* Thu Jun 15 2000 Bernhard Rosenkraenzer <bero@redhat.com>
- Fix summary and description, they had old version numbers (Bug #12092)

* Tue Jun  6 2000 Bill Nottingham <notting@redhat.com>
- add /etc/skel/.bash* ; obsolete etcskel

* Tue May  2 2000 Bill Nottingham <notting@redhat.com>
- fix for shell functions on 64-bit architectures...

* Wed Mar 29 2000 Bernhard Rosenkraenzer <bero@redhat.com>
- Add some backwards compatibility (for i in ; do something; done)

* Tue Mar 21 2000 Bernhard Rosenkraenzer <bero@redhat.com>
- 2.04 final
- remove the echo, pwd, test and kill man pages from the package,
  we're getting them from sh-utils

* Sun Mar 19 2000 Bernhard Rosenkraenzer <bero@redhat.com>
- 2.04beta5
- adapt patches
- Fix up bashrc
- Don't put in bashrc1, this should be done by the bash1 package
- use install -c instead of plain install to work on *BSD
- remove the collected patches - they're now in the base version.
- make compressed man pages optional

* Thu Mar 16 2000 Florian La Roche <Florian.LaRoche@redhat.com>
- add some collected patches for bash2
- change it over to be the main bash package
- install man-pages root:root
- obsolete bash2, bash2-doc

* Wed Feb 02 2000 Cristian Gafton <gafton@redhat.com>
- man pages are compressed
- fix description

* Thu Dec  2 1999 Ken Estes <kestes@staff.mail.com>
- updated patch to detect what executables are required by a script.

* Fri Sep 14 1999 Dale Lovelace <dale@redhat.com>
- Remove annoying ^H's from documentation

* Fri Jul 16 1999 Ken Estes <kestes@staff.mail.com>
- patch to detect what executables are required by a script.

* Sun Mar 21 1999 Cristian Gafton <gafton@redhat.com> 
- auto rebuild in the new build environment (release 4)

* Fri Mar 19 1999 Jeff Johnson <jbj@redhat.com>
- strip binaries.
- include bash-doc correctly.

* Thu Mar 18 1999 Preston Brown <pbrown@redhat.com>
- fixed post/postun /etc/shells work.

* Thu Mar 18 1999 Cristian Gafton <gafton@redhat.com>
- updated again text in the spec file

* Mon Feb 22 1999 Jeff Johnson <jbj@redhat.com>
- updated text in spec file.
- update to 2.03.

* Fri Feb 12 1999 Cristian Gafton <gafton@redhat.com>
- build it as bash2 instead of bash

* Tue Feb  9 1999 Bill Nottingham <notting@redhat.com>
- set 'NON_INTERACTIVE_LOGIN_SHELLS' so profile gets read

* Thu Jan 14 1999 Jeff Johnson <jbj@redhat.com>
- rename man pages in bash-doc to avoid packaging conflicts (#606).

* Wed Dec 02 1998 Cristian Gafton <gafton@redhat.com>
- patch for the arm
- use $RPM_ARCH-redhat-linux as the build target

* Tue Oct  6 1998 Bill Nottingham <notting@redhat.com>
- rewrite %%pre, axe %%postun (to avoid prereq loops)

* Wed Aug 19 1998 Jeff Johnson <jbj@redhat.com>
- resurrect for RH 6.0.

* Sun Jul 26 1998 Jeff Johnson <jbj@redhat.com>
- update to 2.02.1

* Thu Jun 11 1998 Jeff Johnson <jbj@redhat.com>
- Package for 5.2.

* Mon Apr 20 1998 Ian Macdonald <ianmacd@xs4all.nl>
- added POSIX.NOTES doc file
- some extraneous doc files removed
- minor .spec file changes

* Sun Apr 19 1998 Ian Macdonald <ianmacd@xs4all.nl>
- upgraded to version 2.02
- Alpha, MIPS & Sparc patches removed due to lack of test platforms
- glibc & signal patches no longer required
- added documentation subpackage (doc)

* Fri Nov 07 1997 Donnie Barnes <djb@redhat.com>
- added signal handling patch from Dean Gaudet <dgaudet@arctic.org> that
  is based on a change made in bash 2.0.  Should fix some early exit
  problems with suspends and fg.

* Mon Oct 20 1997 Donnie Barnes <djb@redhat.com>
- added %%clean

* Mon Oct 20 1997 Erik Troan <ewt@redhat.com>
- added comment explaining why install-info isn't used
- added mips patch 

* Fri Oct 17 1997 Donnie Barnes <djb@redhat.com>
- added BuildRoot

* Tue Jun 03 1997 Erik Troan <ewt@redhat.com>
- built against glibc
