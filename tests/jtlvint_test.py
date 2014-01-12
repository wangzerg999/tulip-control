#!/usr/bin/env python
"""
Tests for the interface with JTLV.
"""

from tulip.spec import GRSpec
from tulip.jtlvint import check_gr1, check_realizable, synthesize


class basic_test:
    def setUp(self):
        self.f_un = GRSpec(env_vars="x", sys_vars="y",
                           env_init="x", env_prog="x",
                           sys_init="y", sys_safety=["y -> X(!y)", "!y -> X(y)"],
                           sys_prog="y && x")
        self.f = GRSpec(env_vars="x", sys_vars="y",
                        env_init="x", env_prog="x",
                        sys_init="y",
                        sys_prog=["y & x", "!y"])

    def tearDown(self):
        self.f_un = None
        self.f = None

    def test_dumpjtlv(self):
        specLTL = self.f_un.to_jtlv()
        assumption = specLTL[0]
        guarantee = specLTL[1]
        assert check_gr1(assumption, guarantee,
                         self.f_un.env_vars.keys(), self.f_un.sys_vars.keys())

    def test_check_realizable(self):
        spec = GRSpec(env_vars="x", sys_vars="y",
                      env_init="x", env_prog="x",
                      sys_init="y", sys_safety=["y -> X(!y)", "!y -> X(y)"],
                      sys_prog="y && x")
        assert not check_realizable(self.f_un)
        self.f_un.sys_safety = []
        assert check_realizable(self.f_un)

    def test_synthesize(self):
        aut = synthesize(self.f)
        # There is more than one possible strategy realizing this
        # specification.  Checking only for one here makes this more like
        # a regression test (fragile).  However, it is more meaningful
        # than simply checking that synthesize() returns something
        # non-None (i.e., realizability, which is tested elsewhere).
        assert aut is not None
        assert len(aut.inputs) == 1 and aut.inputs.has_key("x")
        assert len(aut.outputs) == 1 and aut.outputs.has_key("y")
        assert len(aut.states()) == 6
        assert set(aut.transitions()) == set([(0, 1), (0, 2), (1, 3), (1, 4),
                                              (2, 3), (2, 4), (3, 0), (3, 3),
                                              (4, 0), (4, 3), ("Sinit", 0)])
        label_reference = {(0, 1) : (0,0),  # value is bitvector of x,y
                           (0, 2) : (1,0),
                           (1, 3) : (0,0),
                           (1, 4) : (1,0),
                           (2, 3) : (0,0),
                           (2, 4) : (1,0),
                           (3, 0) : (1,1),
                           (3, 3) : (0,0),
                           (4, 0) : (1,1),
                           (4, 3) : (0,0),
                           ("Sinit", 0) : (1,1)}
        for (from_state, to_state, slabel) in aut.transitions(labeled=True):
            assert label_reference[(from_state, to_state)] == (slabel["x"],
                                                               slabel["y"])
