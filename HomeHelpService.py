from gurobipy import *
import numpy as np
import matplotlib.pyplot as plt
import math
import itertools
import random
import googlemaps
import GoogleAPIKey as key
import time

rnd = np.random
print("Seed was:", rnd.get_state()[1][0])

def makeRandomAssignments():
  #initialise random data 
  e = random.randint(1, 7)
  n = random.randint(e, e+5)
  # n = 11
  # e = 6
  v = n+e
  Q = round(n/e)
  N = [i for i in range(n)]
  E = [i for i in range(n, n+e)]
  V = N+E
  print(E)
  print(N)
  loc_x = []
  loc_y = []
  loc_x = rnd.rand(len(V))*200
  loc_y = rnd.rand(len(V))*200
  locations = {}
  for i in range(v):
    locations[i] = (loc_x[i], loc_y[i])
  print(locations)
  # locations = {0: (37.49029961381596, 44.264469318304236), 1: (146.3611770687018, 164.05030582035002), 2: (45.346287627882, 26.19454558118528), 3: (100.11100577471078, 71.81303584360535), 4: (160.2143250292677, 111.40947416135228), 5: (53.12452695690513, 122.89466265526194), 6: (22.97804307052902, 178.98674041221426), 7: (93.03075725951064, 193.8948550491515), 8: (195.5675274884949, 124.38690164596534), 9: (180.4959488335691, 76.15846780243596), 10: (176.89452231125577, 45.6794106900207), 11: (127.39238863466808, 176.1005156156058), 12: (88.49106481885356, 89.63373956486502), 13: (160.02079739445284, 140.11704233136098), 14: (135.45988008498318, 134.18067142137855), 15: (153.4569973718195, 158.44897936199612), 16: (19.67735826250663, 126.61583269940371), 17: (175.96063390889083, 123.2695594020563)}
  A = [(i,j) for i in V  for j in V if i != j]
  c = {(i,j):np.hypot(locations[i][0]-locations[j][0],locations[i][1]-locations[j][1]) for i,j in A}
  
  # plot marks on a graph
  for i in N:
      plt.plot(loc_x[i], loc_y[i], c='b', marker='o')
      plt.annotate('c=%d'%(i),(loc_x[i]+2, loc_y[i]))
  for i in E:
      plt.plot(loc_x[i], loc_y[i], c='r', marker='s')
      plt.annotate('e=%d'%(i),(loc_x[i]+2, loc_y[i]))
  plt.axis('equal')
  # plt.show()
  #create model
  m = Model()

  # set variables
  x=m.addVars(A, vtype=GRB.BINARY, name='x')
  u=m.addVars(V, ub=Q, vtype=GRB.INTEGER, name='u')

  m.update()

  #minimize problem 
  m.setObjective(quicksum(c[i,j]*x[i,j] for i,j in A), GRB.MINIMIZE)

  #constraints
  con1_1 = m.addConstrs(quicksum(x[i,j] for j in V if j!=i)==1 for i in N)
  con1_2 = m.addConstrs(quicksum(x[i,j] for i in V if i!=j)==1 for j in V)
  con2_1 = m.addConstrs(quicksum(x[i,j] for j in V if j!=i)==1 for i in E)
  con2_2 = m.addConstrs(quicksum(x[i,j] for i in V if i!=j)==1 for j in E)
  con3 = m.addConstrs((x[i,j] == 1) >> (x[i,j] == 0) for i,j in A if i in E and j in E and i!=j)
  con9 = m.addConstrs((x[i,j] == 1) >> (u[i]-u[j]+(Q*x[i,j])==Q-1) for i,j in A if i not in E and j not in E and i!=j)

  def subtour(edges):
    visited = [False]*v
    cycles = []
    lengths = []
    selected = [[] for i in range(v)]
    for x,y in edges:
      selected[x].append(y)
    while True:
      current = visited.index(False)
      for i in range(v):
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
      if sum(lengths) == v:
        break
    return cycles

  def subtourelim(model, where):
    if where == GRB.callback.MIPSOL:
      selected = []
      # make a list of edges selected in the solution
      for i in V:
        for j in V:
          if (i != j):
            sol = model.cbGetSolution(x[i,j])
            if sol > 0.5:
              selected += [(i,j)]
      tours = subtour(selected)
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
          model.cbLazy(x[I[0],SUnion[0]] + quicksum(x[i,SUnion[0]] for i in E if i!=I[0])<=1)
        elif len(S)>0 and len(I)>=2:
          print('more than 1 employee, more than 2 clients')
          model.cbLazy(x[I[0],SUnion[0]] + quicksum(x[i,j] for i in E for j in SUnion if i!=I[0])<=1)
        elif len(SUnion) == 2 and len(I)>=2:
          print('only 2 clients and 2 employees')
          model.cbLazy(x[I[0],SUnion[0]] + 3*x[SUnion[0],SUnion[1]] + quicksum(x[i,SUnion[1]] for i in E if i!=I[0])<= 4)    
        # elif len(SUnion)>0 and len(I)>=2:
        #   print('more than 1 employee, more than 2 clients')
        #   model.cbLazy(x[I[0],SUnion[0]] + quicksum(x[i,j] for i in E for j in SUnion if i!=I[0])<=1)
  
  # Optimize
  m._vars = m.getVars()
  m.params.LazyConstraints = 1
  m.params.Cuts = 0
  m.params.TimeLimit = 120
  m.optimize(subtourelim)
  status = m.status

  if status == GRB.Status.UNBOUNDED:
      print('The model cannot be solved because it is unbounded')
      return([],e, n)
      exit(0)
  elif status == GRB.Status.OPTIMAL:
      print('The optimal objective is %g' % m.objVal)
      sol = m.getAttr('x', x)
      selected = [i for i in sol if sol[i] > 0.5]
      finalTour = subtour(selected)
      print('---------FINAL TOUR-----------')
      print(finalTour)
      error=False
      for t in finalTour:
        c = 0 
        for node in t:
          if node in E:
            c +=1
        if c!=1:
          error=True
      if not error:
        # for i in selected:
        #   plt.plot((loc_x[i[0]],loc_x[i[1]]), (loc_y[i[0]],loc_y[i[1]]), color='r')
        # plt.show()
        return(finalTour,e, n)
        exit(0)
  elif status != GRB.Status.INF_OR_UNBD and status != GRB.Status.INFEASIBLE:
      print('Optimization was stopped with status %d' % status)
      return([],e, n)
      exit(0)
  
  #relax infeasible model once
  print('The model is infeasible; relaxing the constraints once')
  m.feasRelaxS(0, False, False, True)
  #relaxed model keeps deggree constraints
  m.optimize(subtourelim)
  status = m.status
  if status == GRB.Status.OPTIMAL:
    print('The optimal objective is %g' % m.objVal)
    sol = m.getAttr('x', x)
    selected = [i for i in sol if sol[i] > 0.5]
    finalTour = subtour(selected)
    print('---------FINAL TOUR-----------')
    print(finalTour)
    error = False
    for t in finalTour:
      c = 0 
      for node in t:
        if node in E:
          c +=1
      if c!=1:
        error=True
    if not error:
      # for i in selected:
      #   plt.plot((loc_x[i[0]],loc_x[i[1]]), (loc_y[i[0]],loc_y[i[1]]), color='r')
      # plt.show()
      return(finalTour,e, n)
      exit(0)

  #relax infeasible model until valid solution generated
  counter = 0
  
  while counter<=30:
    print('The model is infeasible; relaxing the constraints until Feasible')
    con1_1 = m.addConstrs(quicksum(x[i,j] for j in V if j!=i)==1 for i in N)
    con1_2 = m.addConstrs(quicksum(x[i,j] for i in V if i!=j)==1 for j in V)
    con9 = m.addConstrs((x[i,j] == 1) >> (u[i]-u[j]+(Q*x[i,j])==Q-1) for i,j in A if i not in E and j not in E and i!=j)
    con2_1 = m.addConstrs(quicksum(x[i,j] for j in V if j!=i)==1 for i in E)
    con2_2 = m.addConstrs(quicksum(x[i,j] for i in V if i!=j)==1 for j in E)
    m.feasRelaxS(0, False, False, True)
    #relaxed model keeps deggree constraints
    con1_1 = m.addConstrs(quicksum(x[i,j] for j in V if j!=i)==1 for i in N)
    con1_2 = m.addConstrs(quicksum(x[i,j] for i in V if i!=j)==1 for j in N)
    con2_1 = m.addConstrs(quicksum(x[i,j] for j in V if j!=i)==1 for i in E)
    con2_2 = m.addConstrs(quicksum(x[i,j] for i in V if i!=j)==1 for j in E)
    con9 = m.addConstrs((x[i,j] == 1) >> (u[i]-u[j]+(Q*x[i,j])==Q-1) for i,j in A if i not in E and j not in E and i!=j)
    m.params.Lazy = 1
    m.optimize(subtourelim)
    status = m.status
    if status == GRB.Status.OPTIMAL:
      print('The optimal objective is %g' % m.objVal)
      sol = m.getAttr('x', x)
      selected = [i for i in sol if sol[i] > 0.5]
      finalTour = subtour(selected)
      print('---------FINAL TOUR-----------')
      print(finalTour)
      error = False
      for t in finalTour:
        c = 0 
        for node in t:
          if node in E:
            c +=1
        if c!=1:
          error=True
      print(c, error)
      if not error:
        # for i in selected:
        #   plt.plot((loc_x[i[0]],loc_x[i[1]]), (loc_y[i[0]],loc_y[i[1]]), color='r')
        # plt.show()
        return(finalTour,e, n)
        exit(0)
    counter +=1
    
  if status in (GRB.Status.INF_OR_UNBD, GRB.Status.INFEASIBLE, GRB.Status.UNBOUNDED):
      print('The relaxed model cannot be solved \
            because it is infeasible or unbounded')
      return([],e, n)
      exit(1)
  elif status != GRB.Status.OPTIMAL:
      print('Optimization was stopped with status %d' % status)
      return([],e, n)
      exit(1) 
  else:
    return([],e, n) 
    exit(0) 
  
  # return([],e, n)  

def makeAPIAssignments(N, E, locations):
  # add API key
  gmaps = googlemaps.Client(key=key.API_key)

  # initialise varibales from arguments
  n = len(N)
  e = len(E)
  v = n+e
  Q = n/e
  V = N+E
  A = [(i,j) for i in V for j in V if i != j]
  print(locations)
  c = {(i,j): gmaps.distance_matrix(locations[i], locations[j], mode='walking')["rows"][0]["elements"][0]["distance"]["value"] for i,j in A}
  
  #plot markers on graph
  for i in N:
    plt.plot(locations[i][0], locations[i][1], c='b', marker='o')
    plt.annotate('c=%d'%(i),(locations[i][0], locations[i][1]))
  for i in E:
    plt.plot(locations[i][0], locations[i][1], c='r', marker='s')
    plt.annotate('e=%d'%(i),(locations[i][0], locations[i][1]))
  plt.axis('equal')

  #create model
  m = Model()

  # set variables
  x=m.addVars(A, vtype=GRB.BINARY, name='x')
  u=m.addVars(V, ub=Q, vtype=GRB.INTEGER, name='u')

  m.update()

  #minimize problem 
  m.setObjective(quicksum(c[i,j]*x[i,j] for i,j in A), GRB.MINIMIZE)

  # #constraints
  con1_1 = m.addConstrs(quicksum(x[i,j] for j in V if j!=i)==1 for i in N)
  con1_2 = m.addConstrs(quicksum(x[i,j] for i in V if i!=j)==1 for j in V)
  con2_1 = m.addConstrs(quicksum(x[i,j] for j in V if j!=i)==1 for i in E)
  con2_2 = m.addConstrs(quicksum(x[i,j] for i in V if i!=j)==1 for j in E)
  con3 = m.addConstrs((x[i,j] == 1) >> (x[i,j] == 0) for i,j in A if i in E and j in E and i!=j)
  con4 = m.addConstrs((x[i,j] == 1) >> (u[i]-u[j]+(Q*x[i,j])==Q-1) for i,j in A if i not in E and j not in E and i!=j)

  def subtour(edges):
    visited = [False]*v
    cycles = []
    lengths = []
    selected = [[] for i in range(v)]
    for x,y in edges:
      selected[x].append(y)
    while True:
      current = visited.index(False)
      for i in range(v):
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
      if sum(lengths) == v:
        break
    return cycles

  def subtourelim(model, where):
    if where == GRB.callback.MIPSOL:
      selected = []
      # make a list of edges selected in the solution
      for i in V:
        for j in V:
          if (i != j):
            sol = model.cbGetSolution(x[i,j])
            if sol > 0.5:
              selected += [(i,j)]
      tours = subtour(selected)
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
          model.cbLazy(x[I[0],SUnion[0]] + quicksum(x[i,SUnion[0]] for i in E if i!=I[0])<=1)
        elif len(S)>0 and len(I)>=2:
          print('more than 1 employee, more than 2 clients')
          model.cbLazy(x[I[0],SUnion[0]] + quicksum(x[i,j] for i in E for j in SUnion if i!=I[0])<=1)
        elif len(SUnion) == 2 and len(I)>=2:
          print('only 2 clients and 2 employees')
          model.cbLazy(x[I[0],SUnion[0]] + 3*x[SUnion[0],SUnion[1]] + quicksum(x[i,SUnion[1]] for i in E if i!=I[0])<= 4)    
        # elif len(SUnion)>0 and len(I)>=2:
        #   print('more than 1 employee, more than 2 clients')
        #   model.cbLazy(x[I[0],SUnion[0]] + quicksum(x[i,j] for i in E for j in SUnion if i!=I[0])<=1)
  
  # Optimize
  m._vars = m.getVars()
  m.params.LazyConstraints = 1
  m.params.Cuts = 0
  m.optimize(subtourelim)
  status = m.status

  if status == GRB.Status.UNBOUNDED:
      print('The model cannot be solved because it is unbounded')
      exit(0)
  elif status == GRB.Status.OPTIMAL:
      print('The optimal objective is %g' % m.objVal)
      sol = m.getAttr('x', x)
      selected = [i for i in sol if sol[i] > 0.5]
      finalTour = subtour(selected)
      print('---------FINAL TOUR-----------')
      print(finalTour)
      error=False
      for t in finalTour:
        c = 0 
        for node in t:
          if node in E:
            c +=1
        if c!=1:
          error=True
      if not error:
        # for i in selected:
        #   plt.plot((locations[i[0]][0],locations[i[1]][0]), (locations[i[0]][1],locations[i[1]][1]), color='r')
        # plt.show()
        return finalTour
        exit(0)
  elif status != GRB.Status.INF_OR_UNBD and status != GRB.Status.INFEASIBLE:
      print('Optimization was stopped with status %d' % status)
      exit(0)

#relax infeasible model until valid solution generated
  counter = 0
  while counter<=30:
    print('The model is infeasible; relaxing the constraints until Feasible')
    m.feasRelaxS(0, False, False, True)
    #relaxed model keeps deggree constraints
    con1_1 = m.addConstrs(quicksum(x[i,j] for j in V if j!=i)==1 for i in N)
    con1_2 = m.addConstrs(quicksum(x[i,j] for i in V if i!=j)==1 for j in V)
    con2_1 = m.addConstrs(quicksum(x[i,j] for j in V if j!=i)==1 for i in E)
    con2_2 = m.addConstrs(quicksum(x[i,j] for i in V if i!=j)==1 for j in E)
    m.optimize(subtourelim)
    status = m.status
    if status == GRB.Status.OPTIMAL:
      print('The optimal objective is %g' % m.objVal)
      sol = m.getAttr('x', x)
      selected = [i for i in sol if sol[i] > 0.5]
      finalTour = subtour(selected)
      print('---------FINAL TOUR-----------')
      print(finalTour)
      error = False
      for t in finalTour:
        c = 0 
        for node in t:
          if node in E:
            c +=1
        if c!=1:
          error=True
      if not error:
        # for i in selected:
        #   plt.plot((loc_x[i[0]],loc_x[i[1]]), (loc_y[i[0]],loc_y[i[1]]), color='r')
        # plt.show()
        return(finalTour,e, n)
        exit(0)
    counter +=1
    
  if status in (GRB.Status.INF_OR_UNBD, GRB.Status.INFEASIBLE, GRB.Status.UNBOUNDED):
      print('The relaxed model cannot be solved \
            because it is infeasible or unbounded')
      return([],e, n)
      exit(1)
  if status != GRB.Status.OPTIMAL:
      print('Optimization was stopped with status %d' % status)
      return([],e, n)
      exit(1) 


def makeNoAPIAssignments(N, E, locations):
  n = len(N)
  e = len(E)
  v = n+e
  Q = n/e
  V = N+E
  A = [(i,j) for i in V for j in V if i != j]
  c = {(i,j):np.hypot(locations[i][0]-locations[j][0],locations[i][1]-locations[j][1]) for i,j in A}

  for i in N:
    plt.plot(locations[i][0], locations[i][1], c='b', marker='o')
    plt.annotate('c=%d'%(i),(locations[i][0], locations[i][1]))
  for i in E:
    plt.plot(locations[i][0], locations[i][1], c='r', marker='s')
    plt.annotate('e=%d'%(i),(locations[i][0], locations[i][1]))
  plt.axis('equal')
  
  #create model
  m = Model()

  # set variables
  x=m.addVars(A, vtype=GRB.BINARY, name='x')
  u=m.addVars(V, ub=Q, vtype=GRB.INTEGER, name='u')

  m.update()

  #minimize problem 
  m.setObjective(quicksum(c[i,j]*x[i,j] for i,j in A), GRB.MINIMIZE)

  # #constraints
  con1_1 = m.addConstrs(quicksum(x[i,j] for j in V if j!=i)==1 for i in N)
  con1_2 = m.addConstrs(quicksum(x[i,j] for i in V if i!=j)==1 for j in V)
  con2_1 = m.addConstrs(quicksum(x[i,j] for j in V if j!=i)==1 for i in E)
  con2_2 = m.addConstrs(quicksum(x[i,j] for i in V if i!=j)==1 for j in E)
  con3 = m.addConstrs((x[i,j] == 1) >> (x[i,j] == 0) for i,j in A if i in E and j in E and i!=j)
  con4 = m.addConstrs((x[i,j] == 1) >> (u[i]-u[j]+(Q*x[i,j])==Q-1) for i,j in A if i not in E and j not in E and i!=j)

  def subtour(edges):
    visited = [False]*v
    cycles = []
    lengths = []
    selected = [[] for i in range(v)]
    for x,y in edges:
      selected[x].append(y)
    while True:
      current = visited.index(False)
      for i in range(v):
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
      if sum(lengths) == v:
        break
    return cycles

  def subtourelim(model, where):
    if where == GRB.callback.MIPSOL:
      selected = []
      # make a list of edges selected in the solution
      for i in V:
        for j in V:
          if (i != j):
            sol = model.cbGetSolution(x[i,j])
            if sol > 0.5:
              selected += [(i,j)]
      tours = subtour(selected)
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
          model.cbLazy(x[I[0],SUnion[0]] + quicksum(x[i,SUnion[0]] for i in E if i!=I[0])<=1)
        elif len(S)>0 and len(I)>=2:
          print('more than 1 employee, more than 2 clients')
          model.cbLazy(x[I[0],SUnion[0]] + quicksum(x[i,j] for i in E for j in SUnion if i!=I[0])<=1)
        elif len(SUnion) == 2 and len(I)>=2:
          print('only 2 clients and 2 employees')
          model.cbLazy(x[I[0],SUnion[0]] + 3*x[SUnion[0],SUnion[1]] + quicksum(x[i,SUnion[1]] for i in E if i!=I[0])<= 4)    
        # elif len(SUnion)>0 and len(I)>=2:
        #   print('more than 1 employee, more than 2 clients')
        #   model.cbLazy(x[I[0],SUnion[0]] + quicksum(x[i,j] for i in E for j in SUnion if i!=I[0])<=1)
  
  # Optimize
  m._vars = m.getVars()
  m.params.LazyConstraints = 1
  m.params.Cuts = 0
  m.optimize(subtourelim)
  status = m.status

  if status == GRB.Status.UNBOUNDED:
      print('The model cannot be solved because it is unbounded')
      exit(0)
  elif status == GRB.Status.OPTIMAL:
      print('The optimal objective is %g' % m.objVal)
      sol = m.getAttr('x', x)
      selected = [i for i in sol if sol[i] > 0.5]
      finalTour = subtour(selected)
      print('---------FINAL TOUR-----------')
      print(finalTour)
      error=False
      for t in finalTour:
        c = 0 
        for node in t:
          if node in E:
            c +=1
        if c!=1:
          error=True
      if not error:
        # for i in selected:
        #   plt.plot((loc_x[i[0]],loc_x[i[1]]), (loc_y[i[0]],loc_y[i[1]]), color='r')
        # plt.show()
        return(finalTour,e, n)
        exit(0)
  elif status != GRB.Status.INF_OR_UNBD and status != GRB.Status.INFEASIBLE:
      print('Optimization was stopped with status %d' % status)
      exit(0)
  
  #relax infeasible model until valid solution generated
  counter = 0
  while counter<=30:
    print('The model is infeasible; relaxing the constraints until Feasible')
    m.feasRelaxS(0, False, False, True)
    #relaxed model keeps deggree constraints
    con1_1 = m.addConstrs(quicksum(x[i,j] for j in V if j!=i)==1 for i in N)
    con1_2 = m.addConstrs(quicksum(x[i,j] for i in V if i!=j)==1 for j in V)
    con2_1 = m.addConstrs(quicksum(x[i,j] for j in V if j!=i)==1 for i in E)
    con2_2 = m.addConstrs(quicksum(x[i,j] for i in V if i!=j)==1 for j in E)
    m.optimize(subtourelim)
    status = m.status
    if status == GRB.Status.OPTIMAL:
      print('The optimal objective is %g' % m.objVal)
      sol = m.getAttr('x', x)
      selected = [i for i in sol if sol[i] > 0.5]
      finalTour = subtour(selected)
      print('---------FINAL TOUR-----------')
      print(finalTour)
      error = False
      for t in finalTour:
        c = 0 
        for node in t:
          if node in E:
            c +=1
        if c!=1:
          error=True
      if not error:
        # for i in selected:
        #   plt.plot((loc_x[i[0]],loc_x[i[1]]), (loc_y[i[0]],loc_y[i[1]]), color='r')
        # plt.show()
        return(finalTour,e, n)
        exit(0)
    counter +=1
    
  if status in (GRB.Status.INF_OR_UNBD, GRB.Status.INFEASIBLE, GRB.Status.UNBOUNDED):
      print('The relaxed model cannot be solved \
            because it is infeasible or unbounded')
      return([],e, n)
      exit(1)
  if status != GRB.Status.OPTIMAL:
      print('Optimization was stopped with status %d' % status)
      return([],e, n)
      exit(1)

makeRandomAssignments()