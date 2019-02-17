from gurobipy import *
import numpy as np
import matplotlib.pyplot as plt
import math
import itertools
import random

rnd = np.random
# rnd.seed(0)

n = 10
e = 5
v = n+e
Q = n/e
N = [i for i in range(n)]
E = [i for i in range(n, n+e)]
V = N+E
# q = {i:rnd.randint(1,10) for i in N}

loc_x = rnd.rand(len(V))*200
loc_y = rnd.rand(len(V))*100
A = [(i,j) for i in V  for j in V if i != j]
c = {(i,j):np.hypot(loc_x[i]-loc_x[j],loc_y[i]-loc_y[j]) for i,j in A}
for i in N:
    plt.plot(loc_x[i], loc_y[i], c='b', marker='o')
    plt.annotate('c=%d'%(i),(loc_x[i]+2, loc_y[i]))
for i in E:
    plt.plot(loc_x[i], loc_y[i], c='r', marker='s')
    plt.annotate('e=%d'%(i),(loc_x[i]+2, loc_y[i]))
plt.axis('equal')

#create model
m = Model()

# set variables
x=m.addVars(A, vtype=GRB.BINARY, name='x')
u=m.addVars(N, vtype=GRB.CONTINUOUS, ub=Q, name='u')

m.update()

# #minimize problem 
m.setObjective(quicksum(c[i,j]*x[i,j] for i,j in A), GRB.MINIMIZE)

# #constraints
con1 = m.addConstrs(quicksum(x[i,j] for j in V if j!=i)==1 for i in N)
con2 = m.addConstrs(quicksum(x[i,j] for i in V if i!=j)==1 for j in N)
con3 = m.addConstrs(quicksum(x[i,j] for j in V if j!=i)==1 for i in E)
con4 = m.addConstrs(quicksum(x[i,j] for i in V if i!=j)==1 for j in E)
# con5 = m.addConstrs((x[i,j] == 1) >> (u[i]+1==u[j]) for i,j in A if i!=0 and j!=0)
# con6 = m.addConstrs(u[i]<=Q for i in N)


def subtour(edges):
  visited = [False]*v
  cycles = []
  lengths = []
  while True:
    current = visited.index(False)
    thiscycle = [current]
    while True:
      visited[current] = True
      neighbors = [x for x in edges[current] if not visited[x]]
      if len(neighbors) == 0:
        break
      current = neighbors[0]
      thiscycle.append(current)
    cycles.append(thiscycle)
    lengths.append(len(thiscycle))
    if sum(lengths) == v:
      break
  #  return cycles[lengths.index(min(lengths))]
  return cycles


def subtourelim(model, where):
  if where == GRB.callback.MIPSOL:
    selected = []
    # make a list of edges selected in the solution
    for i in range(v):
      for j in range(v):
        if (i != j):
          sol = model.cbGetSolution(x[i,j])
          if sol > 0.5:
            selected += [(i,j)]
    # find the shortest cycle in the selected edge list
    tours = subtour(selected)
    c = 0
    for t in tours:    
      if ([e for e in t if e in E]) == [] :
        c += 1
    if c > 0:
      expr1 = 0 
      for t in tours: 
        for i in range(len(t)):
          for j in range(i+1, len(t)):
            expr1 += x[t[i], t[j]]
      model.cbLazy(expr1 <= e)

# Optimize
m._vars = m.getVars()
m.params.LazyConstraints = 1
m.optimize(subtourelim)
status = m.status

if status == GRB.Status.UNBOUNDED:
    print('The model cannot be solved because it is unbounded')
    exit(0)
if status == GRB.Status.OPTIMAL:
    print('The optimal objective is %g' % m.objVal)
    sol = m.getAttr('x', x)
    selected = [i for i in sol if sol[i] > 0.5]
    for i in selected:
        plt.plot((loc_x[i[0]],loc_x[i[1]]), (loc_y[i[0]],loc_y[i[1]]), color='r')
    plt.show()
    exit(0)
if status != GRB.Status.INF_OR_UNBD and status != GRB.Status.INFEASIBLE:
    print('Optimization was stopped with status %d' % status)
    exit(0)

print('The model is infeasible; relaxing the constraints')
m.feasRelaxS(0, False, False, True)

if status in (GRB.Status.INF_OR_UNBD, GRB.Status.INFEASIBLE, GRB.Status.UNBOUNDED):
    print('The relaxed model cannot be solved \
           because it is infeasible or unbounded')
    exit(1)

if status != GRB.Status.OPTIMAL:
    print('Optimization was stopped with status %d' % status)
    exit(1)

