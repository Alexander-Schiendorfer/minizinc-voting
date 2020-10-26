import minizinc

from minizinc import Model
import logging
from condorcet_runner import CondorcetRunner

logging.basicConfig(filename="minizinc-python.log", level=logging.DEBUG)

from minizinc import Instance, Model, Result, Solver, Status

# hooking up the base model
gecode = Solver.lookup("gecode")
m = Model("base_model_pref_profile_2_2.mzn")
#m.add_file("wallis_sample2_2.dzn")

# define core variables of interest (we can have multiple occurrences of the same scores,
# but the projection onto the variables of interest have to change
variables_of_interest = ["x", "y"]
use_weak_condorcet_domination = True

condorcet_runner = CondorcetRunner(m, gecode, variables_of_interest, "AGENTS", "agent_prefers", use_weak_condorcet_domination)
#condorcet_runner.run_basic()
condorcet_runner.run_extended()