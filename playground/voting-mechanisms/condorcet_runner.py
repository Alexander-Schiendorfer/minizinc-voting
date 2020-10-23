
from minizinc import Instance, Model, Result, Solver, Status
PREFERRED_BY_KEY = "preferred_by"
NUM_VOTERS_KEY = "num_voters"
class CondorcetRunner:


    def __init__(self, model,solver, variables_of_interest, agents_key, agent_prefers_key , use_weak_condorcet_domination = False):
        self.model = model
        self.variables_of_interest = variables_of_interest
        self.solver = solver
        self.agents_key = agents_key
        self.agent_prefers_key = agent_prefers_key
        self.use_weak_condorcet_domination = use_weak_condorcet_domination
        self.num_voters = 0 # we learn this from the model

    def run_basic(self):
        inst = Instance(self.solver, self.model)
        # we'll need a solution pool of previously seen solutions
        # to rule out condorcet cycles
        solution_pool = []

        res: Result = inst.solve()
        print(res.solution)
        while res.status == Status.SATISFIED:
            with inst.branch() as child:
                child.add_string(f"array[{self.agents_key}] of par int: old_score;")
                child["old_score"] = res["score"]  # copy the current ranks

                self.add_condorcet_improvement(child)

                # but it should be a "new" solution
                solution_dict = {var: res[var] for var in self.variables_of_interest}
                solution_pool += [solution_dict]
                self.post_something_changes(child, solution_pool)

                # logging
                with child.files() as files:
                    print(files)
                    # copy files to a dedicated debug folder

                res = child.solve()
                if res.solution is not None:
                    print(res.solution)

    def run_extended(self):
        inst = Instance(self.solver, self.model)
        # we'll need a solution pool of previously seen solutions
        # to rule out condorcet cycles
        solution_pool = []

        res: Result = inst.solve()
        print(res.solution)
        duels = []
        new_solution = None

        while res.status == Status.SATISFIED:
            old_solution = new_solution
            new_solution = {var: res[var] for var in self.variables_of_interest}
            solution_pool += [new_solution]

            if hasattr(res.solution, PREFERRED_BY_KEY):
                preferred_by = res[PREFERRED_BY_KEY]
                self.num_voters = res[NUM_VOTERS_KEY]
                print(preferred_by)
                duels += [(new_solution, old_solution, preferred_by)]

            with inst.branch() as child:
                child.add_string(f"array[{self.agents_key}] of par int: old_score;")
                child["old_score"] = res["score"]  # copy the current ranks

                self.add_condorcet_improvement(child)
                self.add_duel_bookkeeping(child)

                # but it should be a "new" solution
                self.post_something_changes(child, solution_pool)

                # logging
                with child.files() as files:
                    print(files)
                    # copy files to a dedicated debug folder

                res = child.solve()
                if res.solution is not None:
                    print(res.solution)

        for (winning_solution, losing_solution, preferrers) in duels:
            print(f"Solution {winning_solution} won against {losing_solution} with {preferrers} : {self.num_voters - preferrers}")

    def add_condorcet_improvement(self, child):
        # what I essentially want to say here
        # the number of agents that prefer the next solution
        # is higher (or equal) than the number of agents that like the current one
        # a predicate agent_prefers(a, score_var, old_score_var)

        condorcet_comparator = ">=" if self.use_weak_condorcet_domination else ">"
        child.add_string(
            f"constraint sum(a in {self.agents_key}) ( bool2int({self.agent_prefers_key}(a, score[a], old_score[a]) ) ) {condorcet_comparator} max({self.agents_key}) div 2;")

    def post_something_changes(self, child, solution_pool):
        for solution in solution_pool:
            # e.g. '(x != 1 \\/ y != 2)'
            something_changes = "(" + " \/ ".join(
                [f"{v} != {solution[v]}" for v in self.variables_of_interest]) + ")"
            child.add_string(f"constraint {something_changes};")

    def add_duel_bookkeeping(self, child):
        dueL_bookkeeping_var_def = f"var 0..max({self.agents_key}):  {PREFERRED_BY_KEY}; var int: {NUM_VOTERS_KEY}; constraint {NUM_VOTERS_KEY}= max({self.agents_key});"
        dueL_bookkeeping_var_cons = f"constraint {PREFERRED_BY_KEY} = sum(a in {self.agents_key}) ( bool2int({self.agent_prefers_key}(a, score[a], old_score[a]) ) );"

        child.add_string(dueL_bookkeeping_var_def)
        child.add_string(dueL_bookkeeping_var_cons)