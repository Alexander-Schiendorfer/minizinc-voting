int: m = 5;
set of int: ALTERNATIVES = 1..m; 

int: n = 3;
set of int: AGENTS = 1..n; 

set of int: SCORE = 1..10; 

array[AGENTS] of var SCORE: scores; 

include "table.mzn"; 

function var SCORE: scorefunc(array[int,int] of SCORE: tabular, var int: alt) = 
let {
  var SCORE: sc; 
  array[int] of var int: val = [alt, sc];
  constraint table(val,tabular);
} 
in
sc;

var ALTERNATIVES: selection;

% constraint forall(a in AGENTS) (scores[a] = costs([| 1, 4 | 2, 7 | 3, 6 |], selection));

constraint scores[1] = scorefunc([| 1, 4 | 2, 7 | 3, 6 | 4, 5 | 5, 1 |], selection);
constraint scores[2] = scorefunc([| 1, 8 | 2, 3 | 3, 4 | 4, 2 | 5, 6 |], selection);
constraint scores[3] = scorefunc([| 1, 5 | 2, 2 | 3, 5 | 4, 3 | 5, 4 |], selection);

solve 
:: int_search([selection], input_order, indomain_min, complete)
satisfy; 