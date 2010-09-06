# -*- coding: utf-8 -*-
# <Lettuce - Behaviour Driven Development for python>
# Copyright (C) <2010>  Gabriel Falcão <gabriel@nacaolivre.org>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
from nose.tools import assert_equals
from lettuce.core import Language

def test_language_is_english_by_default():
    "Language class is english by default"
    lang = Language()

    assert_equals(lang.code, 'en')
    assert_equals(lang.name, 'English')
    assert_equals(lang.native, 'English')
    assert_equals(lang.feature, 'Feature')
    assert_equals(lang.scenario, 'Scenario')
    assert_equals(lang.examples, 'Examples|Scenarios')
    assert_equals(lang.scenario_outline, 'Scenario Outline')
    assert_equals(repr(lang), '<Language "en">')

def test_language_has_first_of():
    "Language() can pick up first occurrece of a string"
    lang = Language()

    assert_equals(lang.first_of_examples, 'Examples')


def test_language_guess_from_string():
    "language should be able to guess from string"

    pt_br = """

    # language:           pt-br

    """

    lang_pt_br = Language.guess_from_string(pt_br)
    assert_equals(lang_pt_br.code, 'pt-br')

def test_language_guess_from_string_falls_back_to_english():
    "Language.guess_from_string falls back to english if there is no proper language string"

    weird = """

    # languag asdpt-br

    """

    lang_pt_br = Language.guess_from_string(weird)
    assert_equals(lang_pt_br.code, 'en')

