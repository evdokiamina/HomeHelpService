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

class mainAlgorithm:
  def makeRandomAssignments():
    #initialise random employees and patients 
    n = 10
    e = 3
    # e = random.randint(3, 10)
    # n = random.randint(e, 10)
    v = n+e
    Q = round(n/e)
    N = [i for i in range(n)]
    E = [i for i in range(n, n+e)]
    V = N+E
    print(E)
    print(N)
    
    #initialise random locations
    loc_x = []
    loc_y = []
    loc_x = rnd.rand(len(V))*200
    loc_y = rnd.rand(len(V))*200

    #save locations in a dictionary
    locations = {}
    for i in range(v):
      locations[i] = (loc_x[i], loc_y[i])
    print(locations)
    # locations = {0: (106.94620003914198, 181.70143419328926), 1: (0.7729551371220778, 39.333395427292885), 2: (129.55802510335388, 94.28572788924012), 3: (72.02447789983239, 90.9238203694291), 4: (179.94661901329357, 47.21091576033587), 5: (190.77495940071745, 98.83866522927522), 6: (14.575465594370463, 147.96246087779107), 7: (55.55447672037832, 70.77449161939045), 8: (134.56410638681155, 66.74921446020927), 9: (137.14736345079982, 25.141752159543863), 10: (104.31776988588719, 144.07224689522417), 11: (1.4529080867347943, 110.99618220989831), 12: (137.93553807690466, 70.59449839935678), 13: (113.51200281428, 30.34891138208384), 14: (124.85085986970044, 71.02387286648066), 15: (174.5836123626304, 178.8721228541386), 16: (21.44852627113909, 159.05687341805444), 17: (17.61557466390431, 117.36776287534106)}
    
    #initialise Arcs list and cost list
    A = [(i,j) for i in V  for j in V if i != j]
    c = {(i,j):np.hypot(locations[i][0]-locations[j][0],locations[i][1]-locations[j][1]) for i,j in A}
    
    # plot marks on a graph-clear graph if previously plotted
    plt.clf() 
    for i in N:
      plt.plot(locations[i][0], locations[i][1], c='b', marker='o')
      plt.annotate('c=%d'%(i),(locations[i][0], locations[i][1]))
    for i in E:
      plt.plot(locations[i][0], locations[i][1], c='r', marker='s')
      plt.annotate('e=%d'%(i),(locations[i][0], locations[i][1]))
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
          # S = SUnion[1:-1]
          if len(I) == 0 and len(t)>1:
            print('no empoloyees')
            model.cbLazy(quicksum(x[i,j] for i,j in itertools.combinations(t, 2))<= len(t)-1)
          elif len(SUnion)>0 and len(I)>=2:
            print('more than 1 employee, more than 2 clients')
            model.cbLazy(x[I[0],SUnion[0]] + quicksum(x[i,j] for i in E for j in SUnion if i!=I[0])<=1)        # elif len(I)>=2 and len(SUnion) == 1:
          #   model.cbLazy(x[I[0],SUnion[0]] + quicksum(x[i,SUnion[0]] for i in E if i!=I[0])<=1)
          # elif len(S)>0 and len(I)>=2:
          #   print('more than 1 employee, more than 2 clients')
          #   model.cbLazy(x[I[0],SUnion[0]] + quicksum(x[i,j] for i in E for j in SUnion if i!=I[0])<=1)
          # elif len(SUnion) == 2 and len(I)>=2:
          #   print('only 2 clients and 2 employees')
          #   model.cbLazy(x[I[0],SUnion[0]] + 3*x[SUnion[0],SUnion[1]] + quicksum(x[i,SUnion[1]] for i in E if i!=I[0])<= 4)    
    
    # Optimize
    m._vars = m.getVars()
    m.params.LazyConstraints = 1
    m.params.Cuts = 0
    m.optimize(subtourelim)
    status = m.status

    if status == GRB.Status.OPTIMAL:
      print('The optimal objective is %g' % m.objVal)
      sol = m.getAttr('x', x)
      selected = [i for i in sol if sol[i] > 0.5]
      finalTour = subtour(selected)
      print('---------FINAL TOUR-----------')
      print(finalTour)
      print(locations)
      error=False
      for t in finalTour:
        c = 0 
        for node in t:
          if node in E:
            c +=1
        if c!=1:
          error=True
      if not error:
        for i in selected:
          plt.plot(( locations[i[0]][0],locations[i[1]][0]), (locations[i[0]][1],locations[i[1]][1]), color='r')
        # plt.show()
        return(finalTour,e, n, 'First Try')
        exit(0)

    
    #relax infeasible model once the quickest way
    print('The model is infeasible; relaxing the constraints once')
    # relaxed model keeps deggree constraints
    m.feasRelaxS(0,False, False, True)
    m.optimize(subtourelim)
    status = m.status
    if status == GRB.Status.OPTIMAL:
      print('The optimal objective is %g' % m.objVal)
      sol = m.getAttr('x', x)
      selected = [i for i in sol if sol[i] > 0.5]
      finalTour = subtour(selected)
      print('---------FINAL TOUR-----------')
      print(finalTour)
      print(locations)
      error = False
      for t in finalTour:
        c = 0 
        for node in t:
          if node in E:
            c +=1
        if c!=1:
          error=True
      if not error:
        for i in selected:
          plt.plot(( locations[i[0]][0],locations[i[1]][0]), (locations[i[0]][1],locations[i[1]][1]), color='r')
        # plt.show()
        return(finalTour,e, n, 'First Relaxation')
        exit(0)

    #relax infeasible model until valid solution generated
    counter = 0
    while counter>=0:
    # while True:
      print('The model is infeasible; relaxing the constraints until Feasible')
      con1_1 = m.addConstrs(quicksum(x[i,j] for j in V if j!=i)==1 for i in N)
      con1_2 = m.addConstrs(quicksum(x[i,j] for i in V if i!=j)==1 for j in V)
      con2_1 = m.addConstrs(quicksum(x[i,j] for j in V if j!=i)==1 for i in E)
      con2_2 = m.addConstrs(quicksum(x[i,j] for i in V if i!=j)==1 for j in E)
      m.feasRelax(0, True, x, None, None, None, None)
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
        print(locations)
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
          for i in selected:
            plt.plot(( locations[i[0]][0],locations[i[1]][0]), (locations[i[0]][1],locations[i[1]][1]), color='r')
          # plt.show()
          return(finalTour,e, n, counter)
          exit(0)
      counter +=1
      
    if status in (GRB.Status.INF_OR_UNBD, GRB.Status.INFEASIBLE, GRB.Status.UNBOUNDED):
        print('The relaxed model cannot be solved \
              because it is infeasible or unbounded')
        return(locations,e, n,counter)
        exit(1)
    elif status != GRB.Status.OPTIMAL:
        print('Optimization was stopped with status %d' % status)
        return(locations,e, n, counter)
        exit(1) 
    else:
      return(locations,e, n, counter) 
      exit(0) 

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
    plt.clf() 
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
          # S = SUnion[1:-1]
          if len(I) == 0 and len(t)>1:
            print('no empoloyees')
            model.cbLazy(quicksum(x[i,j] for i,j in itertools.combinations(t, 2))<= len(t)-1)
          elif len(SUnion)>0 and len(I)>=2:
            print('more than 1 employee, more than 2 clients')
            model.cbLazy(x[I[0],SUnion[0]] + quicksum(x[i,j] for i in E for j in SUnion if i!=I[0])<=1)
          # elif len(I)>=2 and len(SUnion) == 1:
          #   model.cbLazy(x[I[0],SUnion[0]] + quicksum(x[i,SUnion[0]] for i in E if i!=I[0])<=1)
          # elif len(S)>0 and len(I)>=2:
          #   print('more than 1 employee, more than 2 clients')
          #   model.cbLazy(x[I[0],SUnion[0]] + quicksum(x[i,j] for i in E for j in SUnion if i!=I[0])<=1)
          # elif len(SUnion) == 2 and len(I)>=2:
          #   print('only 2 clients and 2 employees')
          #   model.cbLazy(x[I[0],SUnion[0]] + 3*x[SUnion[0],SUnion[1]] + quicksum(x[i,SUnion[1]] for i in E if i!=I[0])<= 4)    
          
    # Optimize
    m._vars = m.getVars()
    m.params.LazyConstraints = 1
    m.params.Cuts = 0
    m.optimize(subtourelim)
    status = m.status

    if status == GRB.Status.OPTIMAL:
      print('The optimal objective is %g' % m.objVal)
      sol = m.getAttr('x', x)
      selected = [i for i in sol if sol[i] > 0.5]
      finalTour = subtour(selected)
      # print('---------FINAL TOUR-----------')
      # print(finalTour)
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
    
    #relax infeasible model once the quickest way
    print('The model is infeasible; relaxing the constraints once')
    # relaxed model keeps deggree constraints
    m.feasRelaxS(0,False, False, True)
    m.optimize(subtourelim)
    status = m.status
    if status == GRB.Status.OPTIMAL:
      print('The optimal objective is %g' % m.objVal)
      sol = m.getAttr('x', x)
      selected = [i for i in sol if sol[i] > 0.5]
      finalTour = subtour(selected)
      print('---------FINAL TOUR-----------')
      print(finalTour)
      print(locations)
      error = False
      for t in finalTour:
        c = 0 
        for node in t:
          if node in E:
            c +=1
        if c!=1:
          error=True
      if not error:
        for i in selected:
          plt.plot(( locations[i[0]][0],locations[i[1]][0]), (locations[i[0]][1],locations[i[1]][1]), color='r')
        # plt.show()
        return(finalTour,e, n, 'First Relaxation')
        exit(0)


  #relax infeasible model until valid solution generated
    counter = 0
    while counter>=0:
    # while True:
      print('The model is infeasible; relaxing the constraints until Feasible')
      con1_1 = m.addConstrs(quicksum(x[i,j] for j in V if j!=i)==1 for i in N)
      con1_2 = m.addConstrs(quicksum(x[i,j] for i in V if i!=j)==1 for j in V)
      con2_1 = m.addConstrs(quicksum(x[i,j] for j in V if j!=i)==1 for i in E)
      con2_2 = m.addConstrs(quicksum(x[i,j] for i in V if i!=j)==1 for j in E)
      m.feasRelax(0, True, x, None, None, None, None)
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
        # print('---------FINAL TOUR-----------')
        # print(finalTour)
        # print(locations)
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
          #   plt.plot(( locations[i[0]][0],locations[i[1]][0]), (locations[i[0]][1],locations[i[1]][1]), color='r')
          # plt.show()
          return(finalTour,e, n, counter)
          exit(0)
      counter +=1
      
    if status in (GRB.Status.INF_OR_UNBD, GRB.Status.INFEASIBLE, GRB.Status.UNBOUNDED):
        print('The relaxed model cannot be solved \
              because it is infeasible or unbounded')
        return(locations,e, n,counter)
        exit(1)
    elif status != GRB.Status.OPTIMAL:
        print('Optimization was stopped with status %d' % status)
        return(locations,e, n, counter)
        exit(1) 
    else:
      return(locations,e, n, counter) 
      exit(0)  


  def makeNoAPIAssignments(N, E, locations):
    # initialise varibales from arguments
    n = len(N)
    e = len(E)
    v = n+e
    Q = n/e
    V = N+E
    A = [(i,j) for i in V for j in V if i != j]
    c = {(i,j):np.hypot(locations[i][0]-locations[j][0],locations[i][1]-locations[j][1]) for i,j in A}

    #plot markers on graph
    plt.clf() 
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
          # S = SUnion[1:-1]
          if len(I) == 0 and len(t)>1:
            print('no empoloyees')
            model.cbLazy(quicksum(x[i,j] for i,j in itertools.combinations(t, 2))<= len(t)-1)
          elif len(SUnion)>0 and len(I)>=2:
            print('more than 1 employee, more than 2 clients')
            model.cbLazy(x[I[0],SUnion[0]] + quicksum(x[i,j] for i in E for j in SUnion if i!=I[0])<=1)
          # elif len(I)>=2 and len(SUnion) == 1:
          #   model.cbLazy(x[I[0],SUnion[0]] + quicksum(x[i,SUnion[0]] for i in E if i!=I[0])<=1)
          # elif len(S)>0 and len(I)>=2:
          #   print('more than 1 employee, more than 2 clients')
          #   model.cbLazy(x[I[0],SUnion[0]] + quicksum(x[i,j] for i in E for j in SUnion if i!=I[0])<=1)
          # elif len(SUnion) == 2 and len(I)>=2:
          #   print('only 2 clients and 2 employees')
          #   model.cbLazy(x[I[0],SUnion[0]] + 3*x[SUnion[0],SUnion[1]] + quicksum(x[i,SUnion[1]] for i in E if i!=I[0])<= 4)    
    
    # Optimize
    m._vars = m.getVars()
    m.params.LazyConstraints = 1
    m.params.Cuts = 0
    m.optimize(subtourelim)
    status = m.status

    if status == GRB.Status.OPTIMAL:
      print('The optimal objective is %g' % m.objVal)
      sol = m.getAttr('x', x)
      selected = [i for i in sol if sol[i] > 0.5]
      finalTour = subtour(selected)
      # print('---------FINAL TOUR-----------')
      # print(finalTour)
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
        return(finalTour,e, n, 'First Try')
        exit(0)
    
    #relax infeasible model once the quickest way
    print('The model is infeasible; relaxing the constraints once')
    # relaxed model keeps deggree constraints
    m.feasRelaxS(0,False, False, True)
    m.optimize(subtourelim)
    status = m.status
    if status == GRB.Status.OPTIMAL:
      print('The optimal objective is %g' % m.objVal)
      sol = m.getAttr('x', x)
      selected = [i for i in sol if sol[i] > 0.5]
      finalTour = subtour(selected)
      print('---------FINAL TOUR-----------')
      print(finalTour)
      print(locations)
      error = False
      for t in finalTour:
        c = 0 
        for node in t:
          if node in E:
            c +=1
        if c!=1:
          error=True
      if not error:
        for i in selected:
          plt.plot(( locations[i[0]][0],locations[i[1]][0]), (locations[i[0]][1],locations[i[1]][1]), color='r')
        # plt.show()
        return(finalTour,e, n, 'First Relaxation')
        exit(0)


  #relax infeasible model until valid solution generated
    counter = 0
    while counter>=0:
    # while True:
      print('The model is infeasible; relaxing the constraints until Feasible')
      con1_1 = m.addConstrs(quicksum(x[i,j] for j in V if j!=i)==1 for i in N)
      con1_2 = m.addConstrs(quicksum(x[i,j] for i in V if i!=j)==1 for j in V)
      con2_1 = m.addConstrs(quicksum(x[i,j] for j in V if j!=i)==1 for i in E)
      con2_2 = m.addConstrs(quicksum(x[i,j] for i in V if i!=j)==1 for j in E)
      m.feasRelax(0, True, x, None, None, None, None)
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
        # print('---------FINAL TOUR-----------')
        # print(finalTour)
        # print(locations)
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
          #   plt.plot(( locations[i[0]][0],locations[i[1]][0]), (locations[i[0]][1],locations[i[1]][1]), color='r')
          # plt.show()
          return(finalTour,e, n, counter)
          exit(0)
      counter +=1
      
    if status in (GRB.Status.INF_OR_UNBD, GRB.Status.INFEASIBLE, GRB.Status.UNBOUNDED):
        print('The relaxed model cannot be solved \
              because it is infeasible or unbounded')
        return(locations,e, n,counter)
        exit(1)
    elif status != GRB.Status.OPTIMAL:
        print('Optimization was stopped with status %d' % status)
        return(locations,e, n, counter)
        exit(1) 
    else:
      return(locations,e, n, counter) 
      exit(0)  

  # makeRandomAssignments()