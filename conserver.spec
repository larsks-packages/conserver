Name:           conserver
Version:        8.1.14
Release:        4%{?dist}
Summary:        Serial console server daemon/client

Group:          System Environment/Daemons
License:        Distributable
URL:            http://www.conserver.com/
Source0:        http://www.conserver.com/%{name}-%{version}.tar.gz
Patch0:         http://beer.tclug.org/fedora-extras/%{name}/%{name}-%{version}-no-exampledir.patch
Patch1:         http://beer.tclug.org/fedora-extras/%{name}/%{name}-%{version}-initscript.patch
Patch2:         http://beer.tclug.org/fedora-extras/%{name}/%{name}-%{version}-oldkrb.patch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

BuildRequires:  pam-devel, openssl-devel, tcp_wrappers
Requires(post): /sbin/chkconfig
Requires(preun): /sbin/chkconfig
Requires(preun): /sbin/service

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
%patch2 -p1


%build
# we don't want to install the solaris conserver.rc file
f="conserver/Makefile.in"
%{__mv} $f $f.orig
%{__sed} -e 's/^.*conserver\.rc.*$//' < $f.orig > $f

%configure --with-libwrap \
	--with-openssl \
	--with-pam

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
%{__mkdir_p} $RPM_BUILD_ROOT/%{_initrddir}
%{__cp} contrib/redhat-rpm/conserver.init $RPM_BUILD_ROOT/%{_initrddir}/conserver


%clean
rm -rf $RPM_BUILD_ROOT

%post
if [ -x %{_initrddir}/conserver ]; then
  /sbin/chkconfig --add conserver
fi
# make sure /etc/services has a conserver entry
if ! egrep '\<conserver\>' /etc/services > /dev/null 2>&1 ; then
  echo "console		782/tcp		conserver" >> /etc/services
fi

%post client
# make sure /etc/services has a conserver entry
if ! egrep '\<conserver\>' /etc/services > /dev/null 2>&1 ; then
  echo "console		782/tcp		conserver" >> /etc/services
fi


%preun
if [ "$1" = 0 ]; then
  if [ -x %{_initrddir}/conserver ]; then
    %{_initrddir}/conserver stop > /dev/null 2>&1
    /sbin/chkconfig --del conserver
  fi
fi


%files
%defattr(-,root,root,-)
%doc CHANGES FAQ LICENSE INSTALL README conserver.cf/samples/ conserver.cf/conserver.cf conserver.cf/conserver.passwd
%config(noreplace) %{_sysconfdir}/conserver.*
%{_initrddir}/conserver
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
