#! /usr/bin/env python3

### Create a reweighted FES ###

import numpy as np
import pandas as pd
import linecache
import sys
import subprocess
import argparse

### most togled parameters ###
hills_pace=500
cv_stride=500
print_stride=500
#prefix=''
prefix='bck.0.'
bias_column=3
rct_column=4
print_fes_running=True

### parser ###
parser = argparse.ArgumentParser(description='reweight')
parser.add_argument('-c',dest='cv_column',type=int,default=1,required=False,help='cv column to be used from colvar file')
parser.add_argument('-t',dest='transient',type=int,default=0,required=False,help='transient time to be skipped')
args = parser.parse_args()
cv_column=args.cv_column
transient=args.transient

### print some info ###
print(' Some common parameters:')
print('  - reweghting on CV: %d'%cv_column)
print('  - cv_stride = %d'%cv_stride)
print('  - hills_pace = %d'%hills_pace)
if transient:
  print('  - transient = %d'%transient)
if prefix:
  print('  - prefix: '+prefix)

### input stuff ###
Kb=0.0083144621 #kj/mol
temp=350
#- grid -
grid_min=1.5
grid_max=2.7
grid_bin=100
periodic=False
#- files in -
cv_header=1
file_ext='.data'
colvar_file=prefix+'Colvar'
hills_file=prefix+'Hills.data'
#- files out -
FES_file='FES_rew-'+str(cv_column)
FES_head='cv_bin  prat_unif_FES'
fes_running_file='fes_running'
fes_running_head='cv_bin  fes  bias'
if transient>0:
  tran_dir='tran'+str(transient)
  print_fes_running=False

### setup ###
beta=1/(Kb*temp)
hills_needed=True
if (not print_fes_running) and (rct_column>0):
  print(' - WARNING: hills file will not be loaded')
  hills_needed=False
#- fix grid -
cv_grid=np.linspace(grid_min,grid_max,grid_bin)
if periodic:
  periodicity=grid_max-grid_min
#- get walkers -
cmd=subprocess.Popen('ls '+colvar_file+'* |wc -l',shell=True,stdout=subprocess.PIPE)
output=cmd.communicate()
n_walkers=int(output[0])
print('  - n_walkers found: %d'%n_walkers)
if n_walkers==1:
  colvar_files=[colvar_file+file_ext]
else:
  colvar_files=[colvar_file+'.'+str(n)+file_ext for n in range(n_walkers)]
#- get hills data -
stride_step=hills_pace/cv_stride
if not stride_step.is_integer():
  sys.exit(' ERROR: hills_pace not compatible with cv_stride')
if hills_needed:
  hills_header=1
  while linecache.getline(hills_file,hills_header).split()[0]=='#!':
    hills_header+=1
  one_hills_line=linecache.getline(hills_file,hills_header)
  if len(one_hills_line.split()) != 5:
    sys.exit(' ERROR: hills file not compatible')
  b_sigma=float(one_hills_line.split()[2])
  gamma=float(one_hills_line.split()[4])
  inv_gamma=0 #non well-tempered case
  if gamma!=-1:
    inv_gamma=1/gamma
  hills_header-=1
  data=pd.read_table(hills_file,dtype=float,sep='\s+',skiprows=hills_header,header=None,usecols=[1,3])
  b_center=np.array(data.ix[:,1])
  b_height=np.array(data.ix[:,3])
#- get cv data -
if cv_header<0:
  cv_header=1
  while linecache.getline(colvar_files[0],cv_header).split()[0]=='#!':
    cv_header+=1
  cv_header-=1
columns=[0,cv_column,bias_column,rct_column]
if rct_column<0:
  columns=[0,cv_column,bias_column]
data=pd.read_table(colvar_files[0],dtype=float,sep='\s+',skiprows=cv_header,header=None,usecols=columns)
time=np.array(data.ix[:,0])
cv_=np.array(data.ix[:,cv_column])
V_=np.array(data.ix[:,bias_column])
if rct_column>0:
  rc_=np.array(data.ix[:,rct_column])
del columns[0]
for n in range(1,n_walkers):
  data=pd.read_table(colvar_files[n],dtype=float,sep='\s+',skiprows=cv_header,header=None,usecols=columns)
  cv_=np.column_stack((cv_,data.ix[:,cv_column]))
  V_=np.column_stack((V_,data.ix[:,bias_column]))
  if rct_column>0:
    rc_=np.column_stack((rc_,data.ix[:,rct_column]))
del data
print(' --> all data loaded <-- ')

# - prepare output files -
create_dir='bck.meup.sh {0}; mkdir -p {0}'
current_FES=FES_file+'/'+FES_file+'.t-%d'+file_ext
if transient>0:
  FES_file=tran_dir+'/'+FES_file
  current_FES=tran_dir+'/'+current_FES
cmd=subprocess.Popen(create_dir.format(FES_file),shell=True)
cmd.wait()
if print_fes_running:
  current_fes_running=fes_running_file+'/'+fes_running_file+'.t-%d'+file_ext
  cmd=subprocess.Popen(create_dir.format(fes_running_file),shell=True)
  cmd.wait()

#- initialize some variables -
big_number=700
conteniment=0
prat_unif_hist=np.zeros(grid_bin)
bias=np.zeros(grid_bin)
rc_t=0
iter_t=0

#- useful funcions -
def print_fes(my_t):
  it=int(time[my_t])
  prat_unif_fes=-1/beta*np.log(prat_unif_hist)
  prat_unif_fes-=min(prat_unif_fes)
  np.savetxt(current_FES%it,np.c_[cv_grid,prat_unif_fes],header=FES_head,fmt='%14.9f')
  if print_fes_running:
    fes=-1/(1-inv_gamma)*bias
    fes-=min(fes)
    np.savetxt(current_fes_running%it,np.c_[cv_grid,fes,bias-max(bias)],header=fes_running_head,fmt='%14.9f')
def get_delta_bias(i):
  delta_bias=np.zeros(grid_bin)
  if hills_needed:
    for n in range(n_walkers):
      delta_bias+=(1-inv_gamma)*b_height[n_walkers*i+n]*np.exp(-0.5*((cv_grid-b_center[n_walkers*i+n])/b_sigma)**2)
      if periodic:
        delta_bias+=(1-inv_gamma)*b_height[n_walkers*i+n]*np.exp(-0.5*((cv_grid-periodicity-b_center[n_walkers*i+n])/b_sigma)**2)
        delta_bias+=(1-inv_gamma)*b_height[n_walkers*i+n]*np.exp(-0.5*((cv_grid+periodicity-b_center[n_walkers*i+n])/b_sigma)**2)
  return delta_bias

# - set transient -
skip=0
for t in range(len(time)):
  if time[t]>=transient:
    break
  skip+=1
  if t%stride_step==0 and t!=0:
    bias+=get_delta_bias(iter_t)
    iter_t+=1

# - run the thing -
for t in range(skip,len(time)):
  if t%stride_step==0 and t!=0:
    if (iter_t+1)%print_stride==0:
      print_fes(t)
    bias+=get_delta_bias(iter_t)
    if rct_column<0:
      while True:
        ZvZ0_t=np.trapz(np.exp(beta*inv_gamma/(1-inv_gamma)*bias))/np.trapz(np.exp(beta/(1-inv_gamma)*bias-conteniment))
        if ZvZ0_t>np.exp(-big_number):
          break
        conteniment+=big_number
        print('-- Updating numerical conteniment: %d'%(conteniment/big_number),end='\r')
      rc_t=-1/beta*np.log(ZvZ0_t)+conteniment/beta
    else:
      rc_t=rc_[t]
    iter_t+=1
  prat_hist_t,e=np.histogram(cv_[t],bins=grid_bin,range=(grid_min,grid_max),weights=np.exp(beta*(V_[t]-rc_t)),density=False)
  prat_unif_hist+=prat_hist_t

# - print last fes -
end_t=len(time)-1
end_time=int(time[end_t])
print_fes(end_t)

# - get final FES -
backup='bck.meup.sh '+FES_file+file_ext
copy='cp '+current_FES%end_time+' '+FES_file+file_ext
if print_fes_running:
  backup+=' '+fes_running_file+file_ext
  copy+=';cp '+current_fes_running%end_time+' '+fes_running_file+file_ext
cmd=subprocess.Popen(backup+';'+copy,shell=True)
cmd.wait()

