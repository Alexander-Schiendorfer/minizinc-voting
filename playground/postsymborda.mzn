int: m = 5;
set of int: ALTERNATIVES = 1..m; 

int: n = 3;
set of int: AGENTS = 1..n; 

set of int: SCORE = 1..10; 

array[AGENTS] of var SCORE: scores; 

include "table.mzn"; 

function var SCORE: scorefunc(array[int,int] of SCORE: tabular, var int: alt) :: promise_total = 
let {
  var SCORE: sc; 
  array[int] of var int: val = [alt, sc];
  constraint table(val,tabular);
} 
in
sc;

var ALTERNATIVES: selection;

array[int,int] of SCORE: scores_a1 = [| 1, 4 | 2, 7 | 3, 6 | 4, 5 | 5, 1 |];
array[int,int] of SCORE: scores_a2 = [| 1, 8 | 2, 3 | 3, 4 | 4, 2 | 5, 6 |];
array[int,int] of SCORE: scores_a3 = [| 1, 5 | 2, 2 | 3, 6 | 4, 3 | 5, 4 |];


constraint scores[1] = scorefunc(scores_a1, selection);
constraint scores[2] = scorefunc(scores_a2, selection);
constraint scores[3] = scorefunc(scores_a3, selection);

% these are our already explored solutions 
array[int] of SCORE: solution_pool = [ 4, 5, 2 ];

% against how many solutions in the pool does my next solution win? 
set of int: POOL = index_set(solution_pool); 
var 0 .. card(POOL)*n: new_sol_borda_sym; 

% for symmetric borda, I do not only count how many solutions
% I already dominate, but I sum up the number of agents
% that really prefer my new sol. (net(x > y) )
constraint new_sol_borda_sym = sum(p in POOL) (
   % does the next solution win against solution p?
   % i.e. do more agents prefer new_sol to p ? 
   %bool2int(
     % does agent 1 like new_sol more than p ? 
     bool2int( scores[1] > scorefunc(scores_a1, solution_pool[p]) ) +
     % does agent 2 like new_sol more than p ? 
     bool2int( scores[2] > scorefunc(scores_a2, solution_pool[p]) ) +
     % does agent 3 like new_sol more than p ?  
     bool2int( scores[3] > scorefunc(scores_a3, solution_pool[p]) ) 
     % is that a majority? i.e., more than n/2 agents 
%     >= 2
%   )
);


%constraint new_sol_wins >= 2;
solve 
:: int_search([selection], input_order, indomain_min, complete)
satisfy; 