#!/usr/bin/bash
# SPDX-License-Identifier: GPL-2.0-or-later

check() {
    return 0
}

depends() {
    echo tpm2-tss
    return 0
}

install() {
    inst_multiple -o \
        cryptsetup cut mktemp base64 uname hexdump \
        tpm2_flushcontext tpm2_import tpm2_load tpm2_unseal tpm2_create tpm2_createprimary \
        /usr/sbin/tpm2-luks-import.sh /lib/udev/rules.d/90-tpm2-import.rules
}
