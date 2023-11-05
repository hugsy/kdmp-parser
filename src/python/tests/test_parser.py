#
# This file is part of kdmp-parser project
#
# Released under MIT License, by 0vercl0k - 2020-2023
#
# With contributions from:
# * masthoon - (github.com/masthoon)
# * hugsy - (github.com/hugsy)
#

import pathlib
import unittest
import zipfile
import pytest

import kdmp_parser

REPO_ROOT = pathlib.Path(__file__).absolute().parent.parent.parent.parent
# Cloned from https://github.com/0vercl0k/kdmp-parser-testdatas
TEST_DATA_DIR = REPO_ROOT / "kdmp-parser-testdatas"
assert TEST_DATA_DIR.exists()
TEST_DATA_ZIPFILE = TEST_DATA_DIR / f"testdatas.zip"
assert TEST_DATA_ZIPFILE.exists()


class TestParserBasic(unittest.TestCase):
    def setUp(self):
        self.formats = ("bmp", "full")
        self.minidump_files: list[pathlib.Path] = []

        minidump_zip = TEST_DATA_ZIPFILE
        assert minidump_zip.exists()

        for format in self.formats:
            minidump_file = TEST_DATA_DIR / f"{format}.dmp"
            if not minidump_file.exists():
                with zipfile.ZipFile(minidump_zip) as f:
                    f.extract(f"{format}.dmp", path=TEST_DATA_DIR)
                assert minidump_file.exists()
            self.minidump_files.append(minidump_file)
        return super().setUp()

    def tearDown(self) -> None:
        return super().tearDown()

    def test_parser_context(self):
        expected_values = {
            "bmp.dmp": {
                "rip": 0xFFFFF805108776A0,
                "rbp": 0xFFFFF80513568600,
                "rsp": 0xFFFFF805135684F8,
                "rax": 0x3,
                "rbx": 0xFFFFF8050F4E9F70,
                "rcx": 0x1,
                "rdx": 0xFFFFF805135684D0,
                "r8": 0x3,
                "r9": 0xFFFFF805135684B8,
                "r10": 0x0,
                "r11": 0xFFFFA8848825E000,
                "r12": 0xFFFFF8050F4E9F80,
                "r13": 0xFFFFF80510C3C958,
                "r14": 0x0,
                "r15": 0x52,
                "dtd": 0x6D4000,
            },
            "full.dmp": {
                "rip": 0xFFFFF805108776A0,
                "rbp": 0xFFFFF80513568600,
                "rsp": 0xFFFFF805135684F8,
                "rax": 0x3,
                "rbx": 0xFFFFF8050F4E9F70,
                "rcx": 0x1,
                "rdx": 0xFFFFF805135684D0,
                "r8": 0x3,
                "r9": 0xFFFFF805135684B8,
                "r10": 0x0,
                "r11": 0xFFFFA8848825E000,
                "r12": 0xFFFFF8050F4E9F80,
                "r13": 0xFFFFF80510C3C958,
                "r14": 0x0,
                "r15": 0x52,
                "dtd": 0x6D4000,
            },
        }

        for md in self.minidump_files:
            parser = kdmp_parser.KernelDumpParser(md)
            assert parser.filepath == md

            values = expected_values[md.name]
            assert parser.context is not None
            assert parser.context.Rip == values["rip"]
            assert parser.context.Rbp == values["rbp"]
            assert parser.context.Rsp == values["rsp"]
            assert parser.context.Rax == values["rax"]
            assert parser.context.Rbx == values["rbx"]
            assert parser.context.Rcx == values["rcx"]
            assert parser.context.Rdx == values["rdx"]
            assert parser.context.R8 == values["r8"]
            assert parser.context.R9 == values["r9"]
            assert parser.context.R10 == values["r10"]
            assert parser.context.R11 == values["r11"]
            assert parser.context.R12 == values["r12"]
            assert parser.context.R13 == values["r13"]
            assert parser.context.R14 == values["r14"]
            assert parser.context.R15 == values["r15"]

            assert parser.directory_table_base == values["dtd"]

    def test_parser_memory(self):
        parser = kdmp_parser.KernelDumpParser(self.minidump_files[0])
        assert parser.directory_table_base == 0x6D4000

        page = parser.read_physical_page(0x5000)
        assert page is not None
        assert page[0x34:0x38] == b"MSFT"

        assert parser.translate_virtual(0xFFFFF78000000000) == 0x0000000000C2F000
        assert parser.translate_virtual(0xFFFFF80513370000) == 0x000000003D555000

        assert parser.read_virtual_page(
            0xFFFFF78000000000
        ) == parser.read_physical_page(0x0000000000C2F000)
        assert parser.read_virtual_page(
            0xFFFFF80513370000
        ) == parser.read_physical_page(0x000000003D555000)
