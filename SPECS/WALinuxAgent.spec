Summary:              Microsoft Azure Linux Agent
Name:                 WALinuxAgent
Version:              2.7.0.6
Release:              8%{?dist}.openela.0.1

License:              ASL 2.0
Group:                Development/Libraries
Url:                  https://github.com/Azure/WALinuxAgent
Source0:              v2.7.0.6.tar.gz

BuildArch:            noarch
Patch0001:            0001-Add-inital-redhat-build-support.patch
Patch0002:            0002-Implement-restart_if-for-RedHat-OS.patch
# For bz#2080826 - [Azure][WALA][RHEL-8] [8.7] walinuxagent kills network during boot
Patch0003:            wla-redhat-Fix-command-sequence-for-restarting-net-inter.patch
# For bz#2092002 - [Azure][WALA][RHEL-8.7] Provisioning failed if no ifcfg-eth0
Patch4:               wla-redhat-Use-NetworkManager-to-set-DHCP-hostnames-on-r.patch
# For bz#2114824 - [Azure][WALA][RHEL-8.7] The description of "Logs.Collect" is incorrect
Patch5:               wla-Update-Log-Collector-default-in-Comments-and-Readme-.patch
# For bz#2170104 - [Azure][WALA][RHEL-8] systemd service should not use python3
Patch6:               wla-Use-platform-python-in-waagent.service.patch
Patch7:               9999-add-openela-temporarily.patch

# rhel requirements
BuildRequires:        python3-devel
BuildRequires:        python3-setuptools
Requires:             %name-udev = %version-%release
Requires:             openssh
Requires:             openssh-server
Requires:             openssl
Requires:             parted
Requires:             python3-pyasn1
Requires:             python36
Requires:             iptables

BuildRequires:        systemd
Requires(post):  systemd
Requires(preun): systemd
Requires(postun): systemd

%description
The Azure Linux Agent supports the provisioning and running of Linux
VMs in the Azure cloud. This package should be installed on Linux disk
images that are built to run in the Azure environment.

%package udev
Summary:              Udev rules for Microsoft Azure

%description udev
Udev rules specific to Microsoft Azure Virtual Machines.

%prep
%setup -q

%patch0001 -p1
%patch0002 -p1
%patch0003 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1
%patch7 -p1

%build
%py3_build

%install
%{__python3} setup.py install --single-version-externally-managed -O1 --root=$RPM_BUILD_ROOT --record=INSTALLED_FILES
rm -f %{buildroot}%{_sbindir}/waagent2.0

mkdir -p %{buildroot}%{_udevrulesdir}
mv %{buildroot}%{_sysconfdir}/udev/rules.d/*.rules %{buildroot}%{_udevrulesdir}/

%clean
rm -rf $RPM_BUILD_ROOT

%post
%systemd_post waagent.service

%preun
%systemd_preun waagent.service

%postun
%systemd_postun_with_restart waagent.service
rm -rf %{_unitdir}/waagent.service.d/

%files 
%defattr(-,root,root)
%{python3_sitelib}/*
%config(noreplace) %{_sysconfdir}/waagent.conf
%config(noreplace) %{_sysconfdir}/logrotate.d/waagent.logrotate
%{_sbindir}/waagent
%{_unitdir}/waagent.service
%{_unitdir}/azure.slice
%{_unitdir}/azure-vmextensions.slice
%ghost %{_unitdir}/waagent-network-setup.service

%files udev
%{_udevrulesdir}/*.rules

%changelog
* Tue Mar 05 2024 Release Engineering <releng@openela.org> - 2.7.0.6.openela.0.1
- Backport OpenELA temporarily

* Mon Mar 06 2023 Jon Maloy <jmaloy@redhat.com> - 2.7.0.6-8.el8_8
- wla-redhat-Fix-frh.py-to-not-skip-valid-patches-to-init-.patch [bz#2170104]
- wla-Use-platform-python-in-waagent.service.patch [bz#2170104]
- Resolves: bz#2170104
  ([Azure][WALA][RHEL-8] systemd service should not use python3)

* Mon Mar 06 2023 Jon Maloy <jmaloy@redhat.com> - 2.7.0.6-7.el8_8
- wla-redhat-Fix-frh.py-to-not-skip-valid-patches-to-init-.patch [bz#2170104]
- wla-Use-platform-python-in-waagent.service.patch [bz#2170104]
- Resolves: bz#2170104
  ([Azure][WALA][RHEL-8] systemd service should not use python3)

* Mon Aug 29 2022 Miroslav Rezanina <mrezanin@redhat.com> - 2.7.0.6-6
- wla-redhat-Remove-files-inside-WALA-services-directory.patch [bz#2114742]
- Resolves: bz#2114742
  ([Azure][WALA][RHEL-8] When remove package some files left)

* Tue Aug 23 2022 Miroslav Rezanina <mrezanin@redhat.com> - 2.7.0.6-5
- wla-redhat-Mark-directories-properly-in-the-files-list.patch [bz#2114742]
- Resolves: bz#2114742
  ([Azure][WALA][RHEL-8] When remove package some files left)

* Wed Aug 17 2022 Jon Maloy <jmaloy@redhat.com> - 2.7.0.6-4
- wla-redhat-Remove-all-waagent-unit-files-when-uninstalli.patch [bz#2114742]
- Resolves: bz#2114742
  ([Azure][WALA][RHEL-8] When remove package some files left)

* Tue Aug 09 2022 Miroslav Rezanina <mrezanin@redhat.com> - 2.7.0.6-3
- wla-redhat-Use-NetworkManager-to-set-DHCP-hostnames-on-r.patch [bz#2092002]
- wla-Update-Log-Collector-default-in-Comments-and-Readme-.patch [bz#2114824]
- Resolves: bz#2092002
  ([Azure][WALA][RHEL-8.7] Provisioning failed if no ifcfg-eth0)
- Resolves: bz#2114824
  ([Azure][WALA][RHEL-8.7] The description of "Logs.Collect" is incorrect)

* Tue Jul 12 2022 Camilla Conte <cconte@redhat.com> - 2.7.0.6-2
- wla-redhat-Fix-command-sequence-for-restarting-net-inter.patch [bz#2080826]
- Resolves: bz#2080826
  ([Azure][WALA][RHEL-8] [8.7] walinuxagent kills network during boot)

* Wed May 25 2022 Miroslav Rezanina <mrezanin@redhat.com> - 2.7.0.6-1
- Rebase to 2.7.0.6 [bz#2083465]
- Adding restart_if implementation for RHEL [bz#2085578]
- Resolves: bz#2083465
  ([Azure][RHEL-8][8.7] Rebase WALinuxAgent to v2.7.0.6)
- Resolves: bz#2085578
  ([Azure][WALA][8.6] WALA provisions VM failed because of no "ifdown")

* Mon Aug 09 2021 Miroslav Rezanina <mrezanin@redhat.com> - 2.3.0.2-2
- wla-Require-iptables-for-setting-up-persistent-firewall-.patch [bz#1985198]
- Resolves: bz#1985198
  ([Azure][WALA][RHEL-8] WALA needs iptables package)

* Fri Jun 25 2021 Miroslav Rezanina <mrezanin@redhat.com> - 2.3.0.2-1
- Rebase to 2.3.0.2 [bz#1972102]
- Resolves: bz#1972102
  ([Azure][RHEL-8]Rebase WALinuxAgent to 2.3.0.2)

* Tue Jan 12 2021 Miroslav Rezanina <mrezanin@redhat.com> - 2.2.49.2-3.el8
- wla-Provide-udev-rules-as-a-separate-subpackage.patch [bz#1913074]
- Resolves: bz#1913074
  ([Azure][RFE] please provide the WALinuxAgent-udev subpackage)

* Thu Dec 17 2020 Miroslav Rezanina <mrezanin@redhat.com> - 2.2.49.2-2.el8
- wla-Fixed-faulty-check-for-run_command-2093.patch [bz#1903074]
- Resolves: bz#1903074
  ([Azure][WALA] Miss report "hostnamectl set-hostname --static] failed, attempting fallback")

* Wed Nov 18 2020 Miroslav Rezanina <mrezanin@redhat.com> - 2.2.49.2-1.el8
- Rebase to 2.2.49.2 [bz#1896907]
  ([Azure] Rebase WALinuxAgent to 2.2.49)

* Thu Aug 13 2020 Miroslav Rezanina <mrezanin@redhat.com> - 2.2.46-8.el8
- wla-Fix-handling-of-gen2-disks-with-udev-rules-1954.patch [bz#1859037]
- Resolves: bz#1859037
  ([Azure][WALA]Cannot create /dev/disk/azure/resource softlinks in Gen2 VM)

* Wed Jun 10 2020 Miroslav Rezanina <mrezanin@redhat.com> - 2.2.46-7.el8
- wla-Mark-logrotate-configs-with-config-noreplace.patch [bz#1838254]
- Resolves: bz#1838254
  ([Azure]WALinuxAgent RPM update clobbers waagent.logrotate log rotation changes)

* Tue May 26 2020 Miroslav Rezanina <mrezanin@redhat.com> - 2.2.46-6.el8
- wala-Update-Provisioning-options-1853.patch [bz#1827792]
- Resolves: bz#1822882
  ([Azure][RHEL-8]Some parameter changes are not in waagent.conf)

* Thu Apr 09 2020 Miroslav Rezanina <mrezanin@redhat.com> - 2.2.46-5.el8
- Rebase to 2.2.46 [bz#1791069]
- Resolves: bz#1791069
  ([Azure][RHEL-8.3]Ask to increase the WALA version available for RHEL 8.0 to 2.2.46)

* Wed Jun 26 2019 Miroslav Rezanina <mrezanin@redhat.com> - 2.2.32-3.el8
- wla-Switch-from-platform-python-to-python36.patch [bz#1720373]
- wla-Stop-packaging-legacy-waagent2.0.patch [bz#1720373]
- Resolves: bz#1720373
  ([RHEL 8.1] [Azure] Change WALinuxAgent spec to depend on Python3.6 package)

* Tue Apr 30 2019 Danilo Cesar Lemes de Paula <ddepaula@redhat.com> - 2.2.32-2.el8
- wla-Add-fixes-for-handling-swap-file-and-other-nit-fixes.patch [bz#1684181 bz#1688276]
- Resolves: bz#1684181
  (CVE-2019-0804 WALinuxAgent: swapfile created with weak permissions)
- Resolves: bz#1688276
  (CVE-2019-0804 WALinuxAgent: swapfile created with weak permissions [rhel-8])

* Fri Dec 14 2018 Miroslav Rezanina <mrezanin@redhat.com> - 2.2.32-1.el8
- Rebase to 2.2.32 [bz#1639498]
- Resolves: bz#1639498]
  (walinuxagent 2.2.32 packaging request for RHEL 8)

* Tue Oct 23 2018 Miroslav Rezanina <mrezanin@redhat.com> - 2.2.26-6.el8
- wala-Use-sys.executable-to-find-system-python.patch [bz#1639775]
- Resolves: bz#1639775
  (WALinuxAgent: Systemd unit file will fail to execute)

* Mon Oct 22 2018 Miroslav Rezanina <mrezanin@redhat.com> - 2.2.26-5.el8
- wala-Switch-to-platform-python-in-systemd-unit-file.patch [bz#1639775]
- Resolves: bz#1639775
  (WALinuxAgent: Systemd unit file will fail to execute)

* Wed Aug 29 2018 Miroslav Rezanina <mrezanin@redhat.com> - 2.2.26-4.el8
- Fix unit file location [bz#1637545]
- Resolves: bz#1637545
  (Wrong macro used for systemd unit file location)

* Wed Jul 04 2018 Tomas Orsava <torsava@redhat.com> - 2.2.26-3
- Switch hardcoded python3 shebangs into the %%{__python3} macro

* Tue Jul 03 2018 Miroslav Rezanina <mrezanin@redhat.com> - 2.2.26-2.el8
- Include 7.6 patches

* Tue Jul 03 2018 Miroslav Rezanina <mrezanin@redhat.com> - 2.2.26-1.el7
- Rebase to 2.2.26 [bz#1571523]
- Resolves: bz#1571523
  (Rebase WALinuxAgent in RHEL-8.0)

* Thu May 03 2018 Miroslav Rezanina <mrezanin@redhat.com> - 2.2.18-2.el7
- wa-Add-show-configuration-option.patch [bz#1508340]
- Resolves: bz#1508340
  ([WALA] WALA usage prompt lack of " waagent -show-configuration")

* Tue Oct 10 2017 Miroslav Rezanina <mrezanin@redhat.com> - 2.2.18-1.el7
- Rebase to 2.2.18 [bz#1491873]
- Resolves: bz#1491873
  ([WALA]Request to package WALA 2.2.18 into RHEL 7 Repo)


* Tue Jul 04 2017 Miroslav Rezanina <mrezanin@redhat.com> - 2.2.14-1.el7
- Rebase to 2.2.14 [bz#1451172]
- wla-Remove-FIPS-setting-from-the-default-config.patch [bz#1467553]
- Resolves: bz#1451172
  ([WALA] Request to package WALA 2.2.14 into RHEL 7 Repo)
- Resolves: bz#1467553
  ([WALA] Remove FIPS from default config in WALA-2.2.14)

* Wed Apr 26 2017 Miroslav Rezanina <mrezanin@redhat.com> - 2.2.10-1.el7
- Rebase to 2.2.10 [bz#1443425]
- Resolves: bz#1443425
  ([WALA]Request to package WALA 2.2.10 into RHEL 7 Repo)

* Wed Apr 19 2017 Miroslav Rezanina <mrezanin@redhat.com> - 2.2.4-2.el7
- Enable AutoUpdate by default [bz#1434933]
- Resolves: bz#1434933
  ([WALA][RHEL-7] Enable AutoUpdate by default)

* Wed Mar 01 2017 Miroslav Rezanina <mrezanin@redhat.com> - 2.2.4-1.el7
- Rebase to 2.2.4 [bz#1419201]
- resolves: bz#1419201
  WALA 2.2.4

* Mon Jan 16 2017 Miroslav Rezanina <mrezanin@redhat.com> - 2.2.0-4.el7
- agent-RHEL-7-hostname-533.patch [bz#1413674]
- agent-fix-for-hostnamectl-534.patch [bz#1413674]
- Resolves: bz#1413674
  ([WALA] Fail to send hostname to DHCP server during provisioning)

* Fri Sep 30 2016 Dave Anderson <anderson@redhat.com> - 2.2.0-1
- Update to v2.2.0
  Resolves: rhbz#1360492

* Wed Sep 21 2016 Dave Anderson <anderson@redhat.com> - 2.1.5-2
- Several QE updates to this file
  Resolves: rhbz#1360492

* Tue Sep 13 2016 Dave Anderson <anderson@redhat.com> - 2.1.5-1
- Update to v2.1.5
  Resolves: rhbz#1360492

* Thu Jan 14 2016 Dave Anderson <anderson@redhat.com> - 2.0.16-1
- Update to 2.0.16
  Resolves: rhbz#1296360

* Mon Jun 01 2015 Dave Anderson <anderson@redhat.com> - 2.0.13-1
- Update to upstream 2.0.13 package.
- Remove global commit md5sum and fix Source0 to point to correct location.
- Fix setup to deal with "WALinuxAgent-WALinuxAgent" naming scheme
- Added files reference for /udev/rules.d/99-azure-product-uuid.rules

* Thu May 07 2015 Dave Anderson <anderson@redhat.com> - 2.0.11-3
- Remove Requires: ntfsprogs for RHEL7

* Sat Jan 10 2015 Scott K Logan <logans@cottsay.net> - 2.0.11-2
- Use systemd for rhel7
- Own logrotate.d
- Fix python2-devel dep

* Sat Dec 20 2014 Scott K Logan <logans@cottsay.net> - 2.0.11-1
- Initial package
