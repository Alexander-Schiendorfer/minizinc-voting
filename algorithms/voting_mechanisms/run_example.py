import minizinc

from minizinc import Model
print("Hi there, excited to run MZN")
# Create a MiniZinc model

basic_voting_model = Model("base_model.mzn")
gecode_solver = minizinc.Solver.lookup("gecode")

instance = minizinc.Instance(gecode_solver, basic_voting_model)
# set some parameters like this
# instance["a"] = 1

# now solve
result = instance.solve(all_solutions=True)
for i in range(len(result)):
    print("x = {}, y = {}".format(result[i, "x"], result[i, "y"]))
    print(result[i])