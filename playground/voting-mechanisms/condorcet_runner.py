
from minizinc import Instance, Model, Result, Solver, Status

class CondorcetRunner:
    def __init__(self, model,solver, variables_of_interest, agents_key, agent_prefers_key , use_weak_condorcet_domination = False):
        self.model = model
        self.variables_of_interest = variables_of_interest
        self.solver = solver
        self.agents_key = agents_key
        self.agent_prefers_key = agent_prefers_key
        self.use_weak_condorcet_domination = use_weak_condorcet_domination

    def run(self):
        inst = Instance(self.solver, self.model)
        # we'll need a solution pool of previously seen solutions
        # to rule out condorcet cycles
        solution_pool = []
        condorcet_comparator = ">=" if self.use_weak_condorcet_domination else ">"

        res: Result = inst.solve()
        print(res.solution)
        while res.status == Status.SATISFIED:
            with inst.branch() as child:
                child.add_string(f"array[{self.agents_key}] of par int: old_score;")
                child["old_score"] = res["score"]  # copy the current ranks

                #child.add_string(f"constraint sum(a in AGENTS) ( bool2int(score[a] > old_score[a] ) ) {condorcet_comparator} win_thresh;")
                child.add_string(
                    f"constraint sum(a in {self.agents_key}) ( bool2int({self.agent_prefers_key}(a, score[a], old_score[a]) ) ) {condorcet_comparator} max({self.agents_key}) div 2;")

                # what I essentially want to say here
                # the number of agents that prefer the next solution
                # is higher (or equal) than the number of agents that like the current one
                # a predicate agent_prefers(a, score_var, old_score_var)

                # but it should be a "new" solution
                solution_dict = {var: res[var] for var in self.variables_of_interest}
                solution_pool += [solution_dict]

                for solution in solution_pool:
                    # e.g. '(x != 1 \\/ y != 2)'
                    something_changes = "(" + " \/ ".join(
                        [f"{v} != {solution[v]}" for v in self.variables_of_interest]) + ")"
                    child.add_string(f"constraint {something_changes};")

                # logging
                with child.files() as files:
                    print(files)
                    # copy files to a dedicated debug folder

                res = child.solve()
                if res.solution is not None:
                    print(res.solution)