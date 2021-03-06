#main Hartree-Fock script
#numbers refer to steps listed in Szabo page 161

import numpy as np
import math
from scipy.sparse.linalg import eigs as eig

from scf import SCF
from basis import Basis
from tests.testValues import testSCF
from integrals import Integrals
from ctypes import *

#import PyQuante to handle integrals
from PyQuante import Molecule
from PyQuante import Ints
from PyQuante import fermi_dirac as pyqSCF
from PyQuante import LA2 

scf = SCF() 
basis = Basis()
testValues = testSCF()
integrals = Integrals()

#load C library for integrals
libcint = CDLL("/modfac/home/saswatr/Documents/Myself/repos/libcint/build")

#########################
#init main variables

#1
#system contains information for physical atoms/electrons
#uses notation est. in Szabo page 161, step 1
system = {
        
        #atomic coordinates
        "R":[[0.0,0.0,0.0] ],
        #atomic numbers
        "Z":[1],
        #number of electrons
        "N":2
        
        }

#build basis set for system
#basisSet = basis.buildBasis(system)

molec = Molecule( 
        
        "H",
        [  (1, (0,0,0) ),
            (1,(0,0,1))]

        )

basisSet = Ints.getbasis(molec)

#scf energy limit
E_limit = 1.0 * pow(10.0, -6)

#########################
#main code goes here

#init integrals
#S = integrals.overlap(basisSet)
#T = integrals.KE(basisSet)
#Vext = integrals.nucAttract(basisSet, system["Z"], system["R"])
#G = integrals.elecRepulsion(basisSet)

#pyquante integrals
S = np.asmatrix(Ints.getS(basisSet))
T = np.asmatrix(Ints.getT(basisSet))
Vext = np.asmatrix(Ints.getV(basisSet, molec))
G = Ints.get2ints(basisSet)

print("Integrals integrated \n")
#
print("\n Overlap matrix")
print(S)
print("overlap end")
#
print("\n KE matrix")
print(T)
print("KE end")
#
print("\n Vext matrix")
print(Vext)
print("Vext end")
#
print("\n G matrix")
print(G)
print("G end")
#
#init test operators to check program is working
#S, Vext, T, G = testValues.testerParse()

#hamiltonian is equal to kinetic energy plus external potential
#pg.176 Equ. 3.233
Hcore = T + Vext

print("Hcore built")

#########################
#start of scf loop

#get transformation matrix X
X = scf.getTransform(S)
X = scf.zero(X)

print("get transform matrix")

#print("\n X:")
#print(X)
#print("\n")

#init energy
E = [-float("inf")]

#4
#set guess fock matrix equal to the Hamiltonian
F = Hcore

#scf cycle counter
cycle = 0

print("scf init complete")

#scf loop
while(0 == 0):
	
        #7
	#transform Fock matrix from AO to MO basis
        FMO = X.conjugate().transpose() * F * X
        FMO = scf.zero(FMO)

        print("FMO")
        print(FMO)
        print("\n")
        print("Fock matrix transformed")

        #8
        #get eigen values and vectors of FMO
        #and get eigen value matrix
        eVal, eVec = np.linalg.eigh(FMO)
    
        print(eVec)
        print(eVal)

        #9
        #transform eigen vectors to AO basis
        eVecAO = np.dot(X, eVec)
        
        print("eVec AO")
        print(eVecAO)
        print("\n")
            
        #calculate density matrix
        De = scf.buildDensity(eVecAO, system["N"])
        
        nclosed,nopen = molec.get_closedopen()
        nocc = nclosed
        S, h, Intss = Ints.getints(basisSet, molec)
        eVal, eVecAO = LA2.geigh(Hcore, S)

        D = pyqSCF.mkdens(eVecAO,34,nocc)

        print("Density built")

        print("Density")
        print(D)
        print("\n")
       
        #calculate electronic energy
        E.append(scf.energy(Hcore, F, De))
        
        #increment cycle counter
        cycle += 1

        #check convergence
        if(abs(E[cycle] - E[cycle-1]) <= E_limit):
            print("energy converged")
            #break
        
        print("\nEnergy  "  + str(E[cycle]))

        #if convergence did not occur,
        #rebuild Fock Matrix using Hartree Exchange Energy

        #htEx = integrals.HTExchange(D, G)

        htEx = Ints.get2JmK(G, D)

        F = Hcore + htEx

print(E[cycle])
