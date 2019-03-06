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
q = {i:1 for i in N}
# S = set(itertools.combinations(N, rn) for rn in range(n))
loc_x = rnd.rand(len(V))*200
loc_y = rnd.rand(len(V))*100
A = [(i,j) for i in V for j in V if i != j]
# a1 = [(i,j) for i in N for j in N if i != j]
# a2 = [(i,j) for i in E for j in N if i != j]
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
for i,j in x.keys():
    x[j,i] = x[i,j] # edge in opposite direction
u=m.addVars(A, ub=2.0, vtype=GRB.INTEGER, name='u')
for i,j in u.keys():
  u[j,i] = u[i,j]
m.update()

#minimize problem 
m.setObjective(quicksum(c[i,j]*x[i,j] for i,j in A ), GRB.MINIMIZE)

#constraints
con1 = m.addConstrs(x.sum(i,'*') == 2 for i in N)
con2 = m.addConstrs((x[i,j] == 1 ) >> (x[i,j] == 0) for i,j in A if i in E and j in E and i!=j )


def subtour(edges):
  visited = [False]*v
  cycles = []
  lengths = []
  selected = [[] for i in range(v)]
  for x,y in edges:
    selected[x].append(y)
  while True:
    current = visited.index(False)
    thiscycle = [current]
    while True:
      visited[current] = True
      neighbors = [x for x in selected[current] if not visited[x]]
      if len(neighbors) == 0:
        break
      current = neighbors[0]
      thiscycle.append(current)
    cycles.append(thiscycle)
    lengths.append(len(thiscycle))
    if sum(lengths) == v:
      break
  # return cycles[lengths.index(min(lengths))]
  return cycles

def subtourelim(model, where):
  if where == GRB.callback.MIPSOL:
    selected = []
    # make a list of edges selected in the solution
    for i in range(v):
      for j in range(v):
        if (i != j):
          sol = model.cbGetSolution(x[i,j])
          #potential idea for x E {0,1,2}
          # if ( model.cbGetSolution(x[i,j]) == 1) and  ( model.cbGetSolution(x[j,i]) == 1):
          #   u[i,j]= 2
          # else:
          #   u[i,j] = sol
          # model.update()
          if sol > 0.5:
            selected += [(i,j)]
    # find the shortest cycle in the selected edge list
    tours = subtour(selected)
    print(tours)
    for t in tours:
      SUnion = []
      I = []
      for node in t:
        if node in N:
          SUnion.append(node)
        else: 
          I.append(node)
      S = SUnion[1:-1]
      if len(S)>0 and len(I)>0:
        print('tour > 0 ')
        #constraint (2)
        model.cbLazy(quicksum(u[i,j] for i,j in itertools.combinations(S, 2)) <= len(S)-1)
        #constraint (3)
        model.cbLazy(u[I[0],SUnion[0]] + 2*quicksum(u[i,j] for i,j in itertools.combinations(SUnion, 2)) + quicksum(u[i,SUnion[len(SUnion)-1]] for i in E if i!=I[0])<= 2*len(S)+3)
        #constraint (4)
        model.cbLazy(quicksum(u[i,SUnion[0]] for i in I) + 3*u[SUnion[0],SUnion[len(SUnion)-1]] + quicksum(u[i,SUnion[len(SUnion)-1]] for i in E if i not in I) <= 4)
        #constraint (5) eliminates  tours with only clients
        # model.cbLazy(quicksum(u[i,j] for i,j in itertools.combinations(SUnion, 2)) <=len(S)+1)

# Optimize
m._vars = m.getVars()
m.params.LazyConstraints = 1
m.optimize(subtourelim)
# m.optimize()
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

