# This file is part of MyPaint.
# Copyright (C) 2007-2008 by Martin Renold <martinxyz@gmx.ch>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License.
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY. See the COPYING file for more details.

import layer

class CommandStack:
    def __init__(self):
        self.undo_stack = []
        self.redo_stack = []
        self.call_before_action = []
    
    def do(self, command):
        for f in self.call_before_action: f()
        self.redo_stack = [] # discard
        command.redo()
        self.undo_stack.append(command)
    
    def undo(self):
        if not self.undo_stack: return
        for f in self.call_before_action: f()
        command = self.undo_stack.pop()
        command.undo()
        self.redo_stack.append(command)
        return command
        
    def redo(self):
        if not self.redo_stack: return
        for f in self.call_before_action: f()
        command = self.redo_stack.pop()
        command.redo()
        self.undo_stack.append(command)
        return command

    def get_last_command(self):
        if not self.undo_stack: return None
        return self.undo_stack[-1]
        

class Action:
    # children must support:
    # - redo
    # - undo
    automatic_undo = False

# FIXME: the code below looks horrible, there must be a less redundant way to implement this.
# - eg command_* special members on the document class?
# - and then auto-build wrapper methods?

class Stroke(Action):
    def __init__(self, doc, stroke):
        self.doc = doc
        assert stroke.finished
        self.stroke = stroke # immutable
    def undo(self):
        l = self.doc.layers[self.doc.layer_idx]
        l.strokes.remove(self.stroke)
        l.rerender()
    def redo(self):
        l = self.doc.layers[self.doc.layer_idx]
        l.strokes.append(self.stroke)
        l.rerender()

class ClearLayer(Action):
    def __init__(self, doc):
        self.doc = doc
    def redo(self):
        layer = self.doc.layers[self.doc.layer_idx]
        self.old_strokes = layer.strokes[:] # copy
        self.old_background = layer.background
        layer.strokes = []
        layer.background = None
        layer.rerender()
    def undo(self):
        layer = self.doc.layers[self.doc.layer_idx]
        layer.strokes = self.old_strokes
        layer.background = self.old_background
        layer.rerender()

        del self.old_strokes, self.old_background

class LoadLayer(Action):
    def __init__(self, doc, data):
        self.doc = doc
        self.data = data
    def redo(self):
        layer = self.doc.layers[self.doc.layer_idx]
        self.old_strokes = layer.strokes[:] # copy
        self.old_background = layer.background
        layer.strokes = []
        layer.background = self.data
        layer.rerender()
    def undo(self):
        layer = self.doc.layers[self.doc.layer_idx]
        layer.strokes = self.old_strokes
        layer.background = self.old_background
        layer.rerender()

        del self.old_strokes, self.old_background

class AddLayer(Action):
    def __init__(self, doc, insert_idx):
        self.doc = doc
        self.insert_idx = insert_idx
    def redo(self):
        l = layer.Layer()
        l.surface.observers.append(self.doc.layer_modified_cb)
        self.doc.layers.insert(self.insert_idx, l)
        self.prev_idx = self.doc.layer_idx
        self.doc.layer_idx = self.insert_idx
        for f in self.doc.layer_observers:
            f()
    def undo(self):
        self.doc.layers.pop(self.insert_idx)
        self.doc.layer_idx = self.prev_idx
        for f in self.doc.layer_observers:
            f()

class SelectLayer(Action):
    automatic_undo = True
    def __init__(self, doc, idx):
        self.doc = doc
        self.idx = idx
    def redo(self):
        assert self.idx >= 0 and self.idx < len(self.doc.layers)
        self.prev_idx = self.doc.layer_idx
        self.doc.layer_idx = self.idx
        for f in self.doc.layer_observers:
            f()
    def undo(self):
        self.doc.layer_idx = self.prev_idx
        for f in self.doc.layer_observers:
            f()

# class ModifyStrokes(Action):
#     def __init__(self, layer, strokes, new_brush):
#         self.layer = layer
#         for s in strokes:
#             assert s in layer.strokes
#         self.strokemap = [[s, None] for s in strokes]
#         self.set_new_brush(new_brush)
#     def set_new_brush(self, new_brush):
#         # only called when the action is not (yet/anymore) on the undo stack
#         for pair in self.strokemap:
#             pair[1] = pair[0].copy_using_different_brush(new_brush)
#     def execute(self, undo=False):
#         for old, new in self.strokemap:
#             if undo: old, new = new, old
#             i = self.layer.strokes.index(old)
#             self.layer.strokes[i] = new
#         self.layer.rerender()
#     def undo(self):
#         self.execute(undo=True)
#     redo = execute
