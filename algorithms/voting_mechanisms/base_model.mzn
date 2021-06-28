% now I want just 4 solutions that I can steer with an auxiliary variable
var 1..3: x;
var 1..3: y; 

enum Solutions = {A, B, C, D};
var Solutions: control;

constraint if control = A then x = 1 /\ y = 3 endif;
constraint if control = B then x = 2 /\ y = 2 endif;
constraint if control = C then x = 1 /\ y = 2 endif;
constraint if control = D then x = 3 /\ y = 1 endif;

solve 
:: int_search([control], input_order, indomain_min, complete)
satisfy;