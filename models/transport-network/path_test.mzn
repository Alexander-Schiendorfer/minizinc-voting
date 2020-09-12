% Use this editor as a MiniZinc scratch book
% this will be my graph example

set of int: CITIES = 1..4; % nodes a,b,c,d

array[CITIES] of var bool: participates;

% these are our possible edges (connections that can be activated)

array[int] of int: froms = [1,1,2,3];
array[int] of int: tos =   [2,3,4,4];
set of int: EDGES = index_set(froms);


array[EDGES] of var bool: edge_participates;

include "path.mzn";

constraint path(froms, tos, 1, 4, participates, edge_participates);

