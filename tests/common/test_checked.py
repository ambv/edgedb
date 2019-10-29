#
# This source file is part of the EdgeDB open source project.
#
# Copyright 2011-present MagicStack Inc. and the EdgeDB authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

from __future__ import annotations
from typing import *  # NoQA

import pickle
import unittest

from edb.common.checked import CheckedDict
from edb.common.checked import CheckedList
from edb.common.checked import CheckedSet
from edb.common.checked import FrozenCheckedList
from edb.common.checked import FrozenCheckedSet


class CheckedDictTests(unittest.TestCase):
    def test_common_checked_checkeddict_basics(self) -> None:
        StrDict = CheckedDict[str, int]
        assert StrDict({"1": 2})["1"] == 2
        assert StrDict(foo=1, initdict=2)["initdict"] == 2

        sd = StrDict(**{"1": 2})
        assert sd["1"] == 2

        assert dict(sd) == {"1": 2}

        sd["foo"] = 42

        with self.assertRaises(KeyError):
            sd[0] = 0
        with self.assertRaises(ValueError):
            sd["foo"] = "bar"
        assert sd["foo"] == 42

        with self.assertRaises(ValueError):
            sd.update({"spam": "ham"})

        sd.update({"spam": 12})
        assert sd["spam"] == 12

        with self.assertRaises(ValueError):
            StrDict(**{"foo": "bar"})

        with self.assertRaisesRegex(TypeError, "expects two type parameters"):
            # no value type given
            CheckedDict[int]

        class Foo:
            def __repr__(self):
                return self.__class__.__name__

        class Bar(Foo):
            pass

        FooDict = CheckedDict[str, Foo]

        td = FooDict(bar=Bar(), foo=Foo())
        expected = (
            f"edb.common.checked.CheckedDict[str, common.test_checked."
            "CheckedDictTests.test_common_checked_checkeddict_basics."
            "<locals>.Foo]({'bar': Bar, 'foo': Foo})"
        )
        assert repr(td) == expected
        expected = "{'bar': Bar, 'foo': Foo}"
        assert str(td) == expected

        with self.assertRaisesRegex(ValueError, "expected at most 1"):
            FooDict(Foo(), Bar())

        td = FooDict.fromkeys("abc", value=Bar())
        assert len(td) == 3
        del td["b"]
        assert "b" not in td
        assert len(td) == 2
        assert str(td) == "{'a': Bar, 'c': Bar}"

    def test_common_checked_checkeddict_pickling(self) -> None:
        StrDict = CheckedDict[str, int]
        sd = StrDict()
        sd["foo"] = 123
        sd["bar"] = 456

        assert sd.keytype is str and sd.valuetype is int
        assert type(sd) is StrDict
        assert sd["foo"] == 123
        assert sd["bar"] == 456

        sd2 = pickle.loads(pickle.dumps(sd))

        assert sd2.keytype is str and sd2.valuetype is int
        assert type(sd2) is StrDict
        assert sd2["foo"] == 123
        assert sd2["bar"] == 456
        assert sd is not sd2
        assert sd == sd2


class BaseCheckedListTests(unittest.TestCase):
    BaseList = FrozenCheckedList

    def test_common_checked_shared_list_basics(self) -> None:
        IntList = self.BaseList[int]
        StrList = self.BaseList[str]

        with self.assertRaises(ValueError):
            IntList(("1", "2"))

        with self.assertRaises(ValueError):
            StrList([1])

        with self.assertRaises(ValueError):
            StrList([None])

        sl = StrList(["Some", "strings", "here"])
        assert sl == ["Some", "strings", "here"]
        assert list(sl) == ["Some", "strings", "here"]
        assert sl > ["Some", "strings"]
        assert sl < ["Some", "strings", "here", "too"]
        assert sl >= ["Some", "strings"]
        assert sl <= ["Some", "strings", "here", "too"]
        assert sl >= ["Some", "strings", "here"]
        assert sl <= StrList(["Some", "strings", "here"])
        assert sl + ["too"] == ["Some", "strings", "here", "too"]
        assert ["Hey"] + sl == ["Hey", "Some", "strings", "here"]
        assert type(sl + ["too"]) is StrList
        assert type(["Hey"] + sl) is StrList
        assert sl[0] == "Some"
        assert type(sl[:2]) is StrList
        assert sl[:2] == StrList(["Some", "strings"])
        assert len(sl) == 3
        assert sl[1:2] * 3 == ["strings", "strings", "strings"]
        assert 3 * sl[1:2] == ["strings", "strings", "strings"]
        assert type(3 * sl[1:2]) is StrList

        class Foo:
            def __repr__(self):
                return self.__class__.__name__

        class Bar(Foo):
            pass

        FooList = self.BaseList[Foo]

        tl = FooList([Bar(), Foo()])
        cls_name = self.BaseList.__name__
        expected = (
            f"edb.common.checked.{cls_name}[common.test_checked."
            "BaseCheckedListTests.test_common_checked_shared_list_basics."
            "<locals>.Foo]([Bar, Foo])"
        )
        assert repr(tl) == expected, repr(tl)
        expected = "[Bar, Foo]"
        assert str(tl) == expected

    def test_common_checked_shared_list_pickling(self):
        StrList = self.BaseList[str]
        sd = StrList(["123", "456"])

        assert sd.type is str
        assert type(sd) is StrList
        assert sd[0] == "123"
        assert sd[1] == "456"

        sd = pickle.loads(pickle.dumps(sd))

        assert sd.type is str
        assert type(sd) is StrList
        assert sd[0] == "123"
        assert sd[1] == "456"

    def test_common_checked_shared_list_invalid_parameters(self):
        with self.assertRaisesRegex(TypeError, "must be parametrized"):
            self.BaseList()

        with self.assertRaisesRegex(TypeError, "expects one type parameter"):
            self.BaseList[int, int]()

        with self.assertRaisesRegex(TypeError, "expects types"):
            self.BaseList[1]()

        with self.assertRaisesRegex(TypeError, "already parametrized"):
            self.BaseList[int][int]


class FrozenCheckedListTests(BaseCheckedListTests):
    BaseList = FrozenCheckedList

    def test_common_checked_frozenlist_basics(self) -> None:
        StrList = self.BaseList[str]
        sl = StrList(["1", "2"])
        with self.assertRaises(AttributeError):
            sl.append("3")


class CheckedListTests(BaseCheckedListTests):
    BaseList = CheckedList

    def test_common_checked_checkedlist_basics(self) -> None:
        StrList = self.BaseList[str]
        tl = StrList()
        tl.append("1")
        tl.extend(("2", "3"))
        tl += ["4"]
        tl += ("5",)
        tl = tl + ("6",)
        tl = ("0",) + tl
        tl.insert(0, "-1")
        assert tl == ["-1", "0", "1", "2", "3", "4", "5", "6"]
        del tl[1]
        assert tl == ["-1", "1", "2", "3", "4", "5", "6"]
        del tl[1:3]
        assert tl == ["-1", "3", "4", "5", "6"]
        tl[2] = "X"
        assert tl == ["-1", "3", "X", "5", "6"]
        tl[1:4] = ("A", "B", "C")
        assert tl == ["-1", "A", "B", "C", "6"]
        tl *= 2
        assert tl == ["-1", "A", "B", "C", "6", "-1", "A", "B", "C", "6"]
        tl.sort()
        assert tl == ["-1", "-1", "6", "6", "A", "A", "B", "B", "C", "C"]

        with self.assertRaises(ValueError):
            tl.append(42)

        with self.assertRaises(ValueError):
            tl.extend((42,))

        with self.assertRaises(ValueError):
            tl.insert(0, 42)

        with self.assertRaises(ValueError):
            tl += (42,)

        with self.assertRaises(ValueError):
            tl = tl + (42,)

        with self.assertRaises(ValueError):
            tl = (42,) + tl


class BaseCheckedSetTests(unittest.TestCase):
    BaseSet = FrozenCheckedSet

    def test_common_checked_shared_set_basics(self) -> None:
        StrSet = self.BaseSet[str]
        s1 = StrSet("sphinx of black quartz judge my vow")
        assert s1 == set("abcdefghijklmnopqrstuvwxyz ")
        s2 = StrSet("hunter2")
        assert (s1 & s2) == StrSet("hunter")
        assert type(s1 & s2) is StrSet
        assert (s1 | s2) == set("abcdefghijklmnopqrstuvwxyz 2")
        assert type(s1 | s2) is StrSet
        assert (s1 - s2) == set("abcdfgijklmopqsvwxyz ")
        assert type(s1 - s2) is StrSet
        assert (set("hunter2") - s1) == StrSet("2")
        assert type(set("hunter2") - s1) is StrSet

        class Foo:
            def __repr__(self):
                return self.__class__.__name__

        class Bar(Foo):
            def __eq__(self, other):
                return isinstance(other, Bar)

            def __hash__(self):
                return 1

        FooSet = self.BaseSet[Foo]

        tl = FooSet([Bar(), Foo(), Bar()])
        tl2 = FooSet(tl | {Foo()})
        assert len(tl) == 2
        assert len(tl ^ tl2) == 1
        assert tl.issuperset({Bar()})
        assert tl.issubset(tl2)
        # We have to do some gymnastics due to sets being unordered.
        expected = {"{Bar, Foo}", "{Foo, Bar}"}
        assert str(tl) in expected
        cls_name = self.BaseSet.__name__
        expected_template = (
            f"edb.common.checked.{cls_name}[common.test_checked."
            "BaseCheckedSetTests.test_common_checked_shared_set_basics."
            "<locals>.Foo]({})"
        )
        assert repr(tl) in {expected_template.format(e) for e in expected}


class FrozenCheckedSetTests(BaseCheckedSetTests):
    BaseSet = FrozenCheckedSet


class CheckedSetTests(BaseCheckedSetTests):
    BaseSet = CheckedSet

    def test_common_checked_checkedset_basics(self) -> None:
        StrSet = self.BaseSet[str]
        tl = StrSet()
        tl.add("1")
        tl.update(("2", "3"))
        tl |= ["4"]
        tl |= ("5",)
        tl = tl | StrSet(["6"])
        tl = {"0"} | tl
        assert set(tl) == {"0", "1", "2", "3", "4", "5", "6"}

        tl = "67896789" - tl  # sic, TypedSet used to coerce arguments, too.
        assert tl == {"7", "8", "9"}
        assert set(tl - {"8", "9"}) == {"7"}

        assert set(tl ^ {"8", "9", "10"}) == {"7", "10"}
        assert set({"8", "9", "10"} ^ tl) == {"7", "10"}
        tl -= {"8"}
        assert tl == StrSet("79")

        with self.assertRaises(ValueError):
            tl.add(42)

        with self.assertRaises(ValueError):
            tl.update((42,))

        with self.assertRaises(ValueError):
            tl |= {42}

        with self.assertRaises(ValueError):
            tl = tl | {42}

        with self.assertRaises(ValueError):
            tl = {42} | tl

        with self.assertRaises(ValueError):
            tl = {42} ^ tl

        with self.assertRaises(ValueError):
            tl &= {42}

        with self.assertRaises(ValueError):
            tl ^= {42}

    def test_common_checkedset_pickling(self):
        StrSet = self.BaseSet[str]
        sd = StrSet({"123", "456"})

        assert sd.type is str
        assert type(sd) is StrSet
        assert "123" in sd
        assert "456" in sd

        sd = pickle.loads(pickle.dumps(sd))

        assert sd.type is str
        assert type(sd) is StrSet
        assert "123" in sd
        assert "456" in sd
