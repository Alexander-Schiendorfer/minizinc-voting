
from minizinc import Instance, Model, Result, Solver, Status
gecode = Solver.lookup("gecode")
m = Model("mwe_pydata.mzn")

m["test_param"] = 3

# this did not work
#m["test_vals"] = [1, 4, 4]
#m["test_len"] = 3;
# this did not work either
m.add_file("mwe_pydata.dzn")

inst = Instance(gecode, m)
result = inst.solve()
print(result["x"])
