int: test_param;
int: fixed_param = 1;
int: test_len;

array[1..test_len] of int: test_vals ;

var 1..10: x;

constraint x = 2 * test_param + fixed_param;
