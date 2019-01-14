%if 0%{?fedora} >= 27 || 0%{?rhel} > 7
%define use_libwrap 0
%else
%define use_libwrap 1
%endif

%if 0%{?fedora} || 0%{?rhel} >= 7
%define use_systemd 1
%else
%define use_systemd 0
%endif

Name:           conserver
Version:        8.2.2
Release:        2%{?dist}
Summary:        Serial console server daemon/client

Group:          System Environment/Daemons
License:        BSD with advertising and zlib
URL:            http://www.conserver.com/
Source0:        http://www.conserver.com/%{name}-%{version}.tar.gz
Source1:	%{name}.service
Patch0:         %{name}-no-exampledir.patch
Patch1:         %{name}-gssapi.patch
%if !%{use_systemd}
Patch2:         %{name}-initscript.patch
%endif

BuildRequires:  gcc
BuildRequires:  autoconf, automake, pam-devel, krb5-devel, freeipmi-devel

BuildRequires:  openssl-devel

%if %{use_libwrap}
BuildRequires:  tcp_wrappers-devel
%endif

%if %{use_systemd}
BuildRequires:  systemd
%{?systemd_requires}
%endif

%description
Conserver is an application that allows multiple users to watch a serial 
console at the same time.  It can log the data, allows users to take 
write-access of a console (one at a time), and has a variety of bells 
and whistles to accentuate that basic functionality.

%package client
Summary: Serial console client
Group: Applications/Communications

%description client
This is the client package needed to interact with a Conserver daemon.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%if !%{use_systemd}
%patch2 -p1
%endif

%build
%global _hardened_build 1
# we don't want to install the solaris conserver.rc file
f="conserver/Makefile.in"
%{__mv} $f $f.orig
%{__sed} -e 's/^.*conserver\.rc.*$//' < $f.orig > $f

autoreconf -f -i

%configure --with-openssl \
%if %{use_libwrap}
        --with-libwrap \
%endif
        --with-pam \
        --with-freeipmi \
        --with-gssapi \
        --with-striprealm \
        --with-port=782

make %{?_smp_mflags}


%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT

# put commented copies of the sample configure files in the
# system configuration directory
%{__mkdir_p} $RPM_BUILD_ROOT/%{_sysconfdir}
%{__sed} -e 's/^/#/' \
  < conserver.cf/conserver.cf \
  > $RPM_BUILD_ROOT/%{_sysconfdir}/conserver.cf
%{__sed} -e 's/^/#/' \
  < conserver.cf/conserver.passwd \
  > $RPM_BUILD_ROOT/%{_sysconfdir}/conserver.passwd

# install copy of init script
%if %{use_systemd}
%{__install} -D -m 644 %{SOURCE1} $RPM_BUILD_ROOT%{_unitdir}/conserver.service
%else
%{__install} -D contrib/redhat-rpm/conserver.init $RPM_BUILD_ROOT/%{_initrddir}/conserver
%endif

%clean

%post
%systemd_post

%preun
%systemd_preun

%postun
%systemd_postun

%files
%doc CHANGES FAQ LICENSE INSTALL README conserver.cf/samples/ conserver.cf/conserver.cf conserver.cf/conserver.passwd
%config(noreplace) %{_sysconfdir}/conserver.*
%if %{use_systemd}
%{_unitdir}/conserver.service
%else
%{_initrddir}/conserver
%endif
%{_libdir}/conserver
%{_mandir}/man5/conserver.cf.5.gz
%{_mandir}/man5/conserver.passwd.5.gz
%{_mandir}/man8/conserver.8.gz
%{_sbindir}/conserver

%files client
%doc LICENSE
%{_bindir}/console
%{_mandir}/man1/console.1.gz

%changelog
* Mon Jan 14 2019 Björn Esser <besser82@fedoraproject.org> - 8.2.2-2
- Rebuilt for libcrypt.so.2 (#1666033)

* Fri Jan  4 2019 Jiri Kastner - 8.2.2-1
- update to 8.2.2
- fixes openssl-1.1 build

* Thu Jul 12 2018 Fedora Release Engineering <releng@fedoraproject.org> - 8.2.1-10
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 8.2.1-9
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Sat Jan 20 2018 Björn Esser <besser82@fedoraproject.org> - 8.2.1-8
- Rebuilt for switch to libxcrypt

* Sun Dec 10 2017 Jiri Kastner - 8.2.1-7
- removed old systemd snippets and dependencies (BZ#850068)
- changed dependency on openssl to compat-openssl10 for newer fedoras (BZ#1423307)
- removed tcp_wrappers dependency (BZ#1518757)

* Wed Aug 02 2017 Fedora Release Engineering <releng@fedoraproject.org> - 8.2.1-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Binutils_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 8.2.1-5
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 8.2.1-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 8.2.1-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Wed Jun 17 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 8.2.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Wed Jun  3 2015 Jiri Kastner <jkastner (at) redhat (dot) com> - 8.2.1-1
- updated to 8.2.1 (BZ#1225592)

* Mon Jan 12 2015 Jiri Kastner <jkastner (at) redhat (dot) com> - 8.2.0-2
- hardening build (BZ#955327)

* Wed Jan  7 2015 Jiri Kastner <jkastner (at) redhat (dot) com> - 8.2.0-1
- updated to new release

* Sat Aug 16 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 8.1.20-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Sat Jun 07 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 8.1.20-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Mon Apr 14 2014 Jiri Kastner <jkastner (at) redhat (dot) com> - 8.1.20-1
- updated to new release
- added support for freeipmi (serial over lan)

* Mon Sep 16 2013 Jiri Kastner <jkastner (at) redhat (dot) com> - 8.1.18-9
- removed libgss*-devel build dependency

* Sat Aug 03 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 8.1.18-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Wed Feb 13 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 8.1.18-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Wed Jul 18 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 8.1.18-6
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Tue Apr 17 2012 Jon Ciesla <limburgher@gmail.com> - 8.1.18-5
- Migrate to systemd, BZ 771450.

* Thu Jan 12 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 8.1.18-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 8.1.18-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Mon Jan 31 2011 Patrick "Jima" Laughton <jima@beer.tclug.org> 8.1.18-2
- Paolo Bonzini advises --with-uds would be a Bad Thing; removed (thanks!)

* Tue Jan 25 2011 Patrick "Jima" Laughton <jima@beer.tclug.org> 8.1.18-1
- Updated to newer version for added Kerberos support (BZ#652688)
- Fixed BZ#466541
- Fixed broken tcp_wrappers support
- Enabled Unix Domain Socket support
- Removed upstream-adopted patches

* Fri Aug 21 2009 Tomas Mraz <tmraz@redhat.com> - 8.1.16-9
- rebuilt with new openssl

* Fri Jul 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 8.1.16-8
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Tue Feb 24 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 8.1.16-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_11_Mass_Rebuild

* Thu Jan 15 2009 Tomas Mraz <tmraz@redhat.com> 8.1.16-6
- rebuild with new openssl

* Wed Feb 13 2008 Patrick "Jima" Laughton <jima@beer.tclug.org> 8.1.16-5
- Bump-n-build for GCC 4.3

* Tue Dec 04 2007 Patrick "Jima" Laughton <jima@beer.tclug.org> 8.1.16-4
- Bump-n-build for openssl soname change

* Wed Aug 22 2007 Patrick "Jima" Laughton <jima@beer.tclug.org> 8.1.16-3
- License clarification

* Tue Aug 21 2007 Patrick "Jima" Laughton <jima@beer.tclug.org> 8.1.16-2
- Rebuild for BuildID

* Wed Apr 11 2007 Patrick "Jima" Laughton <jima@beer.tclug.org> 8.1.16-1
- New upstream release with "certainly important" bugfix
- Removed URLs from patch lines (it's all in CVS)
- Added patch to fix man page permissions (755 -> 644)
- rpmlint's "mixed-use-of-spaces-and-tabs" is mostly a false positive

* Wed Jan 03 2007 Patrick "Jima" Laughton <jima@beer.tclug.org> 8.1.15-1
- New upstream release
- Fix rpmlint warning about mixed spaces/tabs

* Mon Aug 28 2006 Patrick "Jima" Laughton <jima@beer.tclug.org> 8.1.14-4
- Rebuild for FC6

* Wed May 24 2006 Patrick "Jima" Laughton <jima@beer.tclug.org> 8.1.14-3
- Fix from Nate Straz: UDS support (pre-emptively fixed bug 192910)
- Fix from Nate Straz: krb detection

* Wed Apr 26 2006 Patrick "Jima" Laughton <jima@auroralinux.org> 8.1.14-2
- Split 'console' out to -client subpackage, as suggested by Nate Straz

* Mon Apr 10 2006 Patrick "Jima" Laughton <jima@auroralinux.org> 8.1.14-1
- Figures, two days after my initial Fedora Extras RPM, a new release...

* Fri Apr 07 2006 Patrick "Jima" Laughton <jima@auroralinux.org> 8.1.13-1
- Initial Fedora Extras RPM
- Added patch to disable /usr/share/examples/conserver -- non-standard
- Added patch to correct poorly written initscript
- Cleaned up what goes in /usr/share/doc/conserver-8.1.13/ (sloppy)
- Other .spec cleanups with lots of help from Dennis Gilmore (thanks!)
