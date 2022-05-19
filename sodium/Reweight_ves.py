#! /usr/bin/env python3

### Create a reweighted FES ###

import numpy as np
import pandas as pd
import linecache
import sys
import subprocess
import argparse

### most togled parameters ###
gamma=20
av_stride=500
cv_print=500
alpha_print=50000
print_stride=1000
prefix=''
#prefix='bck.0.'
bias_column=3
rct_column=4
alpha_column=1
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
print('  - cv_print = %d'%cv_print)
print('  - av_stride = %d'%av_stride)
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
#- files in -
cv_header=1
file_ext='.data'
colvar_file=prefix+'Colvar'
alpha_file=prefix+'Alpha'
fesA_file='../fesA.data'
fesB_file='../fesB.data'
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
#- initial fesA and fesB -
cv_grid=np.linspace(grid_min,grid_max,grid_bin)
if print_fes_running:
#  gridA,full_fesA=np.loadtxt(fesA_file,usecols=(0,1),unpack=True)
  data=pd.read_table(fesA_file,dtype=float,sep='\s+',skiprows=5,header=None,usecols=[0,1])
  gridA=np.array(data.ix[:,0])
  full_fesA=np.array(data.ix[:,1])
  fesA=np.interp(cv_grid,gridA,full_fesA)
#  gridB,full_fesB=np.loadtxt(fesB_file,usecols=(0,1),unpack=True)
  data=pd.read_table(fesB_file,dtype=float,sep='\s+',skiprows=5,header=None,usecols=[0,1])
  gridB=np.array(data.ix[:,0])
  full_fesB=np.array(data.ix[:,1])
  fesB=np.interp(cv_grid,gridB,full_fesB)
#- get walkers -
cmd=subprocess.Popen('ls '+colvar_file+'* |wc -l',shell=True,stdout=subprocess.PIPE)
output=cmd.communicate()
n_walkers=int(output[0])
print('  - n_walkers found: %d'%n_walkers)
if n_walkers==1:
  colvar_files=[colvar_file+file_ext]
  alpha_file+=file_ext
else:
  colvar_files=[colvar_file+'.'+str(n)+file_ext for n in range(n_walkers)]
  alpha_file+='.0'+file_ext
#- get time -
stride_step=av_stride/cv_print
if not stride_step.is_integer():
  sys.exit(' ERROR: av_stride not compatible with cv_print')
#time,cv_,V_,rc_=np.loadtxt(colvar_files[0],usecols=(0,cv_column,bias_column,rct_column),unpack=True)
if cv_header<0:
  cv_header=1
  while linecache.getline(colvar_files[0],comments_line).split()[0]=='#!':
    cv_header+=1
  cv_header-=1
data=pd.read_table(colvar_files[0],dtype=float,sep='\s+',skiprows=cv_header,header=None,usecols=[0,cv_column,bias_column,rct_column])
time=np.array(data.ix[:,0])
cv_=np.array(data.ix[:,cv_column])
V_=np.array(data.ix[:,bias_column])
rc_=np.array(data.ix[:,rct_column])
if print_fes_running:
  #alpha=np.loadtxt(alpha_file,usecols=(alpha_column,),unpack=True)
  data=pd.read_table(alpha_file,dtype=float,sep='\s+',skiprows=1,header=None,usecols=[alpha_column])
  alpha=np.array(data.ix[:,alpha_column])
for n in range(1,n_walkers):
#  cv_tmp,V_tmp,rc_tmp=np.loadtxt(colvar_files[n],usecols=(cv_column,bias_column,rct_column),unpack=True)
  data=pd.read_table(colvar_files[n],dtype=float,sep='\s+',skiprows=cv_header,header=None,usecols=[cv_column,bias_column,rct_column])
  cv_=np.column_stack((cv_,data.ix[:,cv_column]))
  V_=np.column_stack((V_,data.ix[:,bias_column]))
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
prat_unif_hist=np.zeros(grid_bin)
iter_t=0

#- print funcion -
def print_fes(my_t):
  it=int(time[my_t])
  prat_unif_fes=-1/beta*np.log(prat_unif_hist)
  prat_unif_fes-=min(prat_unif_fes)
  np.savetxt(current_FES%it,np.c_[cv_grid,prat_unif_fes],header=FES_head,fmt='%14.9f')
  if print_fes_running:
    alpha_running=alpha[int(my_t*cv_print/alpha_print)]
    fes=-1/beta*np.log(np.exp(-beta*fesA)+np.exp(-beta*(fesB+alpha_running)))
    fes-=min(fes)
    bias=-1*(1-1/gamma)*fes
    bias-=min(bias)
    np.savetxt(current_fes_running%it,np.c_[cv_grid,fes,bias-max(bias)],header=fes_running_head,fmt='%14.9f')

# - set transient -
skip=0
if transient>0:
  for t in range(len(time)):
    if time[t]>=transient:
      break
    skip+=1
    if t%stride_step==0:
      iter_t+=1

# - run the thing -
for t in range(skip,len(time)):
  if t%stride_step==0:
    if iter_t%print_stride==0 and t!=0:
      print_fes(t)
    iter_t+=1
  prat_hist_t,e=np.histogram(cv_[t],bins=grid_bin,range=(grid_min,grid_max),weights=np.exp(beta*(V_[t]-rc_[t])),density=False)
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

