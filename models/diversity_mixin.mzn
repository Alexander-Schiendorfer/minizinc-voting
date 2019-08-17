array[int,int] of int: diversity_stayaway;
array[int,int] of int: diversity_staynear;
array[int,int] of int: diversity_nogood;

constraint forall (i in index_set_1of2(diversity_nogood)) (
  exists (j in index_set_2of2(diversity_nogood)) (diversity_x[j] != diversity_nogood[i,j])
);

solve maximize
  if length(diversity_stayaway)=0 then 0 else min (i in index_set_1of2(diversity_stayaway)) (sum (j in index_set_2of2(diversity_stayaway)) (abs(diversity_x[j] - diversity_stayaway[i,j]))) endif
  -
  if length(diversity_staynear)=0 then 0 else sum (j in index_set_2of2(diversity_staynear)) (abs(diversity_x[j] - diversity_staynear[max(index_set_1of2(diversity_staynear)),j])) endif
  ;
