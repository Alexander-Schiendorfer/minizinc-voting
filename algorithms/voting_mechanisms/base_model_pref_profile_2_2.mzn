% This time I test how we can easily enter
% a preference profile from a text book 
% to compare the results against it 

% --------------------------------------------
% Actual decision variables
% now I want just 4 solutions that I can steer with an auxiliary variable
var 1..3: x;
var 1..3: y; 

% --------------------------------------------
% Controllable toy example environment
% the choices are artificially constrained to 4 solutions, assignments to x and y are meaningless
int: n_options = 4;

set of int: CHOICES = 1..n_options;
enum Solutions = { A,B,C,D };
%var 1..n_options: control;
var Solutions: control;

int: n_agents = sum(templateCardinalities);
set of int: AGENTS = 1..n_agents;

array[int,CHOICES] of CHOICES: prefTemplates;

array[int] of int: templateCardinalities ; 

array[int] of int: upr  = 
[ sum([templateCardinalities[j] | j in 1..i]) | i in index_set(templateCardinalities)];

array[int] of int: lwr = 
[if i == 1 then 1 else upr[i-1] + 1 endif | i in index_set(templateCardinalities)];


array[int] of int: agent_to_index  = 
  [ max([ i |  i in index_set(templateCardinalities) where a >= lwr[i] ] ) | a in AGENTS];
 

array[AGENTS,CHOICES] of CHOICES: prefs;
prefs = array2d(AGENTS, CHOICES, [ 
prefTemplates[agent_to_index[a],c]
| a in AGENTS, c in CHOICES]);


% for every agent, give me the rank that control achieves
array[AGENTS] of var 1..n_options: rank;


% this will get overwritten by meta-search
%array[AGENTS] of 1..n_options+1: old_rank;% = [n_options+1 | a in AGENTS];

constraint forall(a in AGENTS) (
  prefs[a,rank[a]] = control
);

constraint if control = A then x = 1 /\ y = 3 endif;
constraint if control = B then x = 2 /\ y = 2 endif;
constraint if control = C then x = 1 /\ y = 2 endif;
constraint if control = D then x = 3 /\ y = 1 endif;

% for the toy example, these are borda scores
constraint forall(a in AGENTS) (score[a] = n_options-rank[a]);

% --------------------------------------------
% Generic hooks for the Condorcet meta-search

% let's convert this to Borda scores to make it a bit more general 
% (we would not be able to give actual ranks to a real combinatorial search space)
% but I would abstract from the fact that these are *Borda* scores, they
% are just utilities that induce the preference ordering over solutions
array[AGENTS] of var 0..n_options-1: score;

predicate agent_prefers(AGENTS: agent, var int: next_score, var int: old_score) = (
  next_score > old_score
);

solve 
% deterministic choice of solutions
:: int_search([control], input_order, indomain_min, complete)
satisfy;


% output [ "\(prefs[a,c]) " ++ if c == n_options then "\n" else "" endif | a in AGENTS, c in CHOICES];
% this would be our model constraint for simple condorcet
% force more agents to prefer the next solution, compared to its old rank
%constraint sum(a in AGENTS) ( bool2int(rank[a] < old_rank[a] ) ) >= win_thresh;
% constraint sum(a in AGENTS) ( bool2int(score[a] > old_score[a] ) ) >= win_thresh;

% sample profile from Wallis "The mathematics of elections and voting"
prefTemplates = 
[| A, C, D, B | 
   B, D, A, C |
   A, D, C, B |
   C, D, B, A |
   D, C, A, B |
   D, C, B, A  
|];

templateCardinalities = [ 
5,
7,
4,
3,
3,
2
];
