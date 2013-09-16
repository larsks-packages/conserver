Name:           conserver
Version:        8.1.18
Release:        9%{?dist}
Summary:        Serial console server daemon/client

Group:          System Environment/Daemons
License:        BSD with advertising and zlib
URL:            http://www.conserver.com/
Source0:        http://www.conserver.com/%{name}-%{version}.tar.gz
Source1:	%{name}.service
Patch0:         %{name}-no-exampledir.patch
#Patch1:         %{name}-initscript.patch
Patch2:         %{name}-gssapi.patch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  pam-devel, openssl-devel, tcp_wrappers-devel, krb5-devel
BuildRequires:  autoconf, automake, systemd-units
Requires(post): systemd-units
Requires(preun): systemd-units
Requires(postun): systemd-units

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
#%patch1 -p1
%patch2 -p1

%build
# we don't want to install the solaris conserver.rc file
f="conserver/Makefile.in"
%{__mv} $f $f.orig
%{__sed} -e 's/^.*conserver\.rc.*$//' < $f.orig > $f

autoreconf -f -i

%configure --with-libwrap \
        --with-openssl \
        --with-pam \
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
#%{__mkdir_p} $RPM_BUILD_ROOT/%{_initrddir}
#%{__cp} contrib/redhat-rpm/conserver.init $RPM_BUILD_ROOT/%{_initrddir}/conserver
install -D -m 644 %{SOURCE1} $RPM_BUILD_ROOT%{_unitdir}/conserver.service


%clean
rm -rf $RPM_BUILD_ROOT

%post
if [ $1 -eq 1 ] ; then 
    # Initial installation 
    /bin/systemctl daemon-reload >/dev/null 2>&1 || :
fi

%preun
if [ $1 -eq 0 ] ; then
    # Package removal, not upgrade
    /bin/systemctl --no-reload disable conserver.service > /dev/null 2>&1 || :
    /bin/systemctl stop conserver.service > /dev/null 2>&1 || :
fi

%postun
/bin/systemctl daemon-reload >/dev/null 2>&1 || :
if [ $1 -ge 1 ] ; then
    # Package upgrade, not uninstall
    /bin/systemctl try-restart conserver.service >/dev/null 2>&1 || :
fi

%triggerun -- conserver < 8.1.18-5
# Save the current service runlevel info
# User must manually run systemd-sysv-convert --apply conserver
# to migrate them to systemd targets
/usr/bin/systemd-sysv-convert --save conserver >/dev/null 2>&1 ||:

# Run these because the SysV package being removed won't do them
/sbin/chkconfig --del conserver >/dev/null 2>&1 || :
/bin/systemctl try-restart conserver.service >/dev/null 2>&1 || :

%files
%defattr(-,root,root,-)
%doc CHANGES FAQ LICENSE INSTALL README conserver.cf/samples/ conserver.cf/conserver.cf conserver.cf/conserver.passwd
%config(noreplace) %{_sysconfdir}/conserver.*
%{_unitdir}/conserver.service
%{_libdir}/conserver
%{_mandir}/man5/conserver.cf.5.gz
%{_mandir}/man5/conserver.passwd.5.gz
%{_mandir}/man8/conserver.8.gz
%{_sbindir}/conserver

%files client
%defattr(-,root,root,-)
%doc LICENSE
%{_bindir}/console
%{_mandir}/man1/console.1.gz

%changelog
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
