#! /bin/bash -e
#
# SPDX-License-Identifier: LGPL-2.1-or-later
#
# This script goes through all 'tpm2-import' tokens and converts them
# to 'systemd-tpm2' ones.
#

getval () {
    grep ^\"$2\" $1 | cut -f 2 -d ':' | sed 's/\"//g'
}

if [[ ! -b "$1" ]]; then
    echo "Device $1 does not exist!" 1>&2
    exit 1
fi

/usr/sbin/cryptsetup luksDump "$1" | sed -n '/^Tokens:/,/^Digests:/p' | grep ' tpm2-import' | cut -d ':' -f 1 | while read tokenid; do
    echo "Importing token $tokenid from $1"
    token=`mktemp`
    /usr/sbin/cryptsetup token export --token-id "$tokenid" "$1" | sed -e 's/[{}]/''/g' -e 's/\[//g' -e 's/\]//g' -e 's/,\"/\n"/g' > "$token"
    tempdir=`mktemp -d`
    pushd "$tempdir" > /dev/null
    # Save token data to inidividual files to process them with tpm2-tools
    getval "$token" "parent_pub" | base64 -d > parent.pub
    getval "$token" "parent_prv" | base64 -d > parent.prv
    getval "$token" "parent_seed" | base64 -d > parent.seed
    getval "$token" "seal_pub" | base64 -d > seal.pub
    getval "$token" "seal_prv" | base64 -d > seal.prv
    getval "$token" "pcrpolicy_dat" | base64 -d > pcrpolicy.dat
    if [ ! -z `getval "$token" "unique_dat"` ]; then
        getval "$token" "unique_dat" | base64 -d > unique.dat
    fi
    echo "Unsealing volume key"
    # Import sealed object
    tpm2_flushcontext -t
    if [ ! -f "unique.dat" ]; then
        tpm2_createprimary -Q -C o -a 'restricted|decrypt|fixedtpm|fixedparent|sensitivedataorigin|userwithauth|noda' -g sha256 -G rsa -c primary.ctx
    else
        tpm2_createprimary -Q -C o -a 'restricted|decrypt|fixedtpm|fixedparent|sensitivedataorigin|userwithauth|noda' -g sha256 -G rsa -u unique.dat -c primary.ctx
    fi
    tpm2_flushcontext -t
    tpm2_import -Q -C primary.ctx -u parent.pub -i parent.prv -r parent_imported.prv -s parent.seed
    tpm2_flushcontext -t
    tpm2_load -Q -C primary.ctx -u parent.pub -r parent_imported.prv -c parent.ctx
    tpm2_flushcontext -t
    tpm2_load -Q -C parent.ctx -u seal.pub -r seal.prv -c seal.ctx
    tpm2_flushcontext -t
    tpm2_unseal -Q -c seal.ctx -p pcr:`getval "$token" tpm2-pcr-bank`:`getval "$token" tpm2-pcrs` > volume_key
    tpm2_flushcontext -t
    echo "Sealing new volume key"
    # Create a new sealed object under primary ECC key
    tpm2_createprimary -Q -C o -g sha256 -G ecc:null:aes128cfb -c primary_ecc.ctx
    tpm2_flushcontext -t
    tpm2_create -Q -u seal_local.pub -r seal_local.prv -C primary_ecc.ctx -L pcrpolicy.dat -i volume_key
    # Create a new systemd-tpm2 compatible token
    echo "Adding new LUKS token to $1"
    echo '{"type":"systemd-tpm2","keyslots":["'`getval "$token" keyslots`'"],
           "tpm2-blob":"'`cat seal_local.prv seal_local.pub | base64 -w0`'",
	   "tpm2-pcrs":['`getval "$token" tpm2-pcrs`'],
           "tpm2-pcr-bank":"'`getval "$token" tpm2-pcr-bank`'",
	   "tpm2-primary-alg":"ecc",
	   "tpm2-policy-hash":"'`hexdump -ve '1/1 "%.2x"' pcrpolicy.dat`'",
	   "tpm2-pin": false,
	   "kversion": "'`uname -r`'"}' | /usr/sbin/cryptsetup token import "$1"
    # Remove tpm2-import token now
    echo "Removing now-unneeded token $tokenid from $1"
    /usr/sbin/cryptsetup token remove --token-id "$tokenid" "$1"
    echo "Importing token $tokenid from $1 finished successfully"
    popd > /dev/null
    # Cleanup
    rm -rf "$tempdir"
    rm -f "$token"
done
