
include "path.mzn";

% A first attempt at a transportation network

set of int: STOPS = 1..4; % nodes a,b,c,d

set of int: LINES = 1..2; % the lines we can decide 
array[LINES,STOPS] of var bool: participates_in_line;
array[STOPS] of var bool: participates; % in any line

constraint forall(s in STOPS) ( 
  participates[s] = (exists(l in LINES) (participates_in_line[l,s]) ) ); 
  
array[LINES] of var STOPS: start;
array[LINES] of var STOPS: end;

% these are our possible edges (connections that can be activated, in principle)
array[int] of int: froms = [1,2,1,3,2,4];
array[int] of int: tos =   [2,1,3,1,4,1];
set of int: EDGES = index_set(froms);

array[LINES,EDGES] of var bool: edge_in_line;

constraint forall(l in LINES) (sum([edge_in_line[l, e] | e in EDGES]) = 2);
%include "dag.mzn";

% Each line has to pick start and end as well as a path between them 
% constraint path(froms, tos, 1, 4, participates, edge_participates);
constraint forall(l in LINES) (
  dpath(froms, tos, start[l], end[l], 
       %[participates_in_line[l,s] | s in STOPS], 
       participates_in_line[l,..],
       edge_in_line[l,..])
);

% Each stop has to be part of any line
constraint forall(s in STOPS) (participates[s]);