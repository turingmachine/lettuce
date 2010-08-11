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
import re
import sys
from lettuce import strings
from lettuce import core
from lettuce.terrain import after
from lettuce.terrain import before

def wrt(what):
    sys.stdout.write(what.encode('utf-8'))

def wrap_file_and_line(string, start, end):
    return re.sub(r'([#] [^:]+[:]\d+)', '%s\g<1>%s' % (start, end), string)

def wp(l):
    if l.startswith("#{bold}#{green}"):
        l = l.replace(" |", "#{bold}#{white} |#{bold}#{green}")
    if l.startswith("#{bold}#{cyan}"):
        l = l.replace(" |", "#{bold}#{white} |#{bold}#{cyan}")
    if l.startswith("#{reset}#{cyan}"):
        l = l.replace(" |", "#{bold}#{white} |#{reset}#{cyan}")
    if l.startswith("#{reset}#{red}"):
        l = l.replace(" |", "#{bold}#{white} |#{reset}#{red}")
    if l.startswith("#{bold}#{black}"):
        l = l.replace(" |", "#{bold}#{white} |#{bold}#{black}")

    return l

def write_out(what):
    wrt(wp(what))

@before.each_step
def print_step_running(step):
    if not step.defined_at:
        return

    color = '#{bold}#{black}'

    if step.scenario.outlines:
        color = '#{reset}#{cyan}'

    string = step.represent_string(step.original_sentence)
    string = wrap_file_and_line(string, '#{bold}#{black}', '#{reset}')
    write_out("%s%s" % (color, string))
    if step.hashes:
        for line in step.represent_hashes().splitlines():
            write_out("#{bold}#{black}%s#{reset}\n" % line)

@after.each_step
def print_step_ran(step):
    buf = []

    if step.scenario.outlines:
        return

    if step.hashes:
        buf.append(wp("#{up}" * (len(step.hashes) + 1)))

    string = step.represent_string(step.original_sentence)

    if not step.failed:
        string = wrap_file_and_line(string, '#{bold}#{black}', '#{reset}')


    prefix = '#{up}'

    if step.failed:
        color = "#{reset}#{red}"
        string = wrap_file_and_line(string, '#{bold}#{red}#{on:yellow}', '#{reset}')

    elif step.passed:
        color = "#{bold}#{green}"

    elif step.defined_at:
        color = "#{reset}#{cyan}"

    else:
        color = "#{reset}#{yellow}"
        prefix = ""

    buf.append(wp("%s%s%s" % (prefix, color, string)))

    if step.hashes:
        for line in step.represent_hashes().splitlines():
            buf.append(wp("%s%s#{reset}\n" % (color, line)))

    if step.failed:
        buf.append("#{bold}#{red}")
        pspaced = lambda x: buf.append("%s%s" % (" " * step.indentation, x))
        lines = step.why.traceback.splitlines()

        for pindex, line in enumerate(lines):
            pspaced(line)
            if pindex + 1 < len(lines):
                buf.append("\n")

        buf.append("#{reset}\n")

    wrt("".join(buf))

@before.each_scenario
def print_scenario_running(scenario):
    string = scenario.represented()
    string = wrap_file_and_line(string, '#{bold}#{black}', '#{reset}')
    write_out("#{bold}#{white}%s" % string)

@after.outline
def print_outline(scenario, order, outline, reasons_to_fail):
    table = strings.dicts_to_string(scenario.outlines, scenario.keys)
    lines = table.splitlines()
    head = lines.pop(0)

    wline = lambda x: write_out("#{reset}#{cyan}%s%s#{reset}\n" % (" " * scenario.table_indentation, x))
    wline_success = lambda x: write_out("#{bold}#{green}%s%s#{reset}\n" % (" " * scenario.table_indentation, x))
    wline_red = lambda x: wrt("%s%s" % (" " * scenario.table_indentation, x))
    if order is 0:
        wrt("\n")
        wrt("#{bold}#{white}%s%s:#{reset}\n" % (" " * scenario.indentation, scenario.language.first_of_examples))
        wline(head)

    line = lines[order]
    wline_success(line)
    if reasons_to_fail:
        elines = reasons_to_fail[0].traceback.splitlines()
        wrt("#{bold}#{red}")
        for pindex, line in enumerate(elines):
            wline_red(line)
            if pindex + 1 < len(elines):
                wrt("\n")

        wrt("#{reset}\n")

@before.each_feature
def print_feature_running(feature):
    string = feature.represented()
    lines = string.splitlines()

    write_out("\n")
    for line in lines:
        line = wrap_file_and_line(line, '#{bold}#{black}', '#{reset}')
        write_out("#{bold}#{white}%s\n" % line)

    write_out("\n")

@after.all
def print_end(total):
    write_out("\n")

    word = total.features_ran > 1 and "features" or "feature"

    color = "#{bold}#{green}"
    if total.features_passed is 0:
        color = "#{reset}#{red}"

    write_out("#{bold}#{white}%d %s (%s%d passed#{bold}#{white})#{reset}\n" % (
        total.features_ran,
        word,
        color,
        total.features_passed
        )
    )

    color = "#{bold}#{green}"
    if total.scenarios_passed is 0:
        color = "#{reset}#{red}"

    word = total.scenarios_ran > 1 and "scenarios" or "scenario"
    write_out("#{bold}#{white}%d %s (%s%d passed#{bold}#{white})#{reset}\n" % (
        total.scenarios_ran,
        word,
        color,
        total.scenarios_passed
        )
    )

    steps_details = []
    kinds_and_colors = {
        'failed': '#{reset}#{red}',
        'skipped': '#{reset}#{cyan}',
        'undefined': '#{reset}#{yellow}'
    }


    for kind, color in kinds_and_colors.items():
        attr = 'steps_%s' % kind
        stotal = getattr(total, attr)
        if stotal:
            steps_details.append(
                "%s%d %s" % (color, stotal, kind)
            )

    steps_details.append("#{bold}#{green}%d passed#{bold}#{white}" % total.steps_passed)
    word = total.steps > 1 and "steps" or "step"
    content = "#{bold}#{white}, ".join(steps_details)

    word = total.steps > 1 and "steps" or "step"
    write_out("#{bold}#{white}%d %s (%s)#{reset}\n" % (
        total.steps,
        word,
        content
        )
    )

    if total.proposed_definitions:
        wrt("\n#{reset}#{yellow}You can implement step definitions for undefined steps with these snippets:\n\n")
        wrt("# -*- coding: utf-8 -*-\n")
        wrt("from lettuce import step\n\n")

        last = len(total.proposed_definitions) - 1
        for current, step in enumerate(total.proposed_definitions):
            method_name = step.proposed_method_name
            wrt("@step(u'%s')\n" % step.proposed_sentence)
            wrt("def %s:\n" % method_name)
            wrt("    pass")
            if current is last:
                wrt("#{reset}")

            wrt("\n")

def print_no_features_found(where):
    where = core.fs.relpath(where)
    if not where.startswith(os.sep):
        where = '.%s%s' % (os.sep, where)

    write_out('#{bold}#{red}Oops!#{reset}\n')
    write_out(
        '#{bold}#{white}could not find features at '
        '#{bold}#{yellow}%s#{reset}\n' % where
    )
