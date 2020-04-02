# -*- coding: utf-8 -*-

# Copyright (c) IBM Corporation 2019, 2020
# Apache License, Version 2.0 (see https://opensource.org/licenses/Apache-2.0)

from __future__ import absolute_import, division, print_function

__metaclass__ = type

import os
import sys
import warnings

import ansible.constants
import ansible.errors
import ansible.utils
import pytest

# For the authorized command, you can get the list form Z/os system using command "D IKJTSO,AUTHCMD" in sdsf.
# For example:
# IKJ738I TSO/E PARMLIB SETTINGS : 737
#   SYS1.PARMLIB(IKJTSO00) on volume P2SS01
#   Activated by **IPL** on 2020-01-31 at 07:43:51 from system MVXX
#   Applies to :    MVXX
#           CURRENT PARMLIB SETTINGS FOR AUTHCMD:
#           CKGRACF   C4RSTAT   C4RCATMN  IFASMFDP  ADYOPCMD  DITTO
#           EYU9XENF  DITTOA    PING      RECEIVE   SLDSERVE  TRANSMIT
#           XMIT      LISTD     LISTDS    LISTB     LISTBC    SE
#           SEND      RACONVRT  RACDCERT  RACMAP    RACTRACE  RACTR
#           RMM       SYNC      QCBXA     QCBXX     Q         QCBTRACE
#           TESTAUTH  TESTA     CONSPROF  PARMLIB   SHCDS     WDB
#           WDBAUTH   AD        ADDSD     ADIR      ADDDIR    AF
#           ADDFILE   AG        ADDGROUP  AU        ADDUSER   ALG
#           ALTGROUP  ALD       ALTDSD    ALF       ALTFILE   ALTDIR
#           ALU       ALTUSER   BLKUPD    CO        CONNECT   DD
#           DELDSD    DDIR      DELDIR    DF        DELFILE   DG
#           DELGROUP  DU        DELUSER   LD        LISTDSD   LDIR
#           LDIRECT   LF        LFILE     LG        LISTGRP   LU
#           LISTUSER  RALT      RALTER    RDEF      RDEFINE   RDEL
#           RDELETE   RE        REMOVE    RL        RLIST     RVARY
#           PW        PASSWORD  PHRASE    PE        PERMIT    PDIR
#           PERMDIR   PF        PERMFILE  SETR      SETROPTS  SR
#           SEARCH    SRDIR     SRF       SRFILE    AARSERVE  CONCATD
#           CONCATF   CONCATMC  CONCMAIN  PA        PERMALOC  PRIV
#           ERWMAUTH  KERNCP    MVPXDISP  TRACERTE  KILL      DEFINE
#           ATGACMD   MVS5BEG   CMDISSUE  ATGOMATC  IOEAGFMT  DIAGNOSE
#           CSFDPKDS  NEWPWPH   RACLINK   IRRDPI00


# The happy path test
# Run tso command to allocate a dataset like an existing one.
def test_zos_tso_command_long_unauth_command(ansible_zos_module):
    hosts = ansible_zos_module
    # results = hosts.all.zos_tso_command(command="alloc da('imstestl.ims1.test10') like('imstestl.ims1.test05')")
    command_string = "alloc da('imstestl.ims1.temp.ps') catalog lrecl(133) blksize(13300) recfm(f b) dsorg(po) cylinders space(5,5) dir(5)"
    results = hosts.all.zos_tso_command(command=command_string)
    for result in results.contacted.values():
        assert result.get('result').get('rc') == 0
        assert result.get('changed') is True


# The positive path test
# Run an authorized tso command with auth=true
def test_zos_tso_command_short_auth_command_with_auth_equals_true(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_tso_command(command="LISTDS 'imstestl.ims1.temp.ps'", auth=True)
    for result in results.contacted.values():
        assert result.get('result').get('rc') == 0
        assert result.get('changed') is True


# The failure path test
# Run an authorized tso command with auth=False
def test_zos_tso_command_short_auth_command_with_auth_equals_false(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_tso_command(command="LISTDS 'imstestl.ims1.temp.ps'", auth=False)
    for result in results.contacted.values():
        assert result.get('result').get('rc') == 255
        assert result.get('changed') is True


# The positive path test
# Run an unauthorized tso command with auth=False
def test_zos_tso_command_short_unauth_command_with_auth_equals_false(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_tso_command(command="LISTCAT ENT('imstestl.ims1.temp.ps')", auth=False)
    for result in results.contacted.values():
        assert result.get('result').get('rc') == 0
        assert result.get('changed') is True


# The failue path test
# Run an unauthorized tso command with auth=true
def test_zos_tso_command_short_unauth_command_with_auth_equals_true(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_tso_command(command="delete 'imstestl.ims1.temp.ps'", auth=True)
    for result in results.contacted.values():
        assert result.get('result').get('rc') == 255
        assert result.get('changed') is False


def test_zos_tso_command_valid_command(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_tso_command(command="delete 'imstestl.ims1.temp.ps'")
    for result in results.contacted.values():
        assert result.get('result').get('rc') == 0
        assert result.get('changed') is True


# The failure test
# The input command is empty.
def test_zos_tso_command_empty_command(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_tso_command(command="")
    for result in results.contacted.values():
        assert result.get('changed') is False


# The failure test
# The input command is no-existing command, the module return rc 255.
def test_zos_tso_command_invalid_command(ansible_zos_module):
    hosts = ansible_zos_module
    results = hosts.all.zos_tso_command(command="xxxxxx")
    for result in results.contacted.values():
        assert result.get('result').get('rc') == 255
        assert result.get('changed') is False