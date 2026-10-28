// WNBA hierarchical NB2 single-stat skill model.
// Adapted from D:/NBA Projections/models/skill/stan/hierarchical_one_stat.stan
//
// Three-level shrinkage: league -> position (G/F/C) -> player.
// No aging covariate, no team-quality, no gravity. The robustness-fit
// objective is to neutralize the "career-mean projection might hide
// coupling" critique on the WNBA Test 1 replication — a hierarchical
// NB2 posterior is the simplest projection method that adds shrinkage
// across the player population without pulling in team-level or aging
// machinery that the WNBA dataset does not currently support.
//
// Inputs:
//   counts[i]              non-negative integer stat in game-row i
//   minutes[i]             game-row minutes played (offset)
//   weights[i]             observation weight (1.0 default; reserved for
//                          recency weighting in V2)
//   player_idx[i]          1..N_players
//   player_position[p]     1..N_positions  (3 for G/F/C)
//
// Priors (weakly informative; data dominates given dense per-player likelihoods):
//   mu_league      ~ normal(prior_mu_league, prior_mu_league_sd)
//   sigma_position ~ exponential(2)        (mean 0.5)
//   sigma_player   ~ exponential(4)        (mean 0.25)
//   phi             ~ exponential(1)
//
// prior_mu_league set per stat from caller (PTS ~ -0.9 / REB ~ -1.9 / BLK ~ -3.9
// on the per-minute log scale).

data {
  int<lower=0> N;
  int<lower=0> N_players;
  int<lower=0> N_positions;
  array[N] int<lower=1, upper=N_players> player_idx;
  array[N_players] int<lower=1, upper=N_positions> player_position;
  array[N] int<lower=0> counts;
  vector<lower=0>[N] minutes;
  vector<lower=0>[N] weights;
  real prior_mu_league;
  real<lower=0> prior_mu_league_sd;
}

parameters {
  real mu_league;
  vector[N_positions] mu_position;
  vector[N_players] mu_player;
  real<lower=0> sigma_position;
  real<lower=0> sigma_player;
  real<lower=0> phi;
}

model {
  mu_league      ~ normal(prior_mu_league, prior_mu_league_sd);
  sigma_position ~ exponential(2);
  sigma_player   ~ exponential(4);
  phi             ~ exponential(1);

  mu_position    ~ normal(mu_league, sigma_position);
  mu_player      ~ normal(mu_position[player_position], sigma_player);

  vector[N] log_rate = mu_player[player_idx];
  vector[N] log_mu_obs = log_rate + log(minutes);
  for (i in 1:N) {
    target += weights[i] * neg_binomial_2_log_lpmf(counts[i] | log_mu_obs[i], phi);
  }
}

generated quantities {
  vector[N_players] rate_per_36 = exp(mu_player) * 36.0;
  vector[N_positions] rate_per_36_position = exp(mu_position) * 36.0;
  real rate_per_36_league = exp(mu_league) * 36.0;
}
