for i in N:
  m.addConstr(quicksum(x[i,j] for j in V if i!=j) ==2)
m.update()