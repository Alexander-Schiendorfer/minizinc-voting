% Use this editor as a MiniZinc scratch book
% this will be my graph example

set of int: NODES = 1..4; % nodes a,b,c,d

array[NODES] of var bool: participates;

array[int] of int: froms = [1,2,1,3,2,4];
array[int] of int: tos =   [2,1,3,1,4,1];

set of int: EDGES = index_set(froms);
array[EDGES] of var bool: edge_participates;

constraint sum(participates) = 4;
constraint sum(edge_participates) > 2;
include "dag.mzn";

constraint dag(froms, tos, participates, edge_participates);

include "reachable.mzn";
constraint reachable(froms, tos, participates, edge_participates);
% forces a cycle
% constraint edge_participates[1] = true /\ edge_participates[5] = true /\ edge_participates[6] = true ; 