#! /usr/bin/env python3

import numpy as np

Kb=0.0083144621 #kj/mol
temp=300
beta=1/(Kb*temp)

Fa=30.3252
Fb=22.3214

for i in range(10):
  tempo,alpha=np.loadtxt('16_walkers/'+str(i)+'_ves-p/Alpha.0.data',usecols=(0,1),unpack=True)
#  tempo,alpha=np.loadtxt('one_walker/'+str(i)+'_ves/Alpha.data',usecols=(0,1),unpack=True)
  delta=-1./beta*np.log( np.exp(-beta*alpha)*(1+np.exp(-beta*(Fa-alpha)))/(1+np.exp(-beta*(Fb+alpha))) )
  delta_delta=-1./beta*np.log( (1+np.exp(-beta*(Fa-alpha)))/(1+np.exp(-beta*(Fb+alpha))) )
  order=-1/beta*( np.exp(-beta*(Fa-alpha))-np.exp(-beta*(Fb+alpha)) )
  np.savetxt('test_delta.'+str(i)+'.data',np.c_[tempo,alpha,delta,delta_delta,order])

