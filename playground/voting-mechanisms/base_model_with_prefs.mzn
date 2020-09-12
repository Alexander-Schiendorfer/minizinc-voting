% now I want just 4 solutions that I can steer with an auxiliary variable
var 1..3: x;
var 1..3: y; 

% the choices are artificially constrained to 4 solutions, assignments to x and y are meaningless
int: n_options = 4;
var 1..n_options: control;
set of int: CHOICES = 1..n_options;

int: n_agents = 4;
set of int: AGENTS = 1..n_agents;
int: win_thresh = n_agents div 2;

array[AGENTS,CHOICES] of CHOICES: prefs = 
[| 1, 2, 3, 4 | 4, 1, 3, 2 | 3, 4, 1, 2 | 4, 2, 3, 1 |];

% for every agent, give me the rank that control achieves
array[AGENTS] of var 1..n_options: rank;

% this will get overwritten by meta-search
%array[AGENTS] of 1..n_options+1: old_rank;% = [n_options+1 | a in AGENTS];

constraint forall(a in AGENTS) (
  prefs[a,rank[a]] = control
);

constraint if control = 1 then x = 1 /\ y = 3 endif;
constraint if control = 2 then x = 2 /\ y = 2 endif;
constraint if control = 3 then x = 1 /\ y = 2 endif;
constraint if control = 4 then x = 3 /\ y = 1 endif;

solve 
:: int_search([control], input_order, indomain_min, complete)
satisfy;

% this would be our model constraint for simple condorcet
% force more agents to prefer the next solution, compared to its old rank
%constraint sum(a in AGENTS) ( bool2int(rank[a] < old_rank[a] ) ) >= win_thresh;
