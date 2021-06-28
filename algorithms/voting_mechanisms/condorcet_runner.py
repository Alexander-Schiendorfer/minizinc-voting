
from minizinc import Instance, Model, Result, Solver, Status
import os
from shutil import copyfile

PREFERRED_BY_KEY = "preferred_by"
NUM_VOTERS_KEY = "num_voters"

class CondorcetRunner:


    def __init__(self, model,solver, variables_of_interest, agents_key, agent_prefers_key , use_weak_condorcet_domination = False):
        self.model = model
        self.variables_of_interest = variables_of_interest
        self.solver = solver
        self.inst = Instance(self.solver, self.model)
        self.agents_key = agents_key
        self.agent_prefers_key = agent_prefers_key
        self.use_weak_condorcet_domination = use_weak_condorcet_domination
        self.num_voters = 0 # we learn this from the model
        self.all_solutions = []
        self.debug = False

    # refers to the basic version of Condorcet's procedure in Wallis "The mathematics of elections and voting"
    def run_basic(self):
        # we'll need a solution pool of previously seen solutions
        # to rule out condorcet cycles; a solution is stored as a Python dictionary from variable to value
        solution_pool = []
        inst = self.inst
        res: Result = inst.solve()
        self.create_debug_folder()

        print("Initial solution of model")
        print(res.solution)
        model_counter = 0 # necessary for debugging
        while res.status == Status.SATISFIED:
            model_counter += 1
            with inst.branch() as child:
                child.add_string(f"array[{self.agents_key}] of par int: old_score;")
                child["old_score"] = res["score"]  # copy the current ranks

                self.add_condorcet_improvement(child)

                # but it should be a "new" solution in terms of the variables that I'm interested in at least
                solution_dict = {var: res[var] for var in self.variables_of_interest}
                solution_pool += [solution_dict]
                self.post_something_changes(child, solution_pool)

                # logging
                self.log_and_debug_generated_files(child, model_counter)

                res = child.solve()
                if res.solution is not None:
                    print(res.solution)

        self.all_solutions = solution_pool
        return solution_pool[-1] if len(solution_pool) > 0 else None

    # refers to the extended version of Condorcet's procedure in Wallis "The mathematics of elections and voting"
    def run_extended(self):
        inst = Instance(self.solver, self.model)

        # we'll need a solution pool of previously seen solutions
        # to rule out condorcet cycles; a solution is stored as a Python dictionary from variable to value
        solution_pool = []

        res: Result = inst.solve()
        print(res.solution)
        duels = []
        new_solution = None
        model_counter = 0

        while res.status == Status.SATISFIED:
            model_counter += 1
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
                self.log_and_debug_generated_files(child, model_counter)

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
        # e.g. 'constraint sum(a in AGENTS) ( bool2int(agent_prefers(a, score[a], old_score[a]) ) ) >= max(AGENTS) div 2;'
        child.add_string(
            f"constraint sum(a in {self.agents_key}) ( bool2int({self.agent_prefers_key}(a, score[a], old_score[a]) ) ) {condorcet_comparator} max({self.agents_key}) div 2;")

    def post_something_changes(self, child, solution_pool):
        # an individual constraint is posted for every solution in the pool
        for solution in solution_pool:
            # e.g. '(x != 1 \\/ y != 2)'
            something_changes = "(" + r" \/ ".join(
                [f"{v} != {solution[v]}" for v in self.variables_of_interest]) + ")"
            child.add_string(f"constraint {something_changes};")

    def add_duel_bookkeeping(self, child):
        dueL_bookkeeping_var_def = f"var 0..max({self.agents_key}):  {PREFERRED_BY_KEY}; var int: {NUM_VOTERS_KEY}; constraint {NUM_VOTERS_KEY}= max({self.agents_key});"
        dueL_bookkeeping_var_cons = f"constraint {PREFERRED_BY_KEY} = sum(a in {self.agents_key}) ( bool2int({self.agent_prefers_key}(a, score[a], old_score[a]) ) );"

        child.add_string(dueL_bookkeeping_var_def)
        child.add_string(dueL_bookkeeping_var_cons)

    def create_debug_folder(self):

        self.debug_dir = ("debug")
        if not os.path.isdir(self.debug_dir):
            os.makedirs(self.debug_dir)

    def log_and_debug_generated_files(self, child, model_counter):
        with child.files() as files:
            print(files)
            if self.debug:
                # copy files to a dedicated debug folder
                for item in files[1:]:
                    filename = os.path.basename(item)
                    base, extension = os.path.splitext(filename)
                    copyfile(item, os.path.join(self.debug_dir, f"mzn_condorcet_{model_counter}.{extension}"))