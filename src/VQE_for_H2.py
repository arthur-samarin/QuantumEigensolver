"""
@author: Oleksandr Kyriienko
"""

import numpy as np
import scipy as sc
import random
import os

# INSTALL Qutip library for Python3  from http://qutip.org/
# and import it
from qutip import *

#---------!!!---------
ndata = 1  # flag for a data folder
#---------!!!---------

s_div="" # separator for string joining
newpath = s_div.join(("data_",str(ndata)))
if not os.path.exists(newpath): 
   os.makedirs(newpath)  # create data directory 

#----------------------------------------------------------
# Construct the Hilbert space for the computation (matrices and vectors):
# define Pauli matrices -- these are the basic operators which define qubit algebra
# read more at http://qutip.org/docs/latest/guide/guide-basics.html
si = qeye(2); sx = sigmax(); sy = sigmay(); sz = sigmaz()
# define spin operators with fixed Hilbert space
N = 2	# number of qubits in the simulation
sx_list = []; sy_list = []; sz_list = []; si_list = []  # list of operators acting on 0,1,2,... qubit
for n in range(N):
   op_list = []
   for m in range(N):
       op_list.append(si)
   op_list[n] = sx; sx_list.append(tensor(op_list))  # now each operator acts in the extended space of N qubits
   op_list[n] = sy; sy_list.append(tensor(op_list))
   op_list[n] = sz; sz_list.append(tensor(op_list))
   op_list[n] = si; si_list.append(tensor(op_list))

# Construct H2 (molecular hyrdrogen) Hamiltonian [as in Google paper https://arxiv.org/abs/1512.06860]
H = 0.2976*si_list[0]*si_list[1] + 0.3593*sz_list[0] - 0.4826*sz_list[1] + 0.5818*sz_list[0]*sz_list[1] + 0.0896*sx_list[0]*sx_list[1] + 0.0896*sy_list[0]*sy_list[1]
qutip.qsave(H, 'input/H2')

eps_chem = 0.0016 # chemical accuracy, redefined through scaling constant
# find eigenvalues and eigenvectors
evals, evecs = H.eigenstates()
# save the data to separate folder and file
file_data_store(s_div.join(("data_",str(ndata),"/energies.dat")), np.vstack(evals).T, numtype="real", numformat="decimal", sep="\n")

# Define intial state (Hartree-Fock solution)
# basis(2,0) -- up state; # basis(2,1) -- down state
# Q.unit() -- Returns normalized (unit) vector Q/Q.norm().
sxP = (basis(2, 0) + basis(2, 1)).unit(); sxM = (basis(2, 0) - basis(2, 1)).unit()
syP = (basis(2, 0) + 1j * basis(2, 1)).unit(); syM = (basis(2, 0) - 1j * basis(2, 1)).unit()
szP = (basis(2, 0)).unit(); szM = (basis(2, 1)).unit()
psi0 = tensor(basis(2,0),basis(2,1)).unit()

# Find the true ground state energy from exact diagonalization
Egs = np.min(evals)
# Find the energy value for the intial product state: <psi_0|H|psi_0> = expectation value of H
lambda_0 = expect(H,psi0)
lambda_chem = Egs + eps_chem  # energy within chamical precision
print('E_gs = {}, E_HF = {}'.format(Egs,lambda_0))

# Set the zeroth interation for variational parameter
theta0 = 0. * 2*np.pi

# Prepare the unitary circuit as in Google's PRX, Fig. 1
# rx,ry,rz are 2-by-2 qubit rotation operators from QuTip as described in 
# https://nbviewer.jupyter.org/github/qutip/qutip-notebooks/blob/master/examples/quantum-gates.ipynb
def U(theta):
   return tensor(ry(np.pi/2),-rx(np.pi/2))*cnot(N=N, control=0, target=1)*tensor(si,rz(theta))*cnot(N=N, control=0, target=1)*tensor(-ry(np.pi/2),rx(np.pi/2))
print('Evolution operator reads as {}'.format(U(theta0)))

# Define the energy function as expectation value of the Hamiltonian with variated initial state
def E_to_min(theta):
   return expect(H, U(theta) * psi0)

E_start = E_to_min(theta0)
print('Initial energy for random variational parameters is {}'.format(E_start))
file_data_store(s_div.join(("data_",str(ndata),"/E_start.dat")), np.vstack([E_start]).T, numtype="real", numformat="decimal", sep="\n")

# Choose the variational method implemented in scipy: 
# M = 1 for gradient-free Nelder-Mead
# M = 0 for gradient based quasi-Newton method of Broyden, Fletcher, Goldfarb, and Shanno (BFGS)
M = 1

print('Starting the variational procedure...')

if M==1:
  E_list = [] # save energies for each iteration
  res = sc.optimize.minimize(E_to_min, theta0, method='nelder-mead', options={'xtol': 1e-4, 'disp': True})
  Emin = res.fun
  E_list.append(Emin)
  theta_min = res.x
  print('The ground state energy from minimization is {},'.format(Emin))
  print('and energy distance to true ground state is {}.'.format(Emin-Egs))
  print('Minimum is obtained for the variational angles theta = {}.'.format(theta_min))
  file_data_store(s_div.join(("data_",str(ndata),"/E_list.dat")), np.vstack(E_list).T, numtype="real", numformat="decimal", sep="\n")
  file_data_store(s_div.join(("data_",str(ndata),"/E_min.dat")), np.vstack([Emin]).T, numtype="real", numformat="decimal", sep="\n")
  file_data_store(s_div.join(("data_",str(ndata),"/theta_min.dat")), np.vstack(theta_min).T, numtype="real", numformat="decimal", sep="\n")
else:
  # use BFGS algorithm --- the quasi-Newton method of Broyden, Fletcher, Goldfarb, and Shanno (BFGS)
  Nfeval = 1
  E_list = []
  E_iter = []
  def callbackF(Xi):
      global Nfeval
      print('{0:4d}   {1: 3.6f}   {2: 3.6f} '.format(Nfeval, Xi[0], E_to_min(Xi)))
      E_iter.append(E_to_min(Xi))
      Nfeval += 1

  print('{0:4s}   {1:9s}   {2:9s} '.format('Iter', ' theta', 'f(X)') )  
  x0 = theta0
  [xopt, fopt, gopt, Bopt, func_calls, grad_calls, warnflg] = \
      sc.optimize.fmin_bfgs(E_to_min, 
                x0, 
                callback=callbackF, 
                maxiter=2000, 
                full_output=True, 
                retall=False)
  niter = Nfeval
  Emin = fopt
  E_list.append(Emin)
  theta_min = xopt
  file_data_store(s_div.join(("data_",str(ndata),"/E_list.dat")), np.vstack(E_list).T, numtype="real", numformat="decimal", sep="\n")
  file_data_store(s_div.join(("data_",str(ndata),"/E_min.dat")), np.vstack([Emin]).T, numtype="real", numformat="decimal", sep="\n")
  file_data_store(s_div.join(("data_",str(ndata),"/N_iter.dat")), np.vstack([niter]).T, numtype="real", numformat="decimal", sep="\n")
  file_data_store(s_div.join(("data_",str(ndata),"/theta_min.dat")), np.vstack(xopt).T, numtype="real", numformat="decimal", sep="\n")
  print('The ground state energy from minimization is {},'.format(Emin))
  print('and energy distance to true ground state is {}.'.format(np.abs(Emin-Egs)))
  print('Minimum is obtained for the variational angles theta = {},'.format(theta_min))
  print('achieved for {} iterations.'.format(niter))
  import matplotlib.pyplot as plt
  plt.plot(E_iter, 'r-')
  plt.show()

