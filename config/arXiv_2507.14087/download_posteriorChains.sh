#!/usr/bin/env bash

curl --output temp.tar.gz "https://zenodo.org/api/records/15880667/files/posterior_chain_full_fit.tar.gz/content"
tar -xf temp.tar.gz
rm temp.tar.gz
mv mcmc_full_Kfactor/chain.pkl Posterior_wK/
mv mcmc_full_vanilla/chain.pkl Posterior_K1/
rm -fr mcmc*
