% now I want just 4 solutions that I can steer with an auxiliary variable
var 1..3: x;
var 1..3: y; 

var 1..4: control;

constraint if control = 1 then x = 1 /\ y = 3 endif;
constraint if control = 2 then x = 2 /\ y = 2 endif;
constraint if control = 3 then x = 1 /\ y = 2 endif;
constraint if control = 4 then x = 3 /\ y = 1 endif;

solve 
:: int_search([control], input_order, indomain_min, complete)
satisfy;