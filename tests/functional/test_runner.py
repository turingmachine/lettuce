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
import os
import sys
import couleur
import lettuce

from StringIO import StringIO
from os.path import dirname, abspath, join
from nose.tools import assert_equals, with_setup, assert_raises
from lettuce.fs import FeatureLoader
from lettuce.core import Feature, fs, StepDefinition
from lettuce.terrain import world
from lettuce import Runner

from tests.asserts import assert_lines
from tests.asserts import assert_stderr
from tests.asserts import prepare_stderr
from tests.asserts import prepare_stdout
from tests.asserts import assert_stderr_lines
from tests.asserts import assert_stdout_lines
from tests.asserts import assert_stdout_lines_with_traceback

current_dir = abspath(dirname(__file__))
lettuce_dir = abspath(dirname(lettuce.__file__))
ojoin = lambda *x: join(current_dir, 'output_features', *x)
sjoin = lambda *x: join(current_dir, 'syntax_features', *x)
lettuce_path = lambda *x: fs.relpath(join(lettuce_dir, *x))

call_line = StepDefinition.__call__.im_func.func_code.co_firstlineno + 5

def feature_name(name):
    return join(abspath(dirname(__file__)), 'output_features', name, "%s.feature" % name)

def syntax_feature_name(name):
    return sjoin(name, "%s.feature" % name)

@with_setup(prepare_stderr)
def test_try_to_import_terrain():
    "Runner tries to import terrain, but has a nice output when it fail"
    sandbox_path = ojoin('..', 'sandbox')
    original_path = abspath(".")
    os.chdir(sandbox_path)

    try:
        Runner(".")
        raise AssertionError('The runner should raise ImportError !')
    except SystemExit:
        assert_stderr(
            'Lettuce has tried to load the conventional environment module ' \
            '"terrain"\n'
            'but it has errors, check its contents and try to run lettuce again.\n'
        )

    finally:
        os.chdir(original_path)

def test_feature_representation_without_colors():
    "Feature represented without colors"
    feature_file = ojoin('..', 'simple_features', '1st_feature_dir', 'some.feature')

    feature = Feature.from_file(feature_file)
    assert_lines(
        feature.represented(),
        "Feature: Addition                                      # tests/functional/simple_features/1st_feature_dir/some.feature:5\n"
        "  In order to avoid silly mistakes                     # tests/functional/simple_features/1st_feature_dir/some.feature:6\n"
        "  As a math idiot                                      # tests/functional/simple_features/1st_feature_dir/some.feature:7\n"
        "  I want to be told the sum of two numbers             # tests/functional/simple_features/1st_feature_dir/some.feature:8\n"
    )

def test_scenario_outline_representation_without_colors():
    "Scenario Outline represented without colors"
    feature_file = ojoin('..', 'simple_features', '1st_feature_dir', 'some.feature')

    feature = Feature.from_file(feature_file)
    assert_equals(
        feature.scenarios[0].represented(),
        "  Scenario Outline: Add two numbers                    # tests/functional/simple_features/1st_feature_dir/some.feature:10\n"
    )

def test_scenario_representation_without_colors():
    "Scenario represented without colors"
    feature_file = ojoin('runner_features', 'first.feature')

    feature = Feature.from_file(feature_file)
    assert_equals(
        feature.scenarios[0].represented(),
        "  Scenario: Do nothing                   # tests/functional/output_features/runner_features/first.feature:6\n"
    )

def test_undefined_step_represent_string():
    "Undefined step represented without colors"
    feature_file = ojoin('runner_features', 'first.feature')

    feature = Feature.from_file(feature_file)
    step = feature.scenarios[0].steps[0]
    assert_equals(
        step.represent_string(step.sentence),
        "    Given I do nothing                   # tests/functional/output_features/runner_features/first.feature:7\n"
    )

    assert_equals(
        step.represent_string("foo bar"),
        "    foo bar                              # tests/functional/output_features/runner_features/first.feature:7\n"
    )

def test_defined_step_represent_string():
    "Defined step represented without colors"
    feature_file = ojoin('runner_features', 'first.feature')
    feature_dir = ojoin('runner_features')
    loader = FeatureLoader(feature_dir)
    world._output = StringIO()
    world._is_colored = False
    loader.find_and_load_step_definitions()

    feature = Feature.from_file(feature_file)
    step = feature.scenarios[0].steps[0]
    step.run(True)

    assert_equals(
       step.represent_string(step.sentence),
        "    Given I do nothing                   # tests/functional/output_features/runner_features/dumb_steps.py:6\n"
    )

@with_setup(prepare_stdout)
def test_output_with_success_colorless():
    "Testing the colorless output of a successful feature"

    runner = Runner(join(abspath(dirname(__file__)), 'output_features', 'runner_features'), verbosity=3)
    runner.run()

    assert_stdout_lines(
        "\n"
        "Feature: Dumb feature                    # tests/functional/output_features/runner_features/first.feature:1\n"
        "  In order to test success               # tests/functional/output_features/runner_features/first.feature:2\n"
        "  As a programmer                        # tests/functional/output_features/runner_features/first.feature:3\n"
        "  I want to see that the output is green # tests/functional/output_features/runner_features/first.feature:4\n"
        "\n"
        "  Scenario: Do nothing                   # tests/functional/output_features/runner_features/first.feature:6\n"
        "    Given I do nothing                   # tests/functional/output_features/runner_features/dumb_steps.py:6\n"
        "\n"
        "1 feature (1 passed)\n"
        "1 scenario (1 passed)\n"
        "1 step (1 passed)\n"
    )

@with_setup(prepare_stdout)
def test_output_with_success_colorful():
    "Testing the output of a successful feature"

    runner = Runner(join(abspath(dirname(__file__)), 'output_features', 'runner_features'), verbosity=4)
    couleur.proxy(sys.stdout).disable()
    runner.run()

    assert_stdout_lines(
        "\n" \
        "#{bold}#{white}Feature: Dumb feature                    #{bold}#{black}# tests/functional/output_features/runner_features/first.feature:1#{reset}\n" \
        "#{bold}#{white}  In order to test success               #{bold}#{black}# tests/functional/output_features/runner_features/first.feature:2#{reset}\n" \
        "#{bold}#{white}  As a programmer                        #{bold}#{black}# tests/functional/output_features/runner_features/first.feature:3#{reset}\n" \
        "#{bold}#{white}  I want to see that the output is green #{bold}#{black}# tests/functional/output_features/runner_features/first.feature:4#{reset}\n" \
        "\n" \
        "#{bold}#{white}  Scenario: Do nothing                   #{bold}#{black}# tests/functional/output_features/runner_features/first.feature:6#{reset}\n" \
        "#{bold}#{black}    Given I do nothing                   #{bold}#{black}# tests/functional/output_features/runner_features/dumb_steps.py:6#{reset}\n" \
        "#{up}#{bold}#{green}    Given I do nothing                   #{bold}#{black}# tests/functional/output_features/runner_features/dumb_steps.py:6#{reset}\n" \
        "\n" \
        "#{bold}#{white}1 feature (#{bold}#{green}1 passed#{bold}#{white})#{reset}\n" \
        "#{bold}#{white}1 scenario (#{bold}#{green}1 passed#{bold}#{white})#{reset}\n" \
        "#{bold}#{white}1 step (#{bold}#{green}1 passed#{bold}#{white})#{reset}\n"
    )

@with_setup(prepare_stdout)
def test_output_with_success_colorless_many_features():
    "Testing the output of many successful features"
    runner = Runner(join(abspath(dirname(__file__)), 'output_features', 'many_successful_features'), verbosity=3)
    runner.run()

    assert_stdout_lines(
        "\n"
        "Feature: First feature, of many              # tests/functional/output_features/many_successful_features/one.feature:1\n"
        "  In order to make lettuce more robust       # tests/functional/output_features/many_successful_features/one.feature:2\n"
        "  As a programmer                            # tests/functional/output_features/many_successful_features/one.feature:3\n"
        "  I want to test its output on many features # tests/functional/output_features/many_successful_features/one.feature:4\n"
        "\n"
        "  Scenario: Do nothing                       # tests/functional/output_features/many_successful_features/one.feature:6\n"
        "    Given I do nothing                       # tests/functional/output_features/many_successful_features/dumb_steps.py:6\n"
        "    Then I see that the test passes          # tests/functional/output_features/many_successful_features/dumb_steps.py:8\n"
        "\n"
        "Feature: Second feature, of many    # tests/functional/output_features/many_successful_features/two.feature:1\n"
        "  I just want to see it green :)    # tests/functional/output_features/many_successful_features/two.feature:2\n"
        "\n"
        "  Scenario: Do nothing              # tests/functional/output_features/many_successful_features/two.feature:4\n"
        "    Given I do nothing              # tests/functional/output_features/many_successful_features/dumb_steps.py:6\n"
        "    Then I see that the test passes # tests/functional/output_features/many_successful_features/dumb_steps.py:8\n"
        "\n"
        "2 features (2 passed)\n"
        "2 scenarios (2 passed)\n"
        "4 steps (4 passed)\n"
    )

@with_setup(prepare_stdout)
def test_output_with_success_colorful_many_features():
    "Testing the colorful output of many successful features"

    runner = Runner(join(abspath(dirname(__file__)), 'output_features', 'many_successful_features'), verbosity=4)
    couleur.proxy(sys.stdout).disable()
    runner.run()

    assert_stdout_lines(
        "\n"
        "#{bold}#{white}Feature: First feature, of many              #{bold}#{black}# tests/functional/output_features/many_successful_features/one.feature:1#{reset}\n"
        "#{bold}#{white}  In order to make lettuce more robust       #{bold}#{black}# tests/functional/output_features/many_successful_features/one.feature:2#{reset}\n"
        "#{bold}#{white}  As a programmer                            #{bold}#{black}# tests/functional/output_features/many_successful_features/one.feature:3#{reset}\n"
        "#{bold}#{white}  I want to test its output on many features #{bold}#{black}# tests/functional/output_features/many_successful_features/one.feature:4#{reset}\n"
        "\n"
        "#{bold}#{white}  Scenario: Do nothing                       #{bold}#{black}# tests/functional/output_features/many_successful_features/one.feature:6#{reset}\n"
        "#{bold}#{black}    Given I do nothing                       #{bold}#{black}# tests/functional/output_features/many_successful_features/dumb_steps.py:6#{reset}\n"
        "#{up}#{bold}#{green}    Given I do nothing                       #{bold}#{black}# tests/functional/output_features/many_successful_features/dumb_steps.py:6#{reset}\n"
        "#{bold}#{black}    Then I see that the test passes          #{bold}#{black}# tests/functional/output_features/many_successful_features/dumb_steps.py:8#{reset}\n"
        "#{up}#{bold}#{green}    Then I see that the test passes          #{bold}#{black}# tests/functional/output_features/many_successful_features/dumb_steps.py:8#{reset}\n"
        "\n"
        "#{bold}#{white}Feature: Second feature, of many    #{bold}#{black}# tests/functional/output_features/many_successful_features/two.feature:1#{reset}\n"
        "#{bold}#{white}  I just want to see it green :)    #{bold}#{black}# tests/functional/output_features/many_successful_features/two.feature:2#{reset}\n"
        "\n"
        "#{bold}#{white}  Scenario: Do nothing              #{bold}#{black}# tests/functional/output_features/many_successful_features/two.feature:4#{reset}\n"
        "#{bold}#{black}    Given I do nothing              #{bold}#{black}# tests/functional/output_features/many_successful_features/dumb_steps.py:6#{reset}\n"
        "#{up}#{bold}#{green}    Given I do nothing              #{bold}#{black}# tests/functional/output_features/many_successful_features/dumb_steps.py:6#{reset}\n"
        "#{bold}#{black}    Then I see that the test passes #{bold}#{black}# tests/functional/output_features/many_successful_features/dumb_steps.py:8#{reset}\n"
        "#{up}#{bold}#{green}    Then I see that the test passes #{bold}#{black}# tests/functional/output_features/many_successful_features/dumb_steps.py:8#{reset}\n"
        "\n"
        "#{bold}#{white}2 features (#{bold}#{green}2 passed#{bold}#{white})#{reset}\n" \
        "#{bold}#{white}2 scenarios (#{bold}#{green}2 passed#{bold}#{white})#{reset}\n" \
        "#{bold}#{white}4 steps (#{bold}#{green}4 passed#{bold}#{white})#{reset}\n"
    )

@with_setup(prepare_stdout)
def test_output_when_could_not_find_features():
    "Testing the colorful output of many successful features"

    path = fs.relpath(join(abspath(dirname(__file__)), 'unexistent-folder'))
    runner = Runner(path, verbosity=4)
    couleur.proxy(sys.stdout).disable()
    runner.run()

    assert_stdout_lines(
        '#{bold}#{red}Oops!#{reset}\n'
        '#{bold}#{white}could not find features at #{bold}#{yellow}./%s#{reset}\n' % path
    )

@with_setup(prepare_stdout)
def test_output_when_could_not_find_features_colorless():
    "Testing the colorful output of many successful features colorless"

    path = fs.relpath(join(abspath(dirname(__file__)), 'unexistent-folder'))
    runner = Runner(path, verbosity=3)
    runner.run()

    assert_stdout_lines(
        'Oops!\n'
        'could not find features at ./%s\n' % path
    )

@with_setup(prepare_stdout)
def test_output_with_success_colorless_with_table():
    "Testing the colorless output of success with table"

    runner = Runner(feature_name('success_table'), verbosity=3)
    runner.run()

    assert_stdout_lines(
        '\n'
        'Feature: Table Success           # tests/functional/output_features/success_table/success_table.feature:1\n'
        '\n'
        '  Scenario: Add two numbers      # tests/functional/output_features/success_table/success_table.feature:2\n'
        '    Given I have 0 bucks         # tests/functional/output_features/success_table/success_table_steps.py:28\n'
        '    And that I have these items: # tests/functional/output_features/success_table/success_table_steps.py:32\n'
        '      | name    | price  |\n'
        '      | Porsche | 200000 |\n'
        '      | Ferrari | 400000 |\n'
        '    When I sell the "Ferrari"    # tests/functional/output_features/success_table/success_table_steps.py:42\n'
        '    Then I have 400000 bucks     # tests/functional/output_features/success_table/success_table_steps.py:28\n'
        '    And my garage contains:      # tests/functional/output_features/success_table/success_table_steps.py:47\n'
        '      | name    | price  |\n'
        '      | Porsche | 200000 |\n'
        '\n'
        '1 feature (1 passed)\n'
        '1 scenario (1 passed)\n'
        '5 steps (5 passed)\n'
    )

@with_setup(prepare_stdout)
def test_output_with_success_colorful_with_table():
    "Testing the colorful output of success with table"

    runner = Runner(feature_name('success_table'), verbosity=4)
    couleur.proxy(sys.stdout).disable()
    runner.run()

    assert_stdout_lines(
        '\n'
        '#{bold}#{white}Feature: Table Success           #{bold}#{black}# tests/functional/output_features/success_table/success_table.feature:1#{reset}\n'
        '\n'
        '#{bold}#{white}  Scenario: Add two numbers      #{bold}#{black}# tests/functional/output_features/success_table/success_table.feature:2#{reset}\n'
        '#{bold}#{black}    Given I have 0 bucks         #{bold}#{black}# tests/functional/output_features/success_table/success_table_steps.py:28#{reset}\n'
        '#{up}#{bold}#{green}    Given I have 0 bucks         #{bold}#{black}# tests/functional/output_features/success_table/success_table_steps.py:28#{reset}\n'
        '#{bold}#{black}    And that I have these items: #{bold}#{black}# tests/functional/output_features/success_table/success_table_steps.py:32#{reset}\n'
        '#{bold}#{black}     #{bold}#{white} |#{bold}#{black} name   #{bold}#{white} |#{bold}#{black} price #{bold}#{white} |#{bold}#{black}#{reset}\n'
        '#{bold}#{black}     #{bold}#{white} |#{bold}#{black} Porsche#{bold}#{white} |#{bold}#{black} 200000#{bold}#{white} |#{bold}#{black}#{reset}\n'
        '#{bold}#{black}     #{bold}#{white} |#{bold}#{black} Ferrari#{bold}#{white} |#{bold}#{black} 400000#{bold}#{white} |#{bold}#{black}#{reset}\n'
        '#{up}#{up}#{up}#{up}#{bold}#{green}    And that I have these items: #{bold}#{black}# tests/functional/output_features/success_table/success_table_steps.py:32#{reset}\n'
        '#{bold}#{green}     #{bold}#{white} |#{bold}#{green} name   #{bold}#{white} |#{bold}#{green} price #{bold}#{white} |#{bold}#{green}#{reset}\n'
        '#{bold}#{green}     #{bold}#{white} |#{bold}#{green} Porsche#{bold}#{white} |#{bold}#{green} 200000#{bold}#{white} |#{bold}#{green}#{reset}\n'
        '#{bold}#{green}     #{bold}#{white} |#{bold}#{green} Ferrari#{bold}#{white} |#{bold}#{green} 400000#{bold}#{white} |#{bold}#{green}#{reset}\n'
        '#{bold}#{black}    When I sell the "Ferrari"    #{bold}#{black}# tests/functional/output_features/success_table/success_table_steps.py:42#{reset}\n'
        '#{up}#{bold}#{green}    When I sell the "Ferrari"    #{bold}#{black}# tests/functional/output_features/success_table/success_table_steps.py:42#{reset}\n'
        '#{bold}#{black}    Then I have 400000 bucks     #{bold}#{black}# tests/functional/output_features/success_table/success_table_steps.py:28#{reset}\n'
        '#{up}#{bold}#{green}    Then I have 400000 bucks     #{bold}#{black}# tests/functional/output_features/success_table/success_table_steps.py:28#{reset}\n'
        '#{bold}#{black}    And my garage contains:      #{bold}#{black}# tests/functional/output_features/success_table/success_table_steps.py:47#{reset}\n'
        '#{bold}#{black}     #{bold}#{white} |#{bold}#{black} name   #{bold}#{white} |#{bold}#{black} price #{bold}#{white} |#{bold}#{black}#{reset}\n'
        '#{bold}#{black}     #{bold}#{white} |#{bold}#{black} Porsche#{bold}#{white} |#{bold}#{black} 200000#{bold}#{white} |#{bold}#{black}#{reset}\n'
        '#{up}#{up}#{up}#{bold}#{green}    And my garage contains:      #{bold}#{black}# tests/functional/output_features/success_table/success_table_steps.py:47#{reset}\n'
        '#{bold}#{green}     #{bold}#{white} |#{bold}#{green} name   #{bold}#{white} |#{bold}#{green} price #{bold}#{white} |#{bold}#{green}#{reset}\n'
        '#{bold}#{green}     #{bold}#{white} |#{bold}#{green} Porsche#{bold}#{white} |#{bold}#{green} 200000#{bold}#{white} |#{bold}#{green}#{reset}\n'
        '\n'
        "#{bold}#{white}1 feature (#{bold}#{green}1 passed#{bold}#{white})#{reset}\n" \
        "#{bold}#{white}1 scenario (#{bold}#{green}1 passed#{bold}#{white})#{reset}\n" \
        "#{bold}#{white}5 steps (#{bold}#{green}5 passed#{bold}#{white})#{reset}\n"
    )

@with_setup(prepare_stdout)
def test_output_with_failed_colorless_with_table():
    "Testing the colorless output of failed with table"

    runner = Runner(feature_name('failed_table'), verbosity=3)
    runner.run()

    assert_stdout_lines_with_traceback(
        "\n"
        "Feature: Table Fail                           # tests/functional/output_features/failed_table/failed_table.feature:1\n"
        "\n"
        "  Scenario: See it fail                       # tests/functional/output_features/failed_table/failed_table.feature:2\n"
        "    Given I have a dumb step that passes      # tests/functional/output_features/failed_table/failed_table_steps.py:20\n"
        "    And this one fails                        # tests/functional/output_features/failed_table/failed_table_steps.py:24\n"
        "    Traceback (most recent call last):\n"
        '      File "%(lettuce_core_file)s", line %(call_line)d, in __call__\n'
        "        ret = self.function(self.step, *args, **kw)\n"
        '      File "%(step_file)s", line 25, in tof\n'
        "        assert False\n"
        "    AssertionError\n"
        "    Then this one will be skipped             # tests/functional/output_features/failed_table/failed_table_steps.py:28\n"
        "    And this one will be skipped              # tests/functional/output_features/failed_table/failed_table_steps.py:28\n"
        "    And this one does not even has definition # tests/functional/output_features/failed_table/failed_table.feature:12\n"
        "\n"
        "1 feature (0 passed)\n"
        "1 scenario (0 passed)\n"
        "5 steps (1 failed, 2 skipped, 1 undefined, 1 passed)\n"
        "\n"
        "You can implement step definitions for undefined steps with these snippets:\n"
        "\n"
        "# -*- coding: utf-8 -*-\n"
        "from lettuce import step\n"
        "\n"
        "@step(u'And this one does not even has definition')\n"
        "def and_this_one_does_not_even_has_definition(step):\n"
        "    pass\n" % {
            'lettuce_core_file': lettuce_path('core.py'),
            'step_file': abspath(lettuce_path('..', 'tests', 'functional', 'output_features', 'failed_table', 'failed_table_steps.py')),
            'call_line':call_line,
        }
    )

@with_setup(prepare_stdout)
def test_output_with_failed_colorful_with_table():
    "Testing the colorful output of failed with table"

    runner = Runner(feature_name('failed_table'), verbosity=4)
    couleur.proxy(sys.stdout).disable()
    runner.run()

    assert_stdout_lines_with_traceback(
        "\n"
        "#{bold}#{white}Feature: Table Fail                           #{bold}#{black}# tests/functional/output_features/failed_table/failed_table.feature:1#{reset}\n"
        "\n"
        "#{bold}#{white}  Scenario: See it fail                       #{bold}#{black}# tests/functional/output_features/failed_table/failed_table.feature:2#{reset}\n"
        "#{bold}#{black}    Given I have a dumb step that passes      #{bold}#{black}# tests/functional/output_features/failed_table/failed_table_steps.py:20#{reset}\n"
        "#{up}#{bold}#{green}    Given I have a dumb step that passes      #{bold}#{black}# tests/functional/output_features/failed_table/failed_table_steps.py:20#{reset}\n"
        "#{bold}#{black}    And this one fails                        #{bold}#{black}# tests/functional/output_features/failed_table/failed_table_steps.py:24#{reset}\n"
        "#{up}#{reset}#{red}    And this one fails                        #{bold}#{red}#{on:yellow}# tests/functional/output_features/failed_table/failed_table_steps.py:24#{reset}\n"
        "#{bold}#{red}    Traceback (most recent call last):\n"
        '      File "%(lettuce_core_file)s", line %(call_line)d, in __call__\n'
        "        ret = self.function(self.step, *args, **kw)\n"
        '      File "%(step_file)s", line 25, in tof\n'
        "        assert False\n"
        "    AssertionError#{reset}\n"
        "#{bold}#{black}    Then this one will be skipped             #{bold}#{black}# tests/functional/output_features/failed_table/failed_table_steps.py:28#{reset}\n"
        "#{up}#{reset}#{cyan}    Then this one will be skipped             #{bold}#{black}# tests/functional/output_features/failed_table/failed_table_steps.py:28#{reset}\n"
        "#{bold}#{black}    And this one will be skipped              #{bold}#{black}# tests/functional/output_features/failed_table/failed_table_steps.py:28#{reset}\n"
        "#{up}#{reset}#{cyan}    And this one will be skipped              #{bold}#{black}# tests/functional/output_features/failed_table/failed_table_steps.py:28#{reset}\n"
        "#{reset}#{yellow}    And this one does not even has definition #{bold}#{black}# tests/functional/output_features/failed_table/failed_table.feature:12#{reset}\n"
        "\n"
        "#{bold}#{white}1 feature (#{reset}#{red}0 passed#{bold}#{white})#{reset}\n"
        "#{bold}#{white}1 scenario (#{reset}#{red}0 passed#{bold}#{white})#{reset}\n"
        "#{bold}#{white}5 steps (#{reset}#{red}1 failed#{bold}#{white}, #{reset}#{cyan}2 skipped#{bold}#{white}, #{reset}#{yellow}1 undefined#{bold}#{white}, #{bold}#{green}1 passed#{bold}#{white})#{reset}\n"
        "\n"
        "#{reset}#{yellow}You can implement step definitions for undefined steps with these snippets:\n"
        "\n"
        "# -*- coding: utf-8 -*-\n"
        "from lettuce import step\n"
        "\n"
        "@step(u'And this one does not even has definition')\n"
        "def and_this_one_does_not_even_has_definition(step):\n"
        "    pass#{reset}"
        "\n" % {
            'lettuce_core_file': lettuce_path('core.py'),
            'step_file': abspath(lettuce_path('..', 'tests', 'functional', 'output_features', 'failed_table', 'failed_table_steps.py')),
            'call_line':call_line,
        }
    )

@with_setup(prepare_stdout)
def test_output_with_successful_outline_colorless():
    "Testing the colorless output of a scenario outline"

    runner = Runner(feature_name('success_outline'), verbosity=3)
    runner.run()

    assert_stdout_lines(
        '\n'
        'Feature: Successful Scenario Outline                          # tests/functional/output_features/success_outline/success_outline.feature:1\n'
        '  As lettuce author                                           # tests/functional/output_features/success_outline/success_outline.feature:2\n'
        '  In order to finish the first release                        # tests/functional/output_features/success_outline/success_outline.feature:3\n'
        '  I want to make scenario outlines work :)                    # tests/functional/output_features/success_outline/success_outline.feature:4\n'
        '\n'
        '  Scenario Outline: fill a web form                           # tests/functional/output_features/success_outline/success_outline.feature:6\n'
        '    Given I open browser at "http://www.my-website.com/"      # tests/functional/output_features/success_outline/success_outline_steps.py:21\n'
        '    And click on "sign-up"                                    # tests/functional/output_features/success_outline/success_outline_steps.py:25\n'
        '    When I fill the field "username" with "<username>"        # tests/functional/output_features/success_outline/success_outline_steps.py:29\n'
        '    And I fill the field "password" with "<password>"         # tests/functional/output_features/success_outline/success_outline_steps.py:29\n'
        '    And I fill the field "password-confirm" with "<password>" # tests/functional/output_features/success_outline/success_outline_steps.py:29\n'
        '    And I fill the field "email" with "<email>"               # tests/functional/output_features/success_outline/success_outline_steps.py:29\n'
        '    And I click "done"                                        # tests/functional/output_features/success_outline/success_outline_steps.py:33\n'
        '    Then I see the title of the page is "<title>"             # tests/functional/output_features/success_outline/success_outline_steps.py:37\n'
        '\n'
        '  Examples:\n'
        '    | username | password | email          | title             |\n'
        '    | john     | doe-1234 | john@gmail.org | John \| My Website |\n'
        '    | mary     | wee-9876 | mary@email.com | Mary \| My Website |\n'
        '    | foo      | foo-bar  | foo@bar.com    | Foo \| My Website  |\n'
        '\n'
        '1 feature (1 passed)\n'
        '3 scenarios (3 passed)\n'
        '24 steps (24 passed)\n'
    )

@with_setup(prepare_stdout)
def test_output_with_successful_outline_colorful():
    "Testing the colorful output of a scenario outline"

    runner = Runner(feature_name('success_outline'), verbosity=4)
    couleur.proxy(sys.stdout).disable()
    runner.run()

    assert_stdout_lines_with_traceback(
        '\n'
        '#{bold}#{white}Feature: Successful Scenario Outline                          #{bold}#{black}# tests/functional/output_features/success_outline/success_outline.feature:1#{reset}\n'
        '#{bold}#{white}  As lettuce author                                           #{bold}#{black}# tests/functional/output_features/success_outline/success_outline.feature:2#{reset}\n'
        '#{bold}#{white}  In order to finish the first release                        #{bold}#{black}# tests/functional/output_features/success_outline/success_outline.feature:3#{reset}\n'
        '#{bold}#{white}  I want to make scenario outlines work :)                    #{bold}#{black}# tests/functional/output_features/success_outline/success_outline.feature:4#{reset}\n'
        '\n'
        '#{bold}#{white}  Scenario Outline: fill a web form                           #{bold}#{black}# tests/functional/output_features/success_outline/success_outline.feature:6#{reset}\n'
        '#{reset}#{cyan}    Given I open browser at "http://www.my-website.com/"      #{bold}#{black}# tests/functional/output_features/success_outline/success_outline_steps.py:21#{reset}\n'
        '#{reset}#{cyan}    And click on "sign-up"                                    #{bold}#{black}# tests/functional/output_features/success_outline/success_outline_steps.py:25#{reset}\n'
        '#{reset}#{cyan}    When I fill the field "username" with "<username>"        #{bold}#{black}# tests/functional/output_features/success_outline/success_outline_steps.py:29#{reset}\n'
        '#{reset}#{cyan}    And I fill the field "password" with "<password>"         #{bold}#{black}# tests/functional/output_features/success_outline/success_outline_steps.py:29#{reset}\n'
        '#{reset}#{cyan}    And I fill the field "password-confirm" with "<password>" #{bold}#{black}# tests/functional/output_features/success_outline/success_outline_steps.py:29#{reset}\n'
        '#{reset}#{cyan}    And I fill the field "email" with "<email>"               #{bold}#{black}# tests/functional/output_features/success_outline/success_outline_steps.py:29#{reset}\n'
        '#{reset}#{cyan}    And I click "done"                                        #{bold}#{black}# tests/functional/output_features/success_outline/success_outline_steps.py:33#{reset}\n'
        '#{reset}#{cyan}    Then I see the title of the page is "<title>"             #{bold}#{black}# tests/functional/output_features/success_outline/success_outline_steps.py:37#{reset}\n'
        '\n'
        '#{bold}#{white}  Examples:#{reset}\n'
        '#{reset}#{cyan}   #{bold}#{white} |#{reset}#{cyan} username#{bold}#{white} |#{reset}#{cyan} password#{bold}#{white} |#{reset}#{cyan} email         #{bold}#{white} |#{reset}#{cyan} title            #{bold}#{white} |#{reset}#{cyan}#{reset}\n'
        '#{bold}#{green}   #{bold}#{white} |#{bold}#{green} john    #{bold}#{white} |#{bold}#{green} doe-1234#{bold}#{white} |#{bold}#{green} john@gmail.org#{bold}#{white} |#{bold}#{green} John \| My Website#{bold}#{white} |#{bold}#{green}#{reset}\n'
        '#{bold}#{green}   #{bold}#{white} |#{bold}#{green} mary    #{bold}#{white} |#{bold}#{green} wee-9876#{bold}#{white} |#{bold}#{green} mary@email.com#{bold}#{white} |#{bold}#{green} Mary \| My Website#{bold}#{white} |#{bold}#{green}#{reset}\n'
        '#{bold}#{green}   #{bold}#{white} |#{bold}#{green} foo     #{bold}#{white} |#{bold}#{green} foo-bar #{bold}#{white} |#{bold}#{green} foo@bar.com   #{bold}#{white} |#{bold}#{green} Foo \| My Website #{bold}#{white} |#{bold}#{green}#{reset}\n'
        '\n'
        "#{bold}#{white}1 feature (#{bold}#{green}1 passed#{bold}#{white})#{reset}\n" \
        "#{bold}#{white}3 scenarios (#{bold}#{green}3 passed#{bold}#{white})#{reset}\n" \
        "#{bold}#{white}24 steps (#{bold}#{green}24 passed#{bold}#{white})#{reset}\n"
    )

@with_setup(prepare_stdout)
def test_output_with_failful_outline_colorless():
    "Testing the colorless output of a scenario outline"

    runner = Runner(feature_name('fail_outline'), verbosity=3)
    runner.run()

    assert_stdout_lines_with_traceback(
        '\n'
        'Feature: Failful Scenario Outline                             # tests/functional/output_features/fail_outline/fail_outline.feature:1\n'
        '  As lettuce author                                           # tests/functional/output_features/fail_outline/fail_outline.feature:2\n'
        '  In order to finish the first release                        # tests/functional/output_features/fail_outline/fail_outline.feature:3\n'
        '  I want to make scenario outlines work :)                    # tests/functional/output_features/fail_outline/fail_outline.feature:4\n'
        '\n'
        '  Scenario Outline: fill a web form                           # tests/functional/output_features/fail_outline/fail_outline.feature:6\n'
        '    Given I open browser at "http://www.my-website.com/"      # tests/functional/output_features/fail_outline/fail_outline_steps.py:21\n'
        '    And click on "sign-up"                                    # tests/functional/output_features/fail_outline/fail_outline_steps.py:25\n'
        '    When I fill the field "username" with "<username>"        # tests/functional/output_features/fail_outline/fail_outline_steps.py:29\n'
        '    And I fill the field "password" with "<password>"         # tests/functional/output_features/fail_outline/fail_outline_steps.py:29\n'
        '    And I fill the field "password-confirm" with "<password>" # tests/functional/output_features/fail_outline/fail_outline_steps.py:29\n'
        '    And I fill the field "email" with "<email>"               # tests/functional/output_features/fail_outline/fail_outline_steps.py:29\n'
        '    And I click "done"                                        # tests/functional/output_features/fail_outline/fail_outline_steps.py:33\n'
        '    Then I see the message "<message>"                        # tests/functional/output_features/fail_outline/fail_outline_steps.py:37\n'
        '\n'
        '  Examples:\n'
        '    | username | password | email          | message       |\n'
        '    | john     | doe-1234 | john@gmail.org | Welcome, John |\n'
        '    | mary     | wee-9876 | mary@email.com | Welcome, Mary |\n'
        "    Traceback (most recent call last):\n"
        '      File "%(lettuce_core_file)s", line %(call_line)d, in __call__\n'
        "        ret = self.function(self.step, *args, **kw)\n"
        '      File "%(step_file)s", line 30, in when_i_fill_the_field_x_with_y\n'
        "        if field == 'password' and value == 'wee-9876':  assert False\n"
        "    AssertionError\n"
        '    | foo      | foo-bar  | foo@bar.com    | Welcome, Foo  |\n'
        '\n'
        '1 feature (0 passed)\n'
        '3 scenarios (2 passed)\n'
        '24 steps (1 failed, 4 skipped, 19 passed)\n' % {
            'lettuce_core_file': lettuce_path('core.py'),
            'step_file': abspath(lettuce_path('..', 'tests', 'functional', 'output_features', 'fail_outline', 'fail_outline_steps.py')),
            'call_line':call_line,
        }
    )

@with_setup(prepare_stdout)
def test_output_with_failful_outline_colorful():
    "Testing the colorful output of a scenario outline"

    runner = Runner(feature_name('fail_outline'), verbosity=4)
    couleur.proxy(sys.stdout).disable()
    runner.run()

    assert_stdout_lines_with_traceback(
        '\n'
        '#{bold}#{white}Feature: Failful Scenario Outline                             #{bold}#{black}# tests/functional/output_features/fail_outline/fail_outline.feature:1#{reset}\n'
        '#{bold}#{white}  As lettuce author                                           #{bold}#{black}# tests/functional/output_features/fail_outline/fail_outline.feature:2#{reset}\n'
        '#{bold}#{white}  In order to finish the first release                        #{bold}#{black}# tests/functional/output_features/fail_outline/fail_outline.feature:3#{reset}\n'
        '#{bold}#{white}  I want to make scenario outlines work :)                    #{bold}#{black}# tests/functional/output_features/fail_outline/fail_outline.feature:4#{reset}\n'
        '\n'
        '#{bold}#{white}  Scenario Outline: fill a web form                           #{bold}#{black}# tests/functional/output_features/fail_outline/fail_outline.feature:6#{reset}\n'
        '#{reset}#{cyan}    Given I open browser at "http://www.my-website.com/"      #{bold}#{black}# tests/functional/output_features/fail_outline/fail_outline_steps.py:21#{reset}\n'
        '#{reset}#{cyan}    And click on "sign-up"                                    #{bold}#{black}# tests/functional/output_features/fail_outline/fail_outline_steps.py:25#{reset}\n'
        '#{reset}#{cyan}    When I fill the field "username" with "<username>"        #{bold}#{black}# tests/functional/output_features/fail_outline/fail_outline_steps.py:29#{reset}\n'
        '#{reset}#{cyan}    And I fill the field "password" with "<password>"         #{bold}#{black}# tests/functional/output_features/fail_outline/fail_outline_steps.py:29#{reset}\n'
        '#{reset}#{cyan}    And I fill the field "password-confirm" with "<password>" #{bold}#{black}# tests/functional/output_features/fail_outline/fail_outline_steps.py:29#{reset}\n'
        '#{reset}#{cyan}    And I fill the field "email" with "<email>"               #{bold}#{black}# tests/functional/output_features/fail_outline/fail_outline_steps.py:29#{reset}\n'
        '#{reset}#{cyan}    And I click "done"                                        #{bold}#{black}# tests/functional/output_features/fail_outline/fail_outline_steps.py:33#{reset}\n'
        '#{reset}#{cyan}    Then I see the message "<message>"                        #{bold}#{black}# tests/functional/output_features/fail_outline/fail_outline_steps.py:37#{reset}\n'
        '\n'
        '#{bold}#{white}  Examples:#{reset}\n'
        '#{reset}#{cyan}   #{bold}#{white} |#{reset}#{cyan} username#{bold}#{white} |#{reset}#{cyan} password#{bold}#{white} |#{reset}#{cyan} email         #{bold}#{white} |#{reset}#{cyan} message      #{bold}#{white} |#{reset}#{cyan}#{reset}\n'
        '#{bold}#{green}   #{bold}#{white} |#{bold}#{green} john    #{bold}#{white} |#{bold}#{green} doe-1234#{bold}#{white} |#{bold}#{green} john@gmail.org#{bold}#{white} |#{bold}#{green} Welcome, John#{bold}#{white} |#{bold}#{green}#{reset}\n'
        '#{bold}#{green}   #{bold}#{white} |#{bold}#{green} mary    #{bold}#{white} |#{bold}#{green} wee-9876#{bold}#{white} |#{bold}#{green} mary@email.com#{bold}#{white} |#{bold}#{green} Welcome, Mary#{bold}#{white} |#{bold}#{green}#{reset}\n'
        "#{bold}#{red}    Traceback (most recent call last):\n"
        '      File "%(lettuce_core_file)s", line %(call_line)d, in __call__\n'
        "        ret = self.function(self.step, *args, **kw)\n"
        '      File "%(step_file)s", line 30, in when_i_fill_the_field_x_with_y\n'
        "        if field == 'password' and value == 'wee-9876':  assert False\n"
        "    AssertionError#{reset}\n"
        '#{bold}#{green}   #{bold}#{white} |#{bold}#{green} foo     #{bold}#{white} |#{bold}#{green} foo-bar #{bold}#{white} |#{bold}#{green} foo@bar.com   #{bold}#{white} |#{bold}#{green} Welcome, Foo #{bold}#{white} |#{bold}#{green}#{reset}\n'
        '\n'
        "#{bold}#{white}1 feature (#{reset}#{red}0 passed#{bold}#{white})#{reset}\n" \
        "#{bold}#{white}3 scenarios (#{bold}#{green}2 passed#{bold}#{white})#{reset}\n" \
        "#{bold}#{white}24 steps (#{reset}#{red}1 failed#{bold}#{white}, #{reset}#{cyan}4 skipped#{bold}#{white}, #{bold}#{green}19 passed#{bold}#{white})#{reset}\n" % {
            'lettuce_core_file': lettuce_path('core.py'),
            'step_file': abspath(lettuce_path('..', 'tests', 'functional', 'output_features', 'fail_outline', 'fail_outline_steps.py')),
            'call_line':call_line,
        }
    )

@with_setup(prepare_stderr)
def test_many_features_a_file():
    "syntax checking: Fail if a file has more than one feature"

    filename = syntax_feature_name('many_features_a_file')
    runner = Runner(filename)
    assert_raises(SystemExit, runner.run)

    assert_stderr_lines(
        'Syntax error at: %s\n'
        'A feature file must contain ONLY ONE feature!\n' % filename
    )

@with_setup(prepare_stderr)
def test_feature_without_name():
    "syntax checking: Fail on features without name"

    filename = syntax_feature_name('feature_without_name')
    runner = Runner(filename)
    assert_raises(SystemExit, runner.run)

    assert_stderr_lines(
        'Syntax error at: %s\n'
        'Features must have a name. e.g: "Feature: This is my name"\n'
        % filename
    )


@with_setup(prepare_stdout)
def test_output_snippets_with_groups_within_double_quotes_colorless():
    "Testing that the proposed snippet is clever enough to identify groups within double quotes. colorless"

    runner = Runner(feature_name('double-quoted-snippet'), verbosity=3)
    runner.run()

    assert_stdout_lines(
        u'\n'
        u'Feature: double-quoted snippet proposal                          # tests/functional/output_features/double-quoted-snippet/double-quoted-snippet.feature:1\n'
        u'\n'
        u'  Scenario: Propose matched groups                               # tests/functional/output_features/double-quoted-snippet/double-quoted-snippet.feature:2\n'
        u'    Given I have "stuff here" and "more @#$%ˆ& bizar sutff h3r3" # tests/functional/output_features/double-quoted-snippet/double-quoted-snippet.feature:3\n'
        u'\n'
        u'1 feature (0 passed)\n'
        u'1 scenario (0 passed)\n'
        u'1 step (1 undefined, 0 passed)\n'
        u'\n'
        u'You can implement step definitions for undefined steps with these snippets:\n'
        u'\n'
        u"# -*- coding: utf-8 -*-\n"
        u'from lettuce import step\n'
        u'\n'
        u'@step(u\'Given I have "(.*)" and "(.*)"\')\n'
        u'def given_i_have_group1_and_group2(step, group1, group2):\n'
        u'    pass\n'
    )

@with_setup(prepare_stdout)
def test_output_snippets_with_groups_within_double_quotes_colorful():
    "Testing that the proposed snippet is clever enough to identify groups within double quotes. colorful"

    runner = Runner(feature_name('double-quoted-snippet'), verbosity=4)
    couleur.proxy(sys.stdout).disable()
    runner.run()

    assert_stdout_lines(
        u'\n'
        u'#{bold}#{white}Feature: double-quoted snippet proposal                          #{bold}#{black}# tests/functional/output_features/double-quoted-snippet/double-quoted-snippet.feature:1#{reset}\n'
        u'\n'
        u'#{bold}#{white}  Scenario: Propose matched groups                               #{bold}#{black}# tests/functional/output_features/double-quoted-snippet/double-quoted-snippet.feature:2#{reset}\n'
        u'#{reset}#{yellow}    Given I have "stuff here" and "more @#$%ˆ& bizar sutff h3r3" #{bold}#{black}# tests/functional/output_features/double-quoted-snippet/double-quoted-snippet.feature:3#{reset}\n'
        u'\n'
        "#{bold}#{white}1 feature (#{reset}#{red}0 passed#{bold}#{white})#{reset}\n" \
        "#{bold}#{white}1 scenario (#{reset}#{red}0 passed#{bold}#{white})#{reset}\n" \
        "#{bold}#{white}1 step (#{reset}#{yellow}1 undefined#{bold}#{white}, #{bold}#{green}0 passed#{bold}#{white})#{reset}\n"
        u'\n'
        u'#{reset}#{yellow}You can implement step definitions for undefined steps with these snippets:\n'
        u'\n'
        u"# -*- coding: utf-8 -*-\n"
        u'from lettuce import step\n'
        u'\n'
        u'@step(u\'Given I have "(.*)" and "(.*)"\')\n'
        u'def given_i_have_group1_and_group2(step, group1, group2):\n'
        u'    pass#{reset}\n'
    )


@with_setup(prepare_stdout)
def test_output_snippets_with_groups_within_single_quotes_colorless():
    "Testing that the proposed snippet is clever enough to identify groups within single quotes. colorless"

    runner = Runner(feature_name('single-quoted-snippet'), verbosity=3)
    runner.run()

    assert_stdout_lines(
        u'\n'
        u'Feature: single-quoted snippet proposal                          # tests/functional/output_features/single-quoted-snippet/single-quoted-snippet.feature:1\n'
        u'\n'
        u'  Scenario: Propose matched groups                               # tests/functional/output_features/single-quoted-snippet/single-quoted-snippet.feature:2\n'
        u'    Given I have \'stuff here\' and \'more @#$%ˆ& bizar sutff h3r3\' # tests/functional/output_features/single-quoted-snippet/single-quoted-snippet.feature:3\n'
        u'\n'
        u'1 feature (0 passed)\n'
        u'1 scenario (0 passed)\n'
        u'1 step (1 undefined, 0 passed)\n'
        u'\n'
        u'You can implement step definitions for undefined steps with these snippets:\n'
        u'\n'
        u"# -*- coding: utf-8 -*-\n"
        u'from lettuce import step\n'
        u'\n'
        u'@step(u\'Given I have \\\'(.*)\\\' and \\\'(.*)\\\'\')\n'
        u'def given_i_have_group1_and_group2(step, group1, group2):\n'
        u'    pass\n'
    )

@with_setup(prepare_stdout)
def test_output_snippets_with_groups_within_single_quotes_colorful():
    "Testing that the proposed snippet is clever enough to identify groups within single quotes. colorful"

    runner = Runner(feature_name('single-quoted-snippet'), verbosity=4)
    couleur.proxy(sys.stdout).disable()
    runner.run()

    assert_stdout_lines(
        u'\n'
        u'#{bold}#{white}Feature: single-quoted snippet proposal                          #{bold}#{black}# tests/functional/output_features/single-quoted-snippet/single-quoted-snippet.feature:1#{reset}\n'
        u'\n'
        u'#{bold}#{white}  Scenario: Propose matched groups                               #{bold}#{black}# tests/functional/output_features/single-quoted-snippet/single-quoted-snippet.feature:2#{reset}\n'
        u'#{reset}#{yellow}    Given I have \'stuff here\' and \'more @#$%ˆ& bizar sutff h3r3\' #{bold}#{black}# tests/functional/output_features/single-quoted-snippet/single-quoted-snippet.feature:3#{reset}\n'
        u'\n'
        "#{bold}#{white}1 feature (#{reset}#{red}0 passed#{bold}#{white})#{reset}\n" \
        "#{bold}#{white}1 scenario (#{reset}#{red}0 passed#{bold}#{white})#{reset}\n" \
        "#{bold}#{white}1 step (#{reset}#{yellow}1 undefined#{bold}#{white}, #{bold}#{green}0 passed#{bold}#{white})#{reset}\n"
        u'\n'
        u'#{reset}#{yellow}You can implement step definitions for undefined steps with these snippets:\n'
        u'\n'
        u"# -*- coding: utf-8 -*-\n"
        u'from lettuce import step\n'
        u'\n'
        u'@step(u\'Given I have \\\'(.*)\\\' and \\\'(.*)\\\'\')\n'
        u'def given_i_have_group1_and_group2(step, group1, group2):\n'
        u'    pass#{reset}\n'
    )

@with_setup(prepare_stdout)
def test_output_snippets_with_groups_within_redundant_quotes():
    "Testing that the proposed snippet is clever enough to avoid duplicating the same snippet"

    runner = Runner(feature_name('redundant-steps-quotes'), verbosity=3)
    runner.run()

    assert_stdout_lines(
        u'\n'
        u'Feature: avoid duplicating same snippet                          # tests/functional/output_features/redundant-steps-quotes/redundant-steps-quotes.feature:1\n'
        u'\n'
        u'  Scenario: Propose matched groups                               # tests/functional/output_features/redundant-steps-quotes/redundant-steps-quotes.feature:2\n'
        u'    Given I have "stuff here" and "more @#$%ˆ& bizar sutff h3r3" # tests/functional/output_features/redundant-steps-quotes/redundant-steps-quotes.feature:3\n'
        u'    Given I have "blablabla" and "12345"                         # tests/functional/output_features/redundant-steps-quotes/redundant-steps-quotes.feature:4\n'
        u'\n'
        u'1 feature (0 passed)\n'
        u'1 scenario (0 passed)\n'
        u'2 steps (2 undefined, 0 passed)\n'
        u'\n'
        u'You can implement step definitions for undefined steps with these snippets:\n'
        u'\n'
        u"# -*- coding: utf-8 -*-\n"
        u'from lettuce import step\n'
        u'\n'
        u'@step(u\'Given I have "(.*)" and "(.*)"\')\n'
        u'def given_i_have_group1_and_group2(step, group1, group2):\n'
        u'    pass\n'
    )

@with_setup(prepare_stdout)
def test_output_snippets_with_normalized_unicode_names():
    "Testing that the proposed snippet is clever enough normalize method names even with latin accents"

    runner = Runner(feature_name('latin-accents'), verbosity=3)
    runner.run()

    assert_stdout_lines(
        u"\n"
        u"Funcionalidade: melhorar o output de snippets do lettuce                                      # tests/functional/output_features/latin-accents/latin-accents.feature:2\n"
        u"  Como autor do lettuce                                                                       # tests/functional/output_features/latin-accents/latin-accents.feature:3\n"
        u"  Eu quero ter um output refinado de snippets                                                 # tests/functional/output_features/latin-accents/latin-accents.feature:4\n"
        u"  Para melhorar, de uma forma geral, a vida do programador                                    # tests/functional/output_features/latin-accents/latin-accents.feature:5\n"
        u"\n"
        u"  Cenário: normalizar snippets com unicode                                                    # tests/functional/output_features/latin-accents/latin-accents.feature:7\n"
        u"    Dado que eu tenho palavrões e outras situações                                            # tests/functional/output_features/latin-accents/latin-accents.feature:8\n"
        u"    E várias palavras acentuadas são úteis, tais como: \"(é,não,léo,chororó,chácara,epígrafo)\" # tests/functional/output_features/latin-accents/latin-accents.feature:9\n"
        u"    Então eu fico felizão                                                                     # tests/functional/output_features/latin-accents/latin-accents.feature:10\n"
        u"\n"
        u"1 feature (0 passed)\n"
        u"1 scenario (0 passed)\n"
        u"3 steps (3 undefined, 0 passed)\n"
        u"\n"
        u"You can implement step definitions for undefined steps with these snippets:\n"
        u"\n"
        u"# -*- coding: utf-8 -*-\n"
        u"from lettuce import step\n"
        u"\n"
        u"@step(u'Dado que eu tenho palavrões e outras situações')\n"
        u"def dado_que_eu_tenho_palavroes_e_outras_situacoes(step):\n"
        u"    pass\n"
        u"@step(u'E várias palavras acentuadas são úteis, tais como: \"(.*)\"')\n"
        u"def e_varias_palavras_acentuadas_sao_uteis_tais_como_group1(step, group1):\n"
        u"    pass\n"
        u"@step(u'Então eu fico felizão')\n"
        u"def entao_eu_fico_felizao(step):\n"
        u"    pass\n"
    )
