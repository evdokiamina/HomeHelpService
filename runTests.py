import csv
import HomeHelpService as HHS
import HomeHelpService_Database as DB
import time

with open('testFile_RandomAssignment18_20.csv', 'w', newline='') as f:
  thewriter = csv.writer(f)

  thewriter.writerow(['execution No.', 'time','tour', 'error', 'relax', 'Employee No.', 'Patient No.'])
  for i in range(1):
    start = time.time()
    callHSS = HHS.mainAlgorithm
    tour,e,n, relax = callHSS.makeRandomAssignments()
    end = time.time()
    errorTour = ''
    if len(tour)!=e:
      errorTour = 'Error'
    thewriter.writerow([i, (end-start), tour, errorTour,relax, e, n])
f.close()