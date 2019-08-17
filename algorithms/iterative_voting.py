#!/usr/bin/env python3

import argparse
import minizinc
import random

argparser = argparse.ArgumentParser(description="test")
argparser.add_argument("--model", help="model file", required=True)
argparser.add_argument("--data", help="data file", required=True)
argparser.add_argument("--iterations", help="number of iterations", default=20)
argparser.add_argument("--sol-per-agent", help="number of solutions per agent", default=3)
argparser.add_argument("--voting-method", help="voting method to use", choices=["borda","copeland"], default="copeland")

solver = minizinc.Solver.lookup("gecode")

class Diversifier:

    def __init__(self, model):
        self.mzn_instance = minizinc.Instance(solver,model)
        self.nogoods = []
        self.stayaway = []
        self.staynear = []

    def stay_away(self,s):
        self.stayaway += [sol["diversity_x"] for sol in s]

    def stay_near(self,s):
        self.staynear = [s[1]["diversity_x"]]

    def no_good(self,n):
        self.nogoods += [sol["diversity_x"] for sol in n]

    def next_k(self, k, with_nogoods):
        sols = []
        diversity_pool = self.stayaway[:]
        nogood_pool = self.nogoods[:]+[s["diversity_x"] for s in with_nogoods]
        for i in range(k):
            with self.mzn_instance.branch() as inst:
                inst["diversity_stayaway"] = diversity_pool
                inst["diversity_nogood"] = nogood_pool
                inst["diversity_staynear"] = self.staynear
                next_res = inst.solve()
                if next_res.status.has_solution():
                    diversity_pool.append(next_res["diversity_x"])
                    nogood_pool.append(next_res["diversity_x"])
                    sols.append(next_res)
                else:
                    break
        return sols

class Rank:

    def __init__(self, i):
        self.me = i

    def score(self, x):
        return x[1]["score"][self.me]

    def rank(self, xs):
        xs_i = [ (i,x) for (i,x) in enumerate(xs) ]
        return sorted(xs_i, key=self.score, reverse=True)

class Agent:

    def __init__(self,i,m):
        self._rank = Rank(i)
        self._diversifier = Diversifier(m)

    def rank(self, xs):
        r = self._rank.rank(xs)
        self.stay_near(r[0])
        return r

    def stay_away(self, s):
        self._diversifier.stay_away(s)

    def no_good(self, n):
        self._diversifier.no_good(n)

    def stay_near(self, s):
        self._diversifier.stay_near(s)

    def next_k(self, k, with_nogoods):
        return self._diversifier.next_k(k,with_nogoods)

class Borda:

    def __init__(self):
        pass

    def vote(self, xs):
        votes = [ [0,None] for i in range(len(xs[0])) ]
        for idx, sol in xs[0]:
            votes[idx][1] = sol
        for ranking in xs:
            cur_vote = len(ranking)-1
            for idx, sol in ranking:
                votes[idx][0] += cur_vote
                cur_vote -= 1
        return sorted(votes, key=lambda v:v[0], reverse=True)

class Copeland:

    def __init__(self):
        pass

    def vote(self, xs):
        n_alternatives = len(xs[0])
        positions = []
        solutions = [ None for i in range(n_alternatives) ]
        for sol in xs[0]:
            solutions[sol[0]]=sol[1]
        for x in xs:
            x_pos = [0 for i in range(n_alternatives)]
            for i,j in enumerate(x):
                x_pos[j[0]]=i
            positions.append(x_pos)
        copeland = []
        for i in range(n_alternatives):
            n_wins = 0
            for j in range(n_alternatives):
                if i != j:
                    agent_prefs = 0
                    for a in range(len(positions)):
                        if positions[a][i] < positions[a][j]:
                            agent_prefs += 1
                        else:
                            agent_prefs -= 1
                    if agent_prefs > 0:
                        n_wins += 1
            copeland.append(n_wins)
        votes = [ (w, solutions[i]) for i,w in enumerate(copeland) ]
        return sorted(votes, key=lambda v: v[0], reverse=True)

if __name__ == "__main__":

    args = argparser.parse_args()
    m = minizinc.Model()
    m.add_file(args.model)
    m.add_file(args.data)
    agents = [ Agent(a, m) for a in range(len(m["Passenger"])) ]

    n_steps = args.iterations
    n_agents = len(agents)
    n_sol_per_agent = args.sol_per_agent

    d = Diversifier(m)
    s = d.next_k(n_agents*n_sol_per_agent,[])

    voting = None
    if args.voting_method=="borda":
        voting = Borda()
    elif args.voting_method=="copeland":
        voting = Copeland()
    else:
        pass

    all_sols = []

    winners = []

    for i in range(n_steps):
        rankings = [ agents[i].rank(s) for i in range(n_agents)]
        print("Rankings",[ [ (x[0],x[1]["diversity_x"],x[1]["score"]) for x in r ] for r in rankings])
        voting_result = voting.vote(rankings)
        ranked_sols = [ x[1] for x in voting_result]
        all_sols += ranked_sols
        print("Preliminary voting result", [ (s[0],s[1]["diversity_x"], s[1]["score"]) for s in voting_result])
        stay_away = ranked_sols[-int(len(ranked_sols)/3):]
        winners.append(ranked_sols[0])
        s = []
        if i<n_steps-1:
            cur_len = len(s)
            for a in agents:
                a.stay_away(stay_away)
                a.no_good(ranked_sols)
                s += a.next_k(n_sol_per_agent, with_nogoods=s)
            if len(s)==cur_len:
                # no new solutions found by any agent, finish
                break

    all_rankings = [ agents[i].rank(all_sols) for i in range(n_agents)]
    print("Final rankings", [[(x[0], x[1]["diversity_x"], x[1]["score"]) for x in r] for r in all_rankings])
    print("n solutions",len(all_rankings[0]))
    all_ranked_sols = voting.vote(all_rankings)
    print("Final voting result", [ (s[0],s[1]["diversity_x"], s[1]["score"]) for s in all_ranked_sols])
    for i,w in enumerate(winners):
        if w==all_ranked_sols[0][1]:
            print("Winner found at iteration ",i+1)
            break
