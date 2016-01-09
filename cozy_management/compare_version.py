#!/usr/bin/env python

import sys
from distutils.version import LooseVersion

def compare(current, operator, reference):
    # if len(sys.argv) < 4:
    #     script_name = sys.argv[0]
    #     print 'Usage:'
    #     print '{} current-version operator reference-version'.format(script_name)
    #     print '{} v0.10.29 \'>=\' v0.10.20'.format(script_name)
    #     print '{} v0.10.29 \'<\' v0.12.00'.format(script_name)
    #     sys.exit(1)

    current = LooseVersion(current.replace('v', ''))
    reference = LooseVersion(reference.replace('v', ''))

    if operator == '>=':
        if not current >= reference:
            sys.exit(1)
    elif operator == '>':
        if not current > reference:
            sys.exit(1)
    elif operator == '<=':
        if not current <= reference:
            sys.exit(1)
    elif operator == '<':
        if not current < reference:
            sys.exit(1)
    else:
        print 'Unknown operator {}'.format(operator)
        sys.exit(1)
