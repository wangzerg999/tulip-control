import os.path
import os
import pickle
import sys
import numpy as np

from tulip import spec, synth, hybrid
from polytope import box2poly
from tulip.abstract import prop2part, discretize

from exportFMU import exportFMU
# @import_section_end@


if os.path.isfile('AbstractPwa.p') and os.path.isfile('FSM.p'):
    pwa = pickle.load(open("AbstractPwa.p", "rb"))
    ctrl = pickle.load(open("FSM.p", "rb"))
else:
    # the code in robot_planning/continuous.py
    # Problem parameters
    input_bound = 1.0
    uncertainty = 0.01

    # Continuous state space
    cont_state_space = box2poly([[0., 3.], [0., 2.]])

    # Continuous dynamics
    A = np.array([[1.0, 0.], [0., 1.0]])
    B = np.array([[0.1, 0.], [0., 0.1]])
    E = np.array([[1., 0.], [0., 1.]])

    # Available control, possible disturbances
    U = input_bound * np.array([[-1., 1.], [-1., 1.]])
    W = uncertainty * np.array([[-1., 1.], [-1., 1.]])

    # Convert to polyhedral representation
    U = box2poly(U)
    W = box2poly(W)

    # Construct the LTI system describing the dynamics
    sys_dyn = hybrid.LtiSysDyn(A, B, E, None, U, W, cont_state_space)
    # @dynamics_section_end@

    # @partition_section@
    # Define atomic propositions for relevant regions of state space
    cont_props = {}
    cont_props['home'] = box2poly([[0., 1.], [0., 1.]])
    cont_props['lot'] = box2poly([[2., 3.], [1., 2.]])

    # Compute proposition preserving partition of the continuous state space
    cont_partition = prop2part(cont_state_space, cont_props)
    # @partition_section_end@

    # @discretize_section@
    pwa = discretize(
        cont_partition, sys_dyn, closed_loop=True,
        N=8, min_cell_volume=0.1, plotit=False
    )
    # @discretize_section_end@

    """Specifications"""
    # Environment variables and assumptions
    env_vars = {'park'}
    env_init = set()                # empty set
    env_prog = '!park'
    env_safe = set()                # empty set

    # System variables and requirements
    sys_vars = {'X0reach'}
    sys_init = {'X0reach'}
    sys_prog = {'home'}               # []<>home
    sys_safe = {'(X(X0reach) <-> lot) || (X0reach && !park)'}
    sys_prog |= {'X0reach'}

    # Create the specification
    specs = spec.GRSpec(env_vars, sys_vars, env_init, sys_init,
                        env_safe, sys_safe, env_prog, sys_prog)

    # @synthesize_section@
    """Synthesize"""
    ctrl = synth.synthesize('gr1c', specs,
                            sys=pwa.ts, ignore_sys_init=True)
    # end of the code in robot_planning/continuous.py

    # store the result for future use
    pickle.dump(ctrl, open('FSM.p', 'wb'))
    pickle.dump(pwa, open('AbstractPwa.p', 'wb'))

x0 = np.array([1.5, 1.5])
d0 = 18

exportFMU(ctrl, pwa, x0, d0)
os.system("make testController")
