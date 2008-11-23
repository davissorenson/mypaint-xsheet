#!/usr/bin/env python
# brushlib - The MyPaint Brush Library
# Copyright (C) 2007-2008 Martin Renold <martinxyz@gmx.ch>
#
# This library is free software; you can redistribute it and/or
# modify it under the terms of the GNU Lesser General Public
# License as published by the Free Software Foundation; either
# version 2 of the License, or (at your option) any later version.
#
# This library is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY. See the COPYING file for more details.

"Code generator, part of the build process."
import os, sys
import brushsettings

def writefile(filename, s):
    "write generated code if changed"
    s = '// DO NOT EDIT - autogenerated by ' + sys.argv[0] + '\n\n' + s
    if os.path.exists(filename) and open(filename).read() == s:
        print 'Checked', filename
    else:
        print 'Writing', filename
        open(filename, 'w').write(s)


content = ''
for i in brushsettings.inputs:
    content += '#define INPUT_%s %d\n' % (i.name.upper(), i.index)
content += '#define INPUT_COUNT %d\n' % len(brushsettings.inputs)
content += '\n'
for s in brushsettings.settings:
    content += '#define BRUSH_%s %d\n' % (s.cname.upper(), s.index)
content += '#define BRUSH_SETTINGS_COUNT %d\n' % len(brushsettings.settings)
content += '\n'
for s in brushsettings.states:
    content += '#define STATE_%s %d\n' % (s.cname.upper(), s.index)
content += '#define STATE_COUNT %d\n' % len(brushsettings.states)

writefile('brushsettings.hpp', content)
