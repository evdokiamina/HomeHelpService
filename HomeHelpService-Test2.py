from gurobipy import *
import numpy as np
import matplotlib.pyplot as plt
import math
import itertools
import random
import mysql.connector

rnd = np.random
print("Seed was:", rnd.get_state()[1][0])
class HomeHelpService:
  def __init__(self):
    self.n = 10
    self.e = 5
    self.v = self.n+self.e
    self.Q = self.n/self.e
    self.N = [i for i in range(self.n)]
    self.E = [i for i in range(self.n, self.n+self.e)]
    self.V = self.N+self.E

    loc_x = rnd.rand(len(self.V))*200
    loc_y = rnd.rand(len(self.V))*100
    self.A = [(i,j) for i in self.V  for j in self.V if i != j]
    self.c = {(i,j):np.hypot(loc_x[i]-loc_x[j],loc_y[i]-loc_y[j]) for i,j in self.A}

    for i in self.N:
        plt.plot(loc_x[i], loc_y[i], c='b', marker='o')
        plt.annotate('c=%d'%(i),(loc_x[i]+2, loc_y[i]))
    for i in self.E:
        plt.plot(loc_x[i], loc_y[i], c='r', marker='s')
        plt.annotate('e=%d'%(i),(loc_x[i]+2, loc_y[i]))
    plt.axis('equal')

  def main(self):
    #create model
    m = Model()

    # set variables
    x=m.addVars(self.A, vtype=GRB.CONTINUOUS, ub=2.0, name='x')
    u=m.addVars(self.V, ub=self.Q, vtype=GRB.INTEGER, name='u')

    m.update()

    #minimize problem 
    m.setObjective(quicksum(self.c[i,j]*x[i,j] for i,j in self.A), GRB.MINIMIZE)

    # #constraints
    con1_1 = m.addConstrs(quicksum(x[i,j] for j in self.V if j!=i)==1 for i in self.N)
    con1_2 = m.addConstrs(quicksum(x[i,j] for i in self.V if i!=j)==1 for j in self.V)
    con2_1 = m.addConstrs(quicksum(x[i,j] for j in self.V if j!=i)==1 for i in self.E)
    con2_2 = m.addConstrs(quicksum(x[i,j] for i in self.V if i!=j)==1 for j in self.E)
    con3 = m.addConstrs((x[i,j] == 1) >> (x[i,j] == 0) for i,j in self.A if i in self.E and j in self.E and i!=j)
    con4 = m.addConstrs((x[i,j] == 1) >> (u[i]-u[j]+(self.Q*x[i,j])==self.Q-1) for i,j in self.A if i not in self.E and j not in self.E and i!=j)

    # Optimize
    m._vars = m.getVars()
    m.params.LazyConstraints = 1
    # m.params.Threads = 1
    m.params.Cuts = 3
    m.optimize(self.subtourelim())
    status = m.status

    if status == GRB.Status.UNBOUNDED:
        print('The model cannot be solved because it is unbounded')
        exit(0)
    if status == GRB.Status.OPTIMAL:
        print('The optimal objective is %g' % m.objVal)
        sol = m.getAttr('x', x)
        selected = [i for i in sol if sol[i] > 0.5]
        finalTour = subtour(selected)
        print('---------FINAL TOUR-----------')
        print(finalTour)
        for i in selected:
            plt.plot((loc_x[i[0]],loc_x[i[1]]), (loc_y[i[0]],loc_y[i[1]]), color='r')
        plt.show()
        exit(0)
    if status != GRB.Status.INF_OR_UNBD and status != GRB.Status.INFEASIBLE:
        print('Optimization was stopped with status %d' % status)
        exit(0)

    print('The model is infeasible; relaxing the constraints')
    m.feasRelaxS(0, True, False, True)
    # m.feasRelaxS(2, True, False, True)
    # m.relax()
    m.optimize(subtourelim(self))
    status = m.status

    if status!= GRB.Status.OPTIMAL:
      m.feasRelaxS(0, True, False, True)
      m.optimize(subtourelim)
      status = m.status

    if status == GRB.Status.OPTIMAL:
        print('The optimal objective is %g' % m.objVal)
        sol = m.getAttr('x', x)
        selected = [i for i in sol if sol[i] > 0.5]
        finalTour = subtour(selected)
        print('---------FINAL TOUR-----------')
        print(finalTour)
        print(selected)
        for i in selected:
            plt.plot((loc_x[i[0]],loc_x[i[1]]), (loc_y[i[0]],loc_y[i[1]]), color='r')
        plt.show()
        exit(0)

    if status in (GRB.Status.INF_OR_UNBD, GRB.Status.INFEASIBLE, GRB.Status.UNBOUNDED):
        print('The relaxed model cannot be solved \
              because it is infeasible or unbounded')
        exit(1)

    if status != GRB.Status.OPTIMAL:
        print('Optimization was stopped with status %d' % status)
        exit(1)

  def subtour(self, edges):
    visited = [False]*self.v
    cycles = []
    lengths = []
    selected = [[] for i in range(self.v)]
    for x,y in edges:
      selected[x].append(y)
    while True:
      current = visited.index(False)
      for i in range(self.v):
        if visited[i] == False:
          neighbors = [x for x in selected[i]]
          if len(neighbors) == 1:
            current = i
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
      if sum(lengths) == self.v:
        break
    return cycles

  def subtourelim(self, model, where):
    if where == GRB.callback.MIPSOL:
      selected = []
      # make a list of edges selected in the solution
      for i in range(self.v):
        for j in range(self.v):
          if (i != j):
            sol = model.cbGetSolution(x[i,j])
            if sol > 0.5:
              selected += [(i,j)]
      tours = self.subtour(selected)
      for t in tours:
        SUnion = []
        I = []
        for node in t:
          if node in N:
            SUnion.append(node)
          else: 
            I.append(node)
        S = SUnion[1:-1]
        if len(I) == 0 and len(t)>1:
          print('no empoloyees')
          model.cbLazy(quicksum(x[i,j] for i,j in itertools.combinations(t, 2))<= len(t)-1)
        elif len(I)>=2 and len(SUnion) == 1:
          model.cbLazy(x[I[0],SUnion[0]] + quicksum(x[i,SUnion[0]] for i in self.E if i!=I[0])<=1)
        elif len(S)>0 and len(I)>=2:
          print('more than 1 employee, more than 2 clients')
          model.cbLazy(x[I[0],SUnion[0]] + quicksum(x[i,j] for i in self.E for j in SUnion if i!=I[0])<=1)
        elif len(SUnion) == 2 and len(I)>=2:
          print('only 2 clients and 2 employees')
          model.cbLazy(x[I[0],SUnion[0]] + 3*x[SUnion[0],SUnion[1]] + quicksum(x[i,SUnion[1]] for i in self.E if i!=I[0])<= 4)    

if __name__ == '__main__':
  HomeHelpService = HomeHelpService()
  HomeHelpService.main()
  
