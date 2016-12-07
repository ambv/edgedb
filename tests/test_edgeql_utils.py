##
# Copyright (c) 2016-present MagicStack Inc.
# All rights reserved.
#
# See LICENSE for details.
##


import textwrap

from edgedb.lang.edgeql import utils as eql_utils
from edgedb.lang.schema import declarative as s_decl
from edgedb.lang.schema import std as s_std

from edgedb.lang import _testbase as tb


class TestEdgeQLUtils(tb.BaseSyntaxTest):
    SCHEMA = r"""
        abstract concept NamedObject:
            required link name to str

        concept Group extends NamedObject:
            link settings to Setting:
                mapping: 1*

        concept Setting extends NamedObject:
            required link value to str

        concept Profile extends NamedObject:
            required link value to str

        concept User extends NamedObject:
            required link active to bool
            link groups to Group:
                mapping: **
            required link age to int
            required link score to float
            link profile to Profile:
                mapping: *1
    """

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.schema = s_std.load_std_schema()
        s_decl.parse_module_declarations(
            cls.schema, [('test', cls.SCHEMA)])

    def _assert_normalize_expr(self, text, expected, *,
                               anchors=None, inline_anchors=False):
        normalized = eql_utils.normalize_expr(
            text, self.__class__.schema,
            anchors=anchors, inline_anchors=inline_anchors)

        self.assertEqual(
            textwrap.dedent(normalized).strip(),
            textwrap.dedent(expected).strip()
        )

    def test_edgeql_utils_normalize_01(self):
        self._assert_normalize_expr(
            """SELECT 40 + 2""",
            """SELECT (40 + 2)""",
        )

    def test_edgeql_utils_normalize_02(self):
        self._assert_normalize_expr(
            """SELECT -10""",
            """SELECT -10""",
        )

    def test_edgeql_utils_normalize_03(self):
        self._assert_normalize_expr(
            """SELECT strlen('a')""",
            """SELECT std::strlen('a')""",
        )

    def test_edgeql_utils_normalize_04(self):
        self._assert_normalize_expr(
            """WITH MODULE test SELECT User{name}""",
            """SELECT (test::User) { (std::id), (test::name) }"""
        )

    def test_edgeql_utils_normalize_05(self):
        self._assert_normalize_expr(
            """SELECT <int>'1'""",
            """SELECT <std::int>'1'""",
        )

    def test_edgeql_utils_normalize_06(self):
        self._assert_normalize_expr(
            """SELECT ('aaa')[2:-1]""",
            """SELECT ('aaa')[2:-1]"""
        )

    def test_edgeql_utils_normalize_07(self):
        self._assert_normalize_expr(
            """SELECT ('aaa')[2]""",
            """SELECT ('aaa')[2]"""
        )