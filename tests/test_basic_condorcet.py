import unittest

from minizinc import Solver, Model

from algorithms.voting_mechanisms.condorcet_runner import CondorcetRunner

AGENTS_KEY = "AGENTS"
AGENTS_PREFERS_KEY = "agent_prefers"

class MyTestCase(unittest.TestCase):

    def setup_method(self, method):
        # hooking up the base model
        self.gecode = Solver.lookup("gecode")
        self.test1 = Model("base_model_pref_profile_2_1.mzn")
        self.test2 = Model("base_model_pref_profile_2_2.mzn")

        # define core variables of interest (we can have multiple occurrences of the same scores,
        # but the projection onto the variables of interest have to change
        # for test purposes, knowing "control" helps me out
        self.variables_of_interest = ["x", "y", "control"]
        self.use_weak_condorcet_domination = True

    def test_first_model(self):
        # This corresponds to problem 2.1 in the voting book
        # 5: A B C
        # 7: B A C
        # 4: A C B
        # 3: C B A
        # The solutions are presented in order A-B-C
        # Duels: B:A 10:9, A:C 16:3, B:C 12:7
        # The winner should be B
        # We only get to see A and then B
        condorcet_runner = CondorcetRunner(self.test1, self.gecode, self.variables_of_interest, AGENTS_KEY, AGENTS_PREFERS_KEY,
                                           self.use_weak_condorcet_domination)
        sol = condorcet_runner.run_basic()
        self.assertEqual(2, sol["control"], "B should be Condorcet winner")
        self.assertEqual(2, len(condorcet_runner.all_solutions), "We should have seen two solutions in the process.")
        actual_control_values = [sol["control"] for sol in condorcet_runner.all_solutions]
        expected_control_values = [1,2]
        self.assertListEqual(actual_control_values,expected_control_values, "Should be that stream of solutions")

    def test_second_model_weak(self):
        # Problem set 2.2 of the voting book; Duels are:
        # A;B 12:12, A:C 16:8, D:A 15:9, C:B 17:7, D:B 17:7, D:C 16:8
        # Condorcet winner D
        # First, with weak domination we'll see B as well
        condorcet_runner = CondorcetRunner(self.test2, self.gecode, self.variables_of_interest, AGENTS_KEY, AGENTS_PREFERS_KEY,
                                           True)
        sol = condorcet_runner.run_basic()

        # We should see: A, B, C, D
        self.assertEqual(4, sol["control"], "D should be Condorcet winner")
        self.assertEqual(4, len(condorcet_runner.all_solutions), "We should have seen four solutions in the process.")
        actual_control_values = [sol["control"] for sol in condorcet_runner.all_solutions]
        expected_control_values = [1,2,3,4]
        self.assertListEqual(actual_control_values,expected_control_values, "Should be that stream of solutions")

    def test_second_model_strict(self):
        # Problem set 2.2 of the voting book; Duels are:
        # A;B 12:12, A:C 16:8, D:A 15:9, C:B 17:7, D:B 17:7, D:C 16:8
        # Condorcet winner D
        # Second, with strict domination we won't get to see B, only [A, D]
        condorcet_runner = CondorcetRunner(self.test2, self.gecode, self.variables_of_interest, AGENTS_KEY,
                                           AGENTS_PREFERS_KEY,
                                           False)
        sol = condorcet_runner.run_basic()

        # We should see: A, B, C, D
        self.assertEqual(4, sol["control"], "D should be Condorcet winner")
        self.assertEqual(2, len(condorcet_runner.all_solutions), "We should have seen two solutions in the process.")
        actual_control_values = [sol["control"] for sol in condorcet_runner.all_solutions]
        expected_control_values = [1, 4]
        self.assertListEqual(actual_control_values, expected_control_values, "Should be that stream of solutions")

if __name__ == '__main__':
    unittest.main()
