%global with_legacy 0
%global dracut_modname_udev 97walinuxagent
%global dracut_modname_cvm 97walinuxagentcvm

Name:                 WALinuxAgent
Version:              2.7.0.6
Release:              9%{?dist}.1.openela.0
Summary:              The Microsoft Azure Linux Agent

License:              ASL 2.0
URL:                  https://github.com/Azure/%{name}
Source0:              https://github.com/Azure/%{name}/archive/v%{version}.tar.gz
Source1:              module-setup-udev.sh
Source2:              module-setup-cvm.sh
Source3:              90-tpm2-import.rules
Source4:              tpm2-luks-import.sh

# Python3.9 fixes
Patch0001:            0001-Initial-redhat-build-configuation.patch
Patch0002:            0002-Implement-restart_if-for-RedHat-OS.patch
# For bz#2098233 - [Azure][WALA][RHEL-9] [9.1] walinuxagent kills network during boot
Patch3:               wla-redhat-Fix-command-sequence-for-restarting-net-inter.patch
# For bz#2114830 - [Azure][WALA][RHEL-9.1] Provisioning failed if no ifcfg-eth0
Patch4:               wla-redhat-Use-NetworkManager-to-set-DHCP-hostnames-on-r.patch
# For bz#2093965 - [Azure][WALA][RHEL-9] The description of "Logs.Collect" is incorrect
Patch5:               wla-Update-Log-Collector-default-in-Comments-and-Readme-.patch
Patch6:               9999-add-openela-temporarily.patch

# Source-git patches

BuildArch:            noarch

BuildRequires:        python3-devel
BuildRequires:        python3-setuptools
BuildRequires:        python3-distro
Requires:             %name-udev = %version-%release
%if 0%{?fedora}
Requires:             ntfsprogs
%endif
Requires:             openssh
Requires:             openssh-server
Requires:             openssl
Requires:             parted
Requires:             python3-pyasn1
Requires:             iptables

BuildRequires:        systemd
Requires(post):  systemd
Requires(preun): systemd
Requires(postun): systemd

%description
The Microsoft Azure Linux Agent supports the provisioning and running of Linux
VMs in the Microsoft Azure cloud. This package should be installed on Linux disk
images that are built to run in the Microsoft Azure environment.

%if 0%{?with_legacy}
%package legacy
Summary:              The Microsoft Azure Linux Agent (legacy)
Requires:             %name = %version-%release
Requires:             python2
Requires:             net-tools

%description legacy
The Microsoft Azure Linux Agent supporting old version of extensions.
%endif

%package udev
Summary:              Udev rules for Microsoft Azure

%description udev
Udev rules specific to Microsoft Azure Virtual Machines.

%package cvm
Summary:              Microsoft Azure CVM specific tools
Requires:             tpm2-tools
Requires:             cryptsetup

%description cvm
Scripts and udev rules specific to Microsoft Azure Confidential Virtual Machines.

%prep
%setup -q
%autopatch -p1

%build
%py3_build

%install
%{__python3} setup.py install -O1 --skip-build --root %{buildroot} --lnx-distro redhat

mkdir -p -m 0700 %{buildroot}%{_sharedstatedir}/waagent
mkdir -p %{buildroot}%{_localstatedir}/log
touch %{buildroot}%{_localstatedir}/log/waagent.log

mkdir -p %{buildroot}%{_udevrulesdir}
mv %{buildroot}%{_sysconfdir}/udev/rules.d/*.rules %{buildroot}%{_udevrulesdir}/

rm -rf %{buildroot}/%{python3_sitelib}/tests
rm -rf %{buildroot}/%{python3_sitelib}/__main__.py
rm -rf %{buildroot}/%{python3_sitelib}/__pycache__/__main__*.py*

%if 0%{?with_legacy}
sed -i 's,#!/usr/bin/env python,#!/usr/bin/python2,' %{buildroot}%{_sbindir}/waagent2.0
%else
rm -f %{buildroot}%{_sbindir}/waagent2.0
%endif

mv %{buildroot}%{_sysconfdir}/logrotate.d/waagent.logrotate %{buildroot}%{_sysconfdir}/logrotate.d/%{name}

mkdir -p %{buildroot}%{_prefix}/lib/dracut/modules.d/%{dracut_modname_udev}
cp %{SOURCE1} %{buildroot}%{_prefix}/lib/dracut/modules.d/%{dracut_modname_udev}/module-setup.sh
chmod 0755 %{buildroot}%{_prefix}/lib/dracut/modules.d/%{dracut_modname_udev}/module-setup.sh

mkdir -p %{buildroot}%{_prefix}/lib/dracut/modules.d/%{dracut_modname_cvm}
cp %{SOURCE2} %{buildroot}%{_prefix}/lib/dracut/modules.d/%{dracut_modname_cvm}/module-setup.sh
chmod 0755 %{buildroot}%{_prefix}/lib/dracut/modules.d/%{dracut_modname_cvm}/module-setup.sh
install -m0644 -D -t %{buildroot}%{_udevrulesdir}/ %{SOURCE3}
install -m0755 -D -t %{buildroot}%{_sbindir} %{SOURCE4}

%post
%systemd_post waagent.service

%preun
%systemd_preun waagent.service

%postun
%systemd_postun_with_restart waagent.service
rm -rf %{_unitdir}/waagent.service.d/

%files
%doc LICENSE.txt NOTICE README.md
%ghost %{_localstatedir}/log/waagent.log
%ghost %{_unitdir}/waagent-network-setup.service
%dir %attr(0700, root, root) %{_sharedstatedir}/waagent
%config(noreplace) %{_sysconfdir}/logrotate.d/%{name}
%{_sbindir}/waagent
%config(noreplace) %{_sysconfdir}/waagent.conf
%{_unitdir}/waagent.service
%{_unitdir}/azure.slice
%{_unitdir}/azure-vmextensions.slice
%{python3_sitelib}/azurelinuxagent
%{python3_sitelib}/*.egg-info

%files udev
%{_udevrulesdir}/66-azure-storage.rules
%{_udevrulesdir}/99-azure-product-uuid.rules
%dir %{_prefix}/lib/dracut/modules.d/%{dracut_modname_udev}
%{_prefix}/lib/dracut/modules.d/%{dracut_modname_udev}/*.sh

%files cvm
%{_sbindir}/tpm2-luks-import.sh
%{_udevrulesdir}/90-tpm2-import.rules
%dir %{_prefix}/lib/dracut/modules.d/%{dracut_modname_cvm}
%{_prefix}/lib/dracut/modules.d/%{dracut_modname_cvm}/*.sh

%if 0%{?with_legacy}
%files legacy
%{_sbindir}/waagent2.0
%endif

%changelog
* Fri Feb 09 2024 Release Engineering <releng@openela.org> - 2.7.0.6.openela.0
- Backport OpenELA temporarily

* Tue Jul 18 2023 Miroslav Rezanina <mrezanin@redhat.com> - 2.7.0.6-9.el9_2.1
- Rebuild for BZ 2222947
- Resolves: bz#2222947

* Wed Feb 08 2023 Miroslav Rezanina <mrezanin@redhat.com> - 2.7.0.6-9
- wla-redhat-Adjust-tpm2_createprimary-key-attributes-to-m.patch [bz#2167322]
- Resolves: bz#2167322
  (Adjust TPM primary key creation parameters to match Azure)

* Mon Feb 06 2023 Miroslav Rezanina <mrezanin@redhat.com> - 2.7.0.6-8
- wla-redhat-Explicitly-list-udev-rule-requirements-in-the.patch [bz#2165042]
- Resolves: bz#2165042
  ([9.0.z] /dev/disk/azure/ is created as symlink to sr0 or sda and not as a directory[Azure])

* Mon Jan 23 2023 Miroslav Rezanina <mrezanin@redhat.com> - 2.7.0.6-7
- wla-redhat-Azure-CVM-specific-udev-rules.patch [bz#2162668]
- Resolves: bz#2162668
  (Add support for importing remotely sealed TPM2 objects)

* Mon Aug 29 2022 Miroslav Rezanina <mrezanin@redhat.com> - 2.7.0.6-6
- wla-redhat-Remove-files-inside-WALA-services-directory.patch [bz#2114768]
- Resolves: bz#2114768
  ([Azure][WALA][RHEL-9] When remove package some files left)

* Tue Aug 23 2022 Miroslav Rezanina <mrezanin@redhat.com> - 2.7.0.6-5
- wla-redhat-Mark-directories-properly-in-the-files-list.patch [bz#2114768]
- Resolves: bz#2114768
  ([Azure][WALA][RHEL-9] When remove package some files left)

* Wed Aug 17 2022 Miroslav Rezanina <mrezanin@redhat.com> - 2.7.0.6-4
- wla-redhat-Remove-all-waagent-unit-files-when-uninstalli.patch [bz#2114768]
- Resolves: bz#2114768
  ([Azure][WALA][RHEL-9] When remove package some files left)

* Mon Aug 08 2022 Miroslav Rezanina <mrezanin@redhat.com> - 2.7.0.6-3
- wla-redhat-Use-NetworkManager-to-set-DHCP-hostnames-on-r.patch [bz#2114830]
- wla-Update-Log-Collector-default-in-Comments-and-Readme-.patch [bz#2093965]
- Resolves: bz#2114830
  ([Azure][WALA][RHEL-9.1] Provisioning failed if no ifcfg-eth0)
- Resolves: bz#2093965
  ([Azure][WALA][RHEL-9] The description of "Logs.Collect" is incorrect)

* Fri Jul 15 2022 Miroslav Rezanina <mrezanin@redhat.com> - 2.7.0.6-2
- wla-redhat-Fix-command-sequence-for-restarting-net-inter.patch [bz#2098233]
- Resolves: bz#2098233
  ([Azure][WALA][RHEL-9] [9.1] walinuxagent kills network during boot)

* Wed May 25 2022 Miroslav Rezanina <mrezanin@redhat.com> - 2.7.0.6-1
- Rebase to 2.7.0.6-1 [bz#2083464]
- Adding restart_if implementation for RHEL [bz#2081944]
- Resolves: bz#2083464
  ([Azure][RHEL-9]Rebase WALinuxAgent to v2.7.0.6)
- Resolves: bz#2081944
  ([Azure][WALA][9.0] WALA provisions VM failed because of no "ifdown")

* Tue Aug 10 2021 Mohan Boddu <mboddu@redhat.com> - 2.3.0.2-3
- Rebuilt for IMA sigs, glibc 2.34, aarch64 flags
  Related: rhbz#1991688

* Sun Jul 25 2021 Miroslav Rezanina <mrezanin@redhat.com> - 2.3.0.2-2
- wala-Require-iptables-package.patch [bz#1978572]
- Resolves: bz#1978572
  ([Azure][WALA][RHEL-9] WALA needs iptables package)

* Thu Jun 24 2021 Miroslav Rezanina <mrezanin@redhat.com> - 2.3.0.2-1
- Rebase to 2.3.0.2 [bz#1972101]
- Resolves: bz#1972101
  ([Azure][RHEL-9]Rebase WALinuxAgent to 2.3.0.2)

* Thu Apr 15 2021 Mohan Boddu <mboddu@redhat.com> - 2.2.52-6
- Rebuilt for RHEL 9 BETA on Apr 15th 2021. Related: rhbz#1947937

* Fri Feb 19 2021 Vitaly Kuznetsov <vkuznets@redhat.com> - 2.2.52-5
- Require ntfsprogs on Fedora only

* Tue Jan 26 2021 Vitaly Kuznetsov <vkuznets@redhat.com> - 2.2.52-4
- Fix distro resolution for RedHat

* Mon Jan 25 2021 Fedora Release Engineering <releng@fedoraproject.org> - 2.2.52-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_34_Mass_Rebuild

* Fri Jan 15 2021 Vitaly Kuznetsov <vkuznets@redhat.com> - 2.2.52-2
- Add udev rules to initramfs (#1909287)

* Wed Dec 09 2020 Vitaly Kuznetsov <vkuznets@redhat.com> - 2.2.52-1
- Update to 2.2.52 (#1849923)
- Add not yet upstream patches supporting Python3.9 changes

* Mon Jul 27 2020 Fedora Release Engineering <releng@fedoraproject.org> - 2.2.48.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_33_Mass_Rebuild

* Tue Jun 09 2020 Vitaly Kuznetsov <vkuznets@redhat.com> - 2.2.48.1-1
- Update to 2.2.48.1 (#1641605)
- Split udev rules to a separate subpackage (#1748432)

* Tue May 26 2020 Miro Hrončok <mhroncok@redhat.com> - 2.2.46-2
- Rebuilt for Python 3.9

* Wed Apr 15 2020 Vitaly Kuznetsov <vkuznets@redhat.com> - 2.2.46-1
- Update to 2.2.46

* Tue Jan 28 2020 Fedora Release Engineering <releng@fedoraproject.org> - 2.2.40-7
- Rebuilt for https://fedoraproject.org/wiki/Fedora_32_Mass_Rebuild

* Thu Oct 03 2019 Miro Hrončok <mhroncok@redhat.com> - 2.2.40-6
- Rebuilt for Python 3.8.0rc1 (#1748018)

* Wed Aug 21 2019 Miro Hrončok <mhroncok@redhat.com> - 2.2.40-5
- Rebuilt for Python 3.8

* Wed Aug 21 2019 Vitaly Kuznetsov <vkuznets@redhat.com> - 2.2.40-4
- Disable Python2 dependent 'legacy' subpackage (#1741029)

* Mon Aug 19 2019 Miro Hrončok <mhroncok@redhat.com> - 2.2.40-3
- Rebuilt for Python 3.8

* Wed Jul 24 2019 Fedora Release Engineering <releng@fedoraproject.org> - 2.2.40-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_31_Mass_Rebuild

* Mon Jun 03 2019 Vitaly Kuznetsov <vkuznets@redhat.com> - 2.2.40-1
- Update to 2.2.40
- Fix FTBFS in the preparation for Python3.8 (#1705219)

* Thu Mar 14 2019 Vitaly Kuznetsov <vkuznets@redhat.com> - 2.2.38-1
- Update to 2.2.38 (CVE-2019-0804)

* Thu Mar 14 2019 Vitaly Kuznetsov <vkuznets@redhat.com> - 2.2.37-1
- Update to 2.2.37

* Thu Jan 31 2019 Fedora Release Engineering <releng@fedoraproject.org> - 2.2.32-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_30_Mass_Rebuild

* Thu Sep 20 2018 Vitaly Kuznetsov <vkuznets@redhat.com> - 2.2.32-1
- Update to 2.2.32.2

* Thu Jul 12 2018 Fedora Release Engineering <releng@fedoraproject.org> - 2.2.25-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_29_Mass_Rebuild

* Tue Jun 19 2018 Miro Hrončok <mhroncok@redhat.com> - 2.2.25-3
- Rebuilt for Python 3.7

* Wed Apr 25 2018 Vitaly Kuznetsov <vkuznets@redhat.com> - 2.2.25-2
- Move net-tools dependency to WALinuxAgent-legacy (#1106781)

* Mon Apr 16 2018 Vitaly Kuznetsov <vkuznets@redhat.com> - 2.2.25-1
- Update to 2.2.25
- Switch to Python3
- Legacy subpackage with waagent2.0 supporting old extensions

* Wed Feb 28 2018 Iryna Shcherbina <ishcherb@redhat.com> - 2.0.18-5
- Update Python 2 dependency declarations to new packaging standards
  (See https://fedoraproject.org/wiki/FinalizingFedoraSwitchtoPython3)

* Wed Feb 07 2018 Fedora Release Engineering <releng@fedoraproject.org> - 2.0.18-4
- Rebuilt for https://fedoraproject.org/wiki/Fedora_28_Mass_Rebuild

* Wed Jul 26 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.0.18-3
- Rebuilt for https://fedoraproject.org/wiki/Fedora_27_Mass_Rebuild

* Fri Feb 10 2017 Fedora Release Engineering <releng@fedoraproject.org> - 2.0.18-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_26_Mass_Rebuild

* Sat Apr 02 2016 Scott K Logan <logans@cottsay.net> - 2.0.18-1
- Update to 2.0.18

* Wed Feb 03 2016 Fedora Release Engineering <releng@fedoraproject.org> - 2.0.14-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_24_Mass_Rebuild

* Thu Jul 02 2015 Scott K Logan <logans@cottsay.net> - 2.0.14-1
- Update to 2.0.14

* Tue Jun 16 2015 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 2.0.13-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_23_Mass_Rebuild

* Mon Jun 01 2015 Scott K Logan <logans@cottsay.net> - 2.0.13-1
- Update to 2.0.13

* Thu Apr 02 2015 Scott K Logan <logans@cottsay.net> - 2.0.12-1
- Update to 2.0.12-Oracle

* Sat Jan 10 2015 Scott K Logan <logans@cottsay.net> - 2.0.11-2
- Use systemd for rhel7
- Own logrotate.d
- Fix python2-devel dep

* Sat Dec 20 2014 Scott K Logan <logans@cottsay.net> - 2.0.11-1
- Initial package
