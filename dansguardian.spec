#
# spec file for package dansguardian
#
# Copyright (c) 2013 SUSE LINUX Products GmbH, Nuernberg, Germany.
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

%define         dg_user  dansguardian
%define         dg_group vscan

Name:           dansguardian
Summary:        Content filtering web proxy
Version:        2.12.0.3
Release:        1.1%{?dist}
License:        GPL-2.0+
Group:          Productivity/Networking/Web/Proxy
Url:            http://www.dansguardian.org/
Source0:        %{name}-%{version}.tar.bz2
Source1:        %{name}.init
Source3:        %{name}.logrotate
Source4:        %{name}.init-redhat
Source5:        %{name}.init-sysv
Source10:       dansguardian-rpmlintrc
Source11:       gpl-2.0.txt
# PATCH-FIX-openSUSE -- Fix path to clamd socket in example config
Patch3:         dansguardian-clamdsocket.patch
# PATCH-fix-upstream -- fix undeclared max_upload_size
# http://sourceforge.net/p/dansguardian/patches/12/attachment/dg.maxuploadsize.patch
# rebased and renamed
Patch4:         %{name}-maxuploadsize.patch
BuildRequires:  curl-devel
BuildRequires:  gcc-c++
BuildRequires:  gmp-devel
BuildRequires:  pcre-devel
BuildRequires:  pkgconfig
BuildRequires:  zlib-devel
Requires:       coreutils
%if 0%{?suse_version}
Recommends:     logrotate
%endif
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
#
# openSUSE specials
%if 0%{?suse_version}
PreReq:         %insserv_prereq
PreReq:         pwdutils
Requires:       http_proxy
%define         _initddir %{_sysconfdir}/init.d
%if 0%{?suse_version} > 1020
BuildRequires:  fdupes
%endif
%endif


%description
DansGuardian is a web filtering engine that checks the content within
the page itself in addition to the more traditional URL filtering.

DansGuardian is a content filtering proxy. It filters using multiple methods,
including URL and domain filtering, content phrase filtering, PICS filtering,
MIME filtering, file extension filtering, POST filtering.

%prep
%setup -q
%{__cp} %{S:11} ./COPYING
%if 0%{?suse_version}
%patch3 -p0
%endif
%patch4 -p0

%build
export CXXFLAGS="%{optflags} -fno-strict-aliasing"
%configure \
  --enable-pcre \
  --enable-segv-backtrace \
  --enable-fancydm \
  --enable-trickledm \
  --enable-ntlm \
  --enable-email \
  --enable-lfs \
  --enable-clamd \
  --enable-icap \
  --enable-commandline \
  --with-piddir="/var/run/" \
  --with-logdir="/var/log/%{name}/" \
  --with-proxyuser="%{dg_user}" \
  --with-proxygroup="%{dg_group}"

%{__perl} -pi.orig -e '
        s|^(CHKCONFIG) =.*$|$1 = :|;
        s|^\tchown|#\tchown|;
        s|/usr/lib|%{_libdir}|g;
        ' Makefile
%{__make} %{?_smp_mflags}

%install
%{__install} -d %{buildroot}%{_localstatedir}/cache/%{name}/
%{__install} -d %{buildroot}%{_localstatedir}/log/%{name}/
%if 0%{?suse_version}
%makeinstall
%else
make install DESTDIR="%{buildroot}"
%endif

%if 0%{?suse_version}
# SUSE version
%{__install} -D -m0755 %{SOURCE1} %{buildroot}%{_initddir}/%{name}
# Only create rc shortcut on SUSE
%{__ln_s} /etc/init.d/%{name} %{buildroot}%{_sbindir}/rc%{name}
%if 0%{?suse_version} > 1020
# save some space, link identical files
%fdupes -s %{buildroot}%{_datadir}/%{name}/languages/
%endif
%else
%if 0%{?rhel_version} || 0%{?centos_version} || 0%{?fedora}
# Red Hat version
%{__install} -D -m0755 %{SOURCE4} %{buildroot}%{_initddir}/%{name}
%else
# Generic SYSV version
%{__install} -D -m0755 %{SOURCE5} %{buildroot}%{_initddir}/%{name}
%endif
%endif

%{__install} -D -m0644 %{SOURCE3} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}

# remove obsolete scripts
%{__rm} -rf %{buildroot}%{_datadir}/%{name}/scripts
# fix execute rights
chmod +x %{buildroot}%{_datadir}/%{name}/%{name}.pl
# save some space, link identical files
#%if 0%{?suse_version} > 1100
#%fdupes -s %{buildroot}%{_datadir}/%{name}/languages/
#%endif

%pre
getent group %{dg_group} >/dev/null || groupadd -r %{dg_group}
getent passwd %{dg_user} >/dev/null || useradd -r -g %{dg_group} -d %{_localstatedir}/log/%{name} -s /sbin/nologin -c "User for %{name}" %{dg_user}

%if 0%{?suse_version}
%preun
%stop_on_removal %{name}

%postun
%restart_on_update %{name}
%insserv_cleanup %{name}
%endif

%clean
%{__rm} -rf %{buildroot}

%files
%defattr(-, root, root, 0755)
%doc AUTHORS ChangeLog COPYING NEWS README UPGRADING
%doc %{_mandir}/man?/*
%doc %{_datadir}/doc/%{name}
%dir %{_sysconfdir}/%{name}
%config(noreplace) %{_sysconfdir}/%{name}/*
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%{_datadir}/%{name}/
%{_sbindir}/%{name}
%{_initddir}/%{name}
%if 0%{?suse_version}
# Only create rc shortcut on SUSE
%{_sbindir}/rc%{name}
%endif
%attr(0755, %{dg_user}, %{dg_group}) %dir %{_localstatedir}/cache/%{name}
%attr(0755, %{dg_user}, %{dg_group}) %dir %{_localstatedir}/log/%{name}

%changelog
* Fri Apr  5 2013 chris@computersalat.de
- September 2012 - Dansguardian 2.12.0.3 - alpha
  * Fixed memory leaks reported by analysis from coverity
  * Improved persistent connection for a better RFC compliant implementation,
    but not yet fully HTTP 1.1
  * Minor improvement for debug output
  * Applied patch #11 (Maxuploadsize per filtergroup) by fredbmail35
- September 2012 - Dansguardian 2.12.0.2 - alpha
  * Applied patch #9 (Crash when more than one authplugin are selected)
    by Frederic Bourgeois
  * Added feature to allow Facebook mock ajax (request #6) by Jason Spiro
  * Added contrib dir
  * Added a new html & css validated html template in contrib (request #3).
    By Chris Peschke
  * Converted iso-8859 message files to utf-8 (bug #86). Suggested
    by Fred Ulisses Maranhao
  * Fixed Error reading Content-Length (bug #84). By Carlos Soto
  * Fixed compilation error BSD due lack of string.h when using memcpy()
    (bug #75). By Alexander Hornung
  * Fixed exceptioniplist case sensitivity (bug #11). By Mark J Hewitt
  * Fixed accept-encoding support for new tokens (bug #13). By userquin
- May 2012 - Dansguardian 2.12.0.1 - alpha - UNRELEASED
  * Applied patch 3438750 (GCC 4.4 and 4.6 compatibility) by Mathieu PARENT
  * Applied patch 3438749 (French translation update) by Mathieu PARENT
  * Applied patch 3418297 (Set proxy timeout in dansguardian.conf) by Frederic Bourgeois
  * Applied patch 3419088 (login/password in URL is dropped) by Mathieu PARENT
  * Applied patch 3419089 ("Expect" header should be dropped) by Mathieu PARENT
  * Applied patch 3438751 (Fix queue handling in OptionContainer) by Mathieu PARENT
  * Applied patch 3515167 (Fix digest identication) by Frederic Bourgeois
  * Fixed GCC warnings
  * LFS review in String.cpp (requires different arch review yet)
- remove obsolete patches
  * ntlm, commandlinescan
- add upstream patch #12
  http://sourceforge.net/p/dansguardian/patches/12/attachment/dg.maxuploadsize.patch
  * rename and rebased to be p0
* Tue Apr 24 2012 chris@computersalat.de
- change dg_group to 'vscan' (clamd)
- add conf patch
  * mv cachedir to /var/cache/dansguardian
- rpmlint
  * incorrect-fsf-address:
    update COPYING with an up to date version
    http://www.gnu.org/licenses/gpl-2.0.txt
* Wed Feb 15 2012 lars@linux-schulserver.de
- refreshed patches - now only the following exist:
  + dansguardian-clamdsocket.patch (fix path to clamd socket on
    openSUSE)
  + dansguardian-commandlinescan.patch (add missing include)
  + dansguardian-ntlm.patch (add mssing include)
- create and use 'dansguardian' as proxy user and group to improve
  security
- added rpmlintrc (for user/group)
- enabled ICAP AV server content scanner
- enabled support for command-line content scanners
- enabled logging a backtrace when a segmentation fault occurs
- built with -fno-strict-aliasing
- use try-restart in logrotate script to avoid a running dansguardian
  if the user disabled the daemon
- requiring clamav during build is not needed any more: removed
* Wed Sep  7 2011 chris@computersalat.de
- update to 2.12.0.0 (alpha)
  - Search term filtering
  - POST data scanning
  - ClamAV scanner removed (direct library usage, not ClamD)
  - "KavAV" scanner removed (direct library usage, not KavD)
  - Fix crash on logging very long URLs
  - Per-group PICS settings
  - Option to use a specific blocked response for Flash
    (".swf" URLs; "application/x-shockwave-flash" MIME type)
  - HTTPHeader bug fixes re. persistent connection detection,
    crash in some (unknown) circumstances when trying to tunnel POST data
  - Added per-room-blocking.
  - Fixed a very old problem with gentle restarts where DG would fail to
    release the RAM for the first set of config loaded.  This was very
    noticeable on systems with many groups.
  - Added the ability to have DG listen on more than one port and to
    use a different authentication plugin on each port.  However, some
    combinations are just not physically possible - for example basic
    auth (proxy auth) won't mix with other authentication methods.
  - Added transparent NTLM authentication, however to be useful needs
    an authentication daemon and daemon-aware, NTLM-enabled web server.
    (read source code for how to use it)
  - Added experimental SSL MITM. (read source code for how to use it)
  - Added experimental SSL certificate checking.
    (read source code for how to use it)
  - Added patch by Massimiliano Hofer to add Avast! support.
  - Tidied up licensing notices and removed some email addresses.
  - Support individual log items up to 32KB in length, which may require
    multiple calls to getLine to read in.
* Thu Apr  8 2010 john@redux.org.uk
- Disable libclamav linkage for all but SUSE >= 11.1 and Fedora.
- Disable %%preun and %%postun for all but SUSE.
* Sat Mar 27 2010 john@redux.org.uk
- Updated spec file to build for Fedora and RHEL/CentOS.
- Added --enable-clamd option, as an alternative to libclamav
  usage.
- Added a patch to enable ClamAV support for ClamAV versions
  0.95 or later.
- Added a patch to add a required #include to fix the build on
  Fedora.
- Added separate init scripts for Fedora/Red Hat and a generic
  SysV init script (from the upstream package) for all others.
* Tue Oct 13 2009 chris@computersalat.de
- cp over from Education
- update to 2.10.1.1
  o Add "originalip" option to dansguardian.conf, for determining
    the original destination IP in transparent proxy set-ups, and
    ensuring that the destination domain of the request resolves to
    that IP.  This can help to address a particular transparent
    proxy security vulnerability (US-CERT VU#435052), but because of
    certain limitations - only implemented on Linux/Netfilter;
    potential breakage of websites using round-robin DNS - the code
    is not enabled by default.  Enable by passing "--enable-orig-ip"
    to the configure script.
  o Fix a crash which could occur when dealing with simultaneous
    incoming connections in configurations using more than one
    listening socket.
  o Fix a crash when checking time limits on item lists.
  o Fix potential usage of uninitialised memory during phrase
    filtering.
- DansGuardian 2.10.0.3 - stable
  o uClibc++ compilation patch from Natanael Copa.
  o Fix crash on exit when running out of memory during phrase tree
    preparation, from Victor Stinner.
  o Clean up destructors for various objects, removing code duplication
    with reset() methods.
  o Compilation fixes from Jeffrey A. Young.
  o Better handling of whitespace (tab characters) in configuration files.
  o Fix HTTPS access for unauthenticated users when using basic or NTLM
    authentication plugins.
  o Reload list files on soft restart if cached (".processed") files have
    been updated directly, from Harry Mason.
  o Chop carriage return off useragent strings when "loguseragent" is
    enabled.
  o Don't force contents of dansguardianf*.conf files to lower-case on
    loading, so as not to destroy the case of group names.
  o Make temporary bypass cookies valid for subdomains of the original
    bypassed domain, including stripping "www.".
- DansGuardian 2.10.0.2 - stable
  o Fix persistent connection detection to resolve issues with HTTP 1.1
    browsers (Firefox), NTLM authentication and HTTPS websites.
  o Change supported syntax for blocking HTTPS site access by IP to match
    that documented in the default bannedsitelist (use "*ips", as
    documented, NOT "**ips").
- DansGuardian 2.10.0.1 - stable
  o Improve malformed URL detection (dc2008.de no longer incorrectly
    classed as malformed).
  o Improve persistent connection detection, correcting some situations in
    which DG would return a blank page to browsers.
  o Updated "proxies" weighted phrase list.
  o Updated Chinese Big-5 messages file from Vicente Chua.
- spec mods
  o change Requires from squid to http_proxy
  o change Requires logrotate to Recommends logrotate
  o always build with clamav for opensuse
  o cleanup
  * TAGS
  * configure
  o fix fdupes for suse_version > 1100
  o Replaced ChangeLog with history.txt to doc
  o use of name macro
* Sat Oct 18 2008 lrupp@suse.de
- improve the init-script to provide more LSB options
- add fix_header.patch from e.kunig@home.nl (see bnc#436726)
- separate changelog
- use insserv macros in %%%%post and %%%%postun
- enable pcre, enable fancydm, enable trickledm, enable email
- use fdupes to link some identical language files
- remove unneeded scripts
* Wed Oct 15 2008 Don Vosburg <don@vosburgs.org>  - 2.10
- Updated to upstream declared stable version 2.10
* Fri Sep 19 2008 Don Vosburg <don@vosburgs.org>  - 2.9.9.8
- Updated to version 2.9.9.8
* Mon Aug 18 2008 Don Vosburg <don@vosburgs.org>  - 2.9.9.7
- Updated to version 2.9.9.7
* Tue Jun 10 2008 Wade Berrier  <wberrier@gmail.com>  - 2.9.9.5
- patch to be able to build with gcc 4.3 (on opensuse 11.0)
* Mon Jun  9 2008 Wade Berrier  <wberrier@gmail.com>  - 2.9.9.5
- Remove $time from Required-Start in .init script
  (allows /etc/init.d/dansguardian to be started automatically
  on suse 11.0)
* Sun Jun  8 2008 Don Vosburg <don@vosburgs.org>  - 2.9.9.5
- Update to version 2.9.9.5
* Thu May 29 2008 Don Vosburg <don@vosburgs.org> - 2.9.9.4
- Update to 2.9.9.4
* Fri Mar 21 2008 Wade Berrier <wberrier@gmail.com> - 2.9.9.3
- Fix up and simplify dansguardian.init script
- Remove additional squid_DG script and only use
  dansguardian.init script for start/stop
* Mon Mar  3 2008 Don Vosburg <don@vosburgs.org> - 2.9.9.3
- Update to 2.9.9.3
- Added additional documentation files
* Tue Jan  8 2008 Wade Berrier <wberrier@gmail.com> - 2.9.9.2
- Disable clamav on 10.3 since an updated clamav in updates
  requires a in .so version.
* Mon Jan  7 2008 Wade Berrier <wberrier@gmail.com> - 2.9.9.2
- enable clamd support for all distros.  Build with clamav on
  10.3 (it's the only distro that has a new enough clamav version)
- spec file whitespace cleanup
- don't generate exceptionfileurllist anymore, since it is
  included in 2.9.9.2
* Sun Dec 30 2007 Don Vosburg <don@vosburgs.org> - 2.9.9.2
- Update to latest 2.9.9.2
* Tue Oct  9 2007 Wade Berrier <wberrier@gmail.com>
- add empty exceptionfileurllist so dansguardian will run
* Wed Oct  3 2007 Don Vosburg <don@vosburgs.org> - 2.9.9.1
- Updated to latest 2.9.9.1 code
* Wed Jun  6 2007 Wade Berrier <wberrier@gmail.com> - 2.9.8.5
- convert dansguardian.logrotate to unix format using dos2unix.
  logrotate apparently cares.
* Tue May 29 2007 Don Vosburg <don@vosburgs.org> - 2.9.8.5
- Added requirements for coreutils (for chown) and squid
* Wed May 23 2007 Don Vosburg <don@vosburgs.org> - 2.9.8.5
- Added ntlm support
* Wed Apr 11 2007 Wade Berrier <wberrier@gmail.com> - 2.9.8.5
- Add logrotate script.  Make sure /etc/ files are not listed
  twice.
* Fri Apr  6 2007 Don Vosburg <don@vosburgs.org> - 2.9.8.5
- Added config file designation to avoid overwriting configs
* Thu Apr  5 2007 Don Vosburg <don@vosburgs.org> - 2.9.8.5
- Updated to 2.9.8.5
* Fri Jan 26 2007 Don Vosburg <don@vosburgs.org> - 2.9.8.2
- Updated to 2.9.8.2
- Fixed pid file and log dir issues
* Sun Dec 17 2006 Don Vosburg <don@vosburgs.org> - 2.9.8.1
- Updated to release 2.9.8.1, added to openSUSE build service
* Fri Oct 22 2004 Don Vosburg <don@vosburgs.org> - 2.8.0.3-1
- Updated to release 2.8.0.3
* Thu Jul 29 2004 Dag Wieers <dag@wieers.com> - 2.8.0.2-1
- Updated to release 2.8.0.2.
* Tue Jul 20 2004 Dag Wieers <dag@wieers.com> - 2.8.0-1
- Updated to release 2.8.0-0.
* Wed Apr 14 2004 Dag Wieers <dag@wieers.com> - 2.6.1.13-1
- Updated to release 2.6.1-13.
* Thu Mar 25 2004 Dag Wieers <dag@wieers.com> - 2.6.1.12-1
- Initial package. (using DAR)
