int: m = 3;
set of int: ALTERNATIVES = 1..m; 

int: n = 3;
set of int: AGENTS = 1..n; 

set of int: SCORE = 1..10; 

array[AGENTS] of var SCORE: scores; 

include "table.mzn"; 

function var SCORE: costs(array[int,int] of SCORE: tabular, var int: alt) = 
let {
  var SCORE: sc; 
  array[int] of var int: val = [alt, sc];
  constraint table(val,tabular);
} 
in
sc;

var ALTERNATIVES: selection;

constraint forall(a in AGENTS) (scores[a] = costs([| 1, 4 | 2, 7 | 3, 6 |], selection));

solve satisfy; 