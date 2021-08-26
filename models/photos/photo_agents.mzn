%-----------------------------------------------------------------------------
% Placing people on a photo (modified to be tailored to individual prefs)
%
% Alexander Schiendorfer
% 2021-08-26
%
% Ported from the MiniZinc benchmark example
%
%-----------------------------------------------------------------------------
include "globals.mzn";

%-----------------------------------------------------------------------------
% Specification

int: n_agents;
set of int: AGENTS = 1..n_agents;

% preferences (friends) 
array[AGENTS] of set of AGENTS: friends;

%-----------------------------------------------------------------------------
% Model
% position[i] specifies the place of agent i, i.e., position[1] = 3 means
% that agent #1 is placed on the 3rd spot
array[AGENTS] of var AGENTS: position_of_agent;
array[AGENTS] of var AGENTS: agent_of_position;

%-----------------------------------------------------------------------------
% Constraints
constraint  alldifferent(position_of_agent);

constraint inverse(agent_of_position, position_of_agent);


% Break some symmetry
constraint
  position_of_agent[1] < position_of_agent[2];

%-----------------------------------------------------------------------------
% Utilities
% For each agent, how many friends are adjacent to it?

array[AGENTS] of var 0..2: util_per_agent;
constraint forall(a in AGENTS)(util_per_agent[a] = bool2int(agent_of_position[ position_of_agent[a] - 1] in friends[a] ) + 
                                                   bool2int(agent_of_position[ position_of_agent[a] + 1] in friends[a]));
var 0..2*n_agents: social_welfare;
constraint social_welfare = sum(util_per_agent);                                              
                                                   
solve maximize social_welfare;