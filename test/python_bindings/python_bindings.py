#!/usr/bin/env python

# Copyright 2017 Stanford University
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

from __future__ import print_function

import legion
import numpy

init = legion.extern_task(task_id=3, privileges=[legion.RW])

@legion.task
def f(ctx, x, y, z):
    print("inside task f%s" % ((x, y, z),))
    return x+1

@legion.task(privileges=[legion.RW])
def inc(ctx, R, step):
    print("inside task inc%s" % ((R, step),))

    # Sanity check that the values written by init are here, and that
    # they follow the same array ordering.
    print(R.x)
    for x in xrange(0, 4):
        for y in xrange(0, 4):
            assert int(R.x[x][y]) == x*4 + y

    numpy.add(R.x, step, out=R.x)
    print(R.x)

@legion.task(privileges=[legion.RW])
def fill(ctx, S, value):
    print("inside task fill%s" % ((S, value),))

    S.x.fill(value)
    S.y.fill(value)
    print(S.x[0:10])
    print(S.y[0:10])

@legion.task(privileges=[legion.RW])
def saxpy(ctx, S, a):
    print("inside task saxpy%s" % ((S, a),))

    print(S.x[0:10])
    print(S.y[0:10])
    numpy.add(S.y, a*S.x, out=S.y)
    print(S.y[0:10])

@legion.task
def main_task(ctx):
    print("inside main_task()")

    x = f(ctx, 1, "asdf", True)
    print("result of f is %s" % x)

    R = legion.Region.create(ctx, [4, 4], {'x': (legion.double, 1)})
    init(ctx, R)
    inc(ctx, R, 1)

    S = legion.Region.create(ctx, [1000], {'x': legion.double, 'y': legion.double})
    fill(ctx, S, 10)
    saxpy(ctx, S, 2)