import minizinc

from minizinc import Model
print("Hi there, excited to run MZN")
# Create a MiniZinc model

from minizinc import Instance, Model, Result, Solver, Status

gecode = Solver.lookup("gecode")
m = Model("base_model_with_prefs.mzn")
inst = Instance(gecode, m)

res: Result = inst.solve()
print(res.solution)
while res.status == Status.SATISFIED:
    with inst.branch() as child:
        child.add_string("array[AGENTS] of 1..n_options+1: old_rank;")
        child["old_rank"] = res["rank"]  # copy the current ranks
        child.add_string("constraint sum(a in AGENTS) ( bool2int(rank[a] < old_rank[a] ) ) > win_thresh;")

        res = child.solve()
        if res.solution is not None:
            print(res.solution)