% Use this editor as a MiniZinc scratch book

set of int: Site;
Site: hotel;
array[Site,Site] of int: distance;

array[Site] of int: durationOfVisit;
array[Site] of int: siteOpens;
array[Site] of int: siteCloses;

array[Site] of var Site: next ::add_to_output;

include "subcircuit.mzn";
constraint subcircuit(next);

array[Site] of var 0..infinity: arrivalTime::add_to_output;
array[Site] of var 0..infinity: startOfVisit::add_to_output;

constraint arrivalTime[next[hotel]] = distance[hotel,next[hotel]];
constraint forall (i in Site where i != hotel /\ i != next[i]) (
  arrivalTime[next[i]] = startOfVisit[i]+durationOfVisit[i]+distance[i,next[i]]
);

constraint forall (i in Site where i != next[i]) (
   startOfVisit[i] = max(arrivalTime[i], siteOpens[i])
/\ startOfVisit[i]+durationOfVisit[i] <= siteCloses[i]
);

constraint forall (i in Site where i = next[i]) (
  startOfVisit[i]=0 /\ arrivalTime[i]=0
);

var int: travel_time ::add_to_output = sum (i in Site where i != next[i]) (distance[i,next[i]]);

set of int: Passenger;
array[Passenger,Site] of int: site_score;
array[Passenger] of int: preferred_n_sites;
array[Passenger] of int: preferred_travel_time;
array[Passenger,1..3] of int: preference_weights;

array[Passenger,1..3] of var int: passenger_scores ::add_to_output = array2d(Passenger,1..3,
[ if i=1 then sum (i in Site where i != hotel /\ i != next[i]) (site_score[p,i])
  elseif i=2 then (preferred_n_sites[p]-abs(preferred_n_sites[p] - sum (i in Site where i != hotel) (i != next[i])))
  else min(preferred_travel_time[p]-travel_time,0)
  endif
| p in Passenger, i in 1..3]);

array[Passenger] of var int: score ::add_to_output =
[   preference_weights[p,1] * passenger_scores[p,1]
  + preference_weights[p,2] * passenger_scores[p,2]
  + preference_weights[p,3] * passenger_scores[p,3]
  | p in Passenger ];

include "../diversity_mixin.mzn";
array[int] of var Site: diversity_x ::add_to_output = next;
