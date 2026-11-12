#!/usr/bin/env bash
# round.sh with extra environment (e.g. BEAM_TWO=1) — usage: bash round_env.sh "BEAM_TWO=1" <T> <work> <prevT>
env $1 bash round.sh $2 $3 $4
