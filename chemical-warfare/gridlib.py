import random as rd
import numpy as np
import classes as cl
import vtktools
import present as pres
import hl

threeD=0                          #3d or 2d
#Parametersettings#
x=50                             #sets gridsize
n=0.5                             #set chance of cells t probability
place=1.0                         #set on_state cells n probability
C_on=18.1                         #signalconcentration of activ cel#
K =  18.0                         #threshold c#
feedback = 1                      #positiv(1) or negative(0) feedback#

radius=1                          #set intial radius of cell
maxrad=2*radius
maxvolume=2 * np.pi * radius ** 2      #max r which cell can have before division#
if threeD:
    maxvolume=2 * 4 * np.pi * radius ** 3
k=1.0                             #factor how close neighboring cells can be 1.0 just touching

g_rater=0.125                          #growthrate of radius for resistent cell
g_ratet=0.05                         #growthrate of radius for toxic cell
g_ratew=0.125                          #growthrate of radius for sensitive/work cell

rangetox= 2.0                       #kill range of toxic cell times in radius

ratio=9                             #sets ratio of resistint, sensitiv/work and toxic cell

F_g = 0.0001                       #gravity constant


thres_skr=0.3                     #threshold for skrinking

cell_age=0
maxcell_age=6

# Dimensions
nx, ny, nz = x, x, 1
if threeD:
    nz = x
lx, ly, lz = 100.0, 1000.0, 0.1
if threeD:
    lz = 10.0
dx, dy, dz = lx/nx, ly/ny, lz/nz

ncells = nx * ny * nz
npoints = (nx + 1) * (ny + 1) * (nz + 1)

# Coordinates
x_c = np.arange(0, lx + dx, dx, dtype='float64')
y_c = np.arange(0, ly + dy, dy, dtype='float64')
z_c = np.arange(0, lz + dz, dz, dtype='float64')


C_t=[]                        # concentrations at time step#
state_t=[]                    #lists all individual cellstates at timestep#

resident=np.zeros(npoints)    #spot has cell or not| int references#
c_ary= {}                     #cell-class ref#
pos={}                        #dic for grid [0]=x_axis [1]=y_axis#

ita=40                        #iteration of movefunc, cause explicit procedure

#setup of model and cells

def initialize():                                       #creats grid on which cells are placed by chance
    global c_ary
    if not threeD:
        ce = 0
        for row in range(x):                     #grid saved in a dic#
            for col in range(x):
                pos[ce] = [x_c[col], y_c[row]]
                ce += 1
    else:
        ce = 0
        for wth in range(x):
            for row in range(x):                 #grid saved in a dic#
                for col in range(x):

                    pos[ce] = [x_c[col], y_c[row],z_c[wth]]
                    ce += 1

    if not threeD:
        c_num = 0
        start= 0
        stop = (x) * (maxrad)
        step=1

        print start,stop
        for cc in range(start,stop,step):                        #cells being placed#
            put = rd.randint(0, ratio)

            if cc == stop:  # only one horizontal row used#
                break

            if border(cc):  # checks for outofbounds around edges#
                if checkneighbor(cc):  # check if cell can be placed#

                    if put > 0:
                        putty=rd.randint(0,1)

                        if putty==0:
                            c_ary[c_num] = cl.Cell(c_num, 'work', radius, stategamble(), pos[cc][0],
                                                   min(pos[cc][1], radius), maxrad)
                            occupy(cc, c_num)
                            c_num += 1
                        else:
                            c_ary[c_num] = cl.Cell(c_num, 'res', radius, stategamble(), pos[cc][0],
                                                   min(pos[cc][1], radius), maxrad)
                            occupy(cc, c_num)
                            c_num += 1

                    elif put == 0:
                        c_ary[c_num] = cl.Cell(c_num, 'toxic', radius, stategamble(), pos[cc][0],
                                               min(pos[cc][1], radius), maxrad)
                        occupy(cc, c_num)
                        c_num += 1


    else:
        setcells()

    #cgrad = cl.C_grad(len(c_ary), x, n, place, C_on, K, feedback, c_ary, threeD)
    #C_i, state = cgrad.ini_cell_c()

    #C_t.append(list(C_i))
    #state_t.append(list(state))

    global fx
    global fy
    global fz
    fx = np.zeros(len(c_ary))
    fy = np.zeros(len(c_ary))
    fz = np.zeros(len(c_ary))

def setcells():

    c_num = 0

    start=0

    stop1=x**3
    step1=x**2

    stop2=x
    step2=1


    for i in range(start, stop1, step1):  # cells being placed#
        for j in range(start,stop2,step2):
            cor =radius*x
            cc=i+j+cor


            if cc == stop1:  # only one horizontal row used#
                break

            put = rd.randint(0, 2)

            if border(cc):  # checks for outofbounds around edges#
                if checkneighbor(cc):  # check if cell can be placed#

                    if put == 0:
                        c_ary[c_num] = cl.Cell(c_num, 'work', radius, stategamble(), pos[cc][0],
                                               min(pos[cc][1], radius), maxrad)
                        occupy(cc, c_num)
                        c_num += 1

                    elif put == 1:
                        c_ary[c_num] = cl.Cell(c_num, 'toxic', radius, stategamble(), pos[cc][0],
                                               min(pos[cc][1], radius), maxrad)
                        occupy(cc, c_num)
                        c_num += 1
                    elif put == 2:
                        c_ary[c_num] = cl.Cell(c_num, 'res', radius, stategamble(), pos[cc][0],
                                               min(pos[cc][1], radius), maxrad)
                        occupy(cc, c_num)
                        c_num += 1

def stategamble():                      #prodces random booleanvalue according to place
                                        #usage: setting initial state of cell
    hp = rd.random()
    if hp <= place:
        return True
    else:
        return False

def border(pt):                         #checks for outofbounds around edges #


    if pos[pt][0] - radius < 0 :
        print ('hey b_3')
        return False
    if pos[pt][1] - radius < 0 :
        print ('hey b_o4')
        return False


    if pos[pt][0] + radius > lx:
        print ('hey b_5')
        return False
    if pos[pt][1] + radius > ly:
        print ('hey b_6')
        return False

    if threeD:
        if pos[pt][2] - radius < 0:
            print ('hey b_o4')
            return False
        if pos[pt][2] + radius > lz:
            print ('hey b_6')
            return False


    if pt >= (ncells) or pt < 0:
        print ('out')
        return False
    else:
        print ('hey b_ok')
        return True

def checkneighbor(p):                   #check if cell can be placed#

    ind = True

    if resident[p]!= 0:
        print('str')
        return False

    if maxrad > dx or maxrad > dy or maxrad > dz:

            ind = outersq(p)

    return ind

def outersq(p):

    rad = radius

    for h in range(-rad, rad + 1):      #go along the (row)
        for b in range(-rad, rad + 1):  #outer quadrate of the circle r=rad (col)
            for l in range(-rad, rad + 1):

                poi = p + l + b * x        #position in the chain

                z_cir=0
                if threeD:
                    poi += h * x * x

                if poi >= ncells:
                    print ('hey f1')
                    return False
                if poi < 0:
                    print ('hey f2')
                    return False

                if threeD:
                    z_cir = (pos[poi][2] - pos[p][2]) ** 2

                eq = np.sqrt((pos[poi][0] - pos[p][0]) ** 2 + (pos[poi][1] - pos[p][1]) ** 2 + z_cir )

                if eq <= rad:               #if smaller or same than position inside the cell

                    if resident[poi] != 0:
                        print ('hey f3')
                        return False

    return True

def occupy(m,id):                              #cellplacement

    if isinstance(c_ary[id], cl.Cell):       #get cell_r for placement#
        rad = radius

        if maxrad > dx or maxrad > dy:

            for h in range(-rad,rad+1):         # go along the (row)
                for b in range(-rad,rad+1):     #outer quadrate of the circle r=rad (col)
                    for l in range(-rad, rad + 1):

                        poi = m + l + b * x    # position in the chain
                        z_cir = 0
                        if threeD:
                            poi += h * x * x
                            z_cir = (pos[poi][2] - c_ary[id].zcor) ** 2

                        if poi == m:
                            pass

                        eq = np.sqrt((pos[poi][0] - c_ary[id].xcor) ** 2 + (pos[poi][1] - c_ary[id].ycor) ** 2 + z_cir )

                        if eq <= rad:               #if smaller or same than position inside the cell

                            if resident[poi] == 0 :
                                resident[poi] = c_ary[id].mid
        else:
            resident[m] = c_ary[id].mid

#runtime of the model with all its calculations

def force():                                    #calculates movement by forcecalc of cells pushing

    global fx
    global fy
    global fz
    global del_keys

    del_keys=[]

    fx = np.zeros(len(c_ary))
    fy = np.zeros(len(c_ary))
    fz = np.zeros(len(c_ary))


    thres = np.zeros(len(c_ary))  # array for saving the fac as threshold
    for elem in c_ary:
        fx[elem]=0
        fy[elem]=0
        fz[elem]=0
        if c_ary[elem].name=='dead':
            continue
        for oths in c_ary:

            if c_ary[oths].name == 'dead':
                continue

            sum=np.square(c_ary[oths].xcor-c_ary[elem].xcor)\
            +np.square(c_ary[oths].ycor-c_ary[elem].ycor)\
            +np.square(c_ary[oths].zcor-c_ary[elem].zcor)

            d_n=np.sqrt(sum)                            #actual distance of two cells

            R = c_ary[oths].radius+c_ary[elem].radius

            if c_ary[oths].name == 'toxic':
                if c_ary[elem].name == 'work':
                    if d_n < rangetox * R:
                        print ("kill")
                        c_ary[elem].name = 'dead'
                        c_ary[elem].status= False
                        c_ary[elem].radius=0


            if d_n == 0:
                if oths==elem:
                    continue
                else:
                    d_n=0.00001



            elif d_n < k*R :                           #checks if cell[elem] is pushed by cell[y] only when d_n < R
                fac = (k * R) - d_n

                xdd = -(c_ary[oths].xcor - c_ary[elem].xcor) / d_n
                ydd = -(c_ary[oths].ycor - c_ary[elem].ycor) / d_n
                zdd = -(c_ary[oths].zcor - c_ary[elem].zcor) / d_n

                thres[oths]= max(fac,thres[oths])

                fx[elem] = xdd * fac + fx[elem]
                fy[elem] = ydd * fac + fy[elem]
                if threeD:
                    fz[elem] = zdd * fac + fz[elem]

        thres[elem]=max(thres)

    return max(thres)

def move():                                                 #cells being moved as forces dictate

    thrs = force()

    if not max(np.square(max(fx)),np.square(max(fy)),np.square(max(fz))) == 0:
        dt = 0.1 / np.sqrt(max(np.square(max(fx)),
                       np.square(max(fy)),
                       np.square(max(fz))))
    else:
        dt = 0.1

    for elem in c_ary:
        grav = -4 * np.pi * (c_ary[elem].radius**3) * F_g
        y_cor=max(c_ary[elem].radius,min((c_ary[elem].ycor + dt * fy[elem] + grav),(ly-c_ary[elem].radius)))

        c_ary[elem].xcor = max(min(c_ary[elem].xcor + dt*fx[elem],(lx-c_ary[elem].radius)),c_ary[elem].radius)
        c_ary[elem].ycor = max(y_cor,c_ary[elem].radius)
        if threeD:
            c_ary[elem].zcor = max(min(c_ary[elem].zcor + dt*fz[elem],(lz-c_ary[elem].radius)),c_ary[elem].radius)

    return thrs

def rdspot():      #after muller 1959/Marsaglia 1972 picking random point on sphere uniform

    x_r = rd.gauss(0, 1)
    y_r = rd.gauss(0, 1)
    if threeD:
        z_r = rd.gauss(0, 1)
    else:
        z_r=0
    uni = np.sqrt(np.square(x_r) + np.square(y_r) + np.square(z_r))

    x_r = (x_r * radius) / uni
    y_r = (y_r * radius) / uni
    z_r = (z_r * radius) / uni

    return x_r, y_r, z_r

def divide(p):        #takes rd point and places new cell

    xn,yn,zn=rdspot()
    xn = max((xn + c_ary[p].xcor),radius)
    yn = max((yn + c_ary[p].ycor),radius)
    if threeD:
        zn = max((zn + c_ary[p].zcor),radius)
    else:
        zn=2
    c_num=max(c_ary.keys())
    
    rnew=0.79370052598*c_ary[p].radius

    if c_ary[p].name=='work':
        c_ary[c_num+1] = cl.Cell(c_num+1, 'work', rnew, stategamble(), xn, yn, zn)
    elif c_ary[p].name=='toxic':
        c_ary[c_num+1] = cl.Cell(c_num+1, 'toxic', rnew, stategamble(), xn, yn, zn)
    elif c_ary[p].name == 'res':
        c_ary[c_num + 1] = cl.Cell(c_num + 1, 'res', rnew, stategamble(), xn, yn, zn)
    c_ary[p].radius = rnew
    c_ary[p].status = True

def growth(p):

    if c_ary[p].name == 'work':
        c_ary[p].radius = c_ary[p].radius + g_ratew
    elif c_ary[p].name == 'res':
        c_ary[p].radius = c_ary[p].radius + g_rater
    elif c_ary[p].name == 'toxic':
        c_ary[p].radius = c_ary[p].radius + g_ratet


def chk_vol():

    cvol=0
    if threeD:
        for elem in c_ary:
            cvol += 4 * np.pi * c_ary[elem].radius ** 3
    else:
        for elem in c_ary:
            cvol += np.pi * c_ary[elem].radius ** 2

    cubus=(lx)*(ly)

    if threeD:
        cubus *= lz

    print str(cvol)+'******'+str(cubus)
    print ncells

    if cubus - 1.0E-6 > cvol:
        return True
    else:
        return False

def event(step):                                #what happens to cell in time step

    print(step)

    if chk_vol():
        for elem in c_ary.keys():               #keys()cause new created cells do nothing
            if threeD:
                cvol = 4 * np.pi * c_ary[elem].radius ** 3
            else:
                cvol = np.pi * c_ary[elem].radius ** 2

            if cvol > maxvolume - 1.0E-6:    #cell_r big enough -> division#

                divide(elem)

            else:
                growth(elem)                    #growfunc determines if grow or shrink#

    #cgrad = cl.C_grad(len(c_ary), x, n, place, C_on, K, feedback, c_ary, threeD)

    for i in range(ita):
        thres = move()
        if thres <= 0.1:
            break

    #C_true = cgrad.calc_cval(step,C_t)                          #actual c of cells

    #gridprint(step, C_true)

    #C_i,state = cgrad.switch()
    #switch_cary(state)

    #state_t.append(list(state))
    #C_t.append(list(C_i))

def switch_cary(state):                 #updates cell.status

    for elem in c_ary:
        c_ary[elem].status = state[elem]

def pic(a):                     #creats vtu data with cell situation at time step

    x_list = []
    y_list = []
    z_list = []
    r_list = []
    F_x = []
    F_y = []
    F_z = []


    vtk_writer = vtktools.VTK_XML_Serial_Unstructured()

    for elem in c_ary:
        if c_ary[elem].name == 'toxic':

            x_list.append(c_ary[elem].xcor)
            y_list.append(c_ary[elem].ycor)
            z_list.append(c_ary[elem].zcor)
            r_list.append(c_ary[elem].radius)
            F_x.append(fx[elem])
            F_y.append(fy[elem])
            F_z.append(fz[elem])


    vtk_writer.snapshot("cell_arrangements"+str(a)+".vtu", x_list, y_list, z_list, radii=r_list, x_force=F_x, y_force=F_y,
                        z_force=F_z)
    vtk_writer.writePVD("cell_arrangements"+str(a)+".pvd")

def picw(a):  # creats vtu data with cell situation at time step

    x_list = []
    y_list = []
    z_list = []
    r_list = []
    F_x = []
    F_y = []
    F_z = []

    vtk_writer = vtktools.VTK_XML_Serial_Unstructured()

    for elem in c_ary:
        if c_ary[elem].name == 'work':
            x_list.append(c_ary[elem].xcor)
            y_list.append(c_ary[elem].ycor)
            z_list.append(c_ary[elem].zcor)
            r_list.append(c_ary[elem].radius)
            F_x.append(fx[elem])
            F_y.append(fy[elem])
            F_z.append(fz[elem])

    vtk_writer.snapshot("cell_arrangements_work" + str(a) + ".vtu", x_list, y_list, z_list, radii=r_list,
                        x_force=F_x,
                        y_force=F_y, z_force=F_z)
    vtk_writer.writePVD("cell_arrangements_work" + str(a) + ".pvd")


def picr(a):  # creats vtu data with cell situation at time step

    x_list = [0]
    y_list = [0]
    z_list = [0]
    r_list = [0]
    F_x = [0]
    F_y = [0]
    F_z = [0]

    vtk_writer = vtktools.VTK_XML_Serial_Unstructured()

    for elem in c_ary:
        if c_ary[elem].name == 'res':
            x_list.append(c_ary[elem].xcor)
            y_list.append(c_ary[elem].ycor)
            z_list.append(c_ary[elem].zcor)
            r_list.append(c_ary[elem].radius)
            F_x.append(fx[elem])
            F_y.append(fy[elem])
            F_z.append(fz[elem])

    vtk_writer.snapshot("cell_arrangements_res" + str(a) + ".vtu", x_list, y_list, z_list, radii=r_list,
                        x_force=F_x,
                        y_force=F_y, z_force=F_z)
    vtk_writer.writePVD("cell_arrangements_res" + str(a) + ".pvd")


def pictures(a):
    picw(a)
    pic(a)
    picr(a)

def update(end):

    start = 0
    time = range(start, end)

    initialize()

    for step in time:

        pictures(step)

        event(step)

        st = step

    pictures(st)


#run program

update(20)