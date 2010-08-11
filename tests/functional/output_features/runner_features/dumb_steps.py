#!/usr/bin/env python
# -*- coding: utf-8 -*-
from lettuce import step, before

@step('Given I do nothing')
def do_nothing(step): pass
@step('Then I see that the test passes')
def see_test_passes(step): pass
