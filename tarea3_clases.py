from docplex.mp.model import Model
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Clase instancia

class Instancia:
    def __init__(self, instance = "instancias/n20w120.001.txt"):
        self.instance_name = instance.split("/")[1]
        print(self.instance_name)
        # Parámetros
        self.cust_no = None
        self.coord_x = None
        self.coord_y = None
        self.demand = None
        self.ready_time = None
        self.due_date = None
        self.service_time = None
        # Leer archivo
        self.problem = self.leer_archivo(instance)
    
    def leer_archivo(self,instance):
        # Lectura de instancias
        file_head = []
        cols_head = []
        instance_data = []
        with open(instance, "r") as f:
            file = f.readlines()
            file_head = file[0].replace("\n","").split("\t")[0].split(" ")
            file_head = "{} {} {}".format(file_head[1],file_head[5],file_head[6])
            cols_head = file[3].replace("\n","").split("\t")
            for line in file[6:-1]:
                splited_line = line.replace("\n","").split("\t")
                instance_data.append(splited_line)

        # Convertir en array
        instance_data = np.array(instance_data).astype(int)
        self.cust_no = instance_data[:,0]
        self.coord_x = instance_data[:,1]
        self.coord_y = instance_data[:,2]
        self.demand = instance_data[:,3]
        self.ready_time = instance_data[:,4]
        self.due_date = instance_data[:,5]
        self.service_time = instance_data[:,6]
        self.file_head = file_head

        self.client_data = {}
        self.client_data[0] = [0,0,0,0,10000,0]
        for line in instance_data:
            self.client_data[line[0]] = [line[1],line[2],line[3],line[4],line[5],line[6]]
        

    def __repr__(self):
        return("Instancia: {} con {} clientes y header {}".format(self.instance_name,len(self.demand), self.file_head))

class Modelo:
    def __init__(self):
        pass

instance = Instancia()


velocidad = 1
V = [i for i in instance.client_data.keys()]
arcos = [(i,j) for i in V for j in V if i!=j]
d = {(i,j): int(np.hypot(instance.client_data[i][0] - instance.client_data[j][0],instance.client_data[i][1] - instance.client_data[j][1])) for i in V for j in V if i!=j}
c = {(i,j): np.hypot(instance.client_data[i][0] - instance.client_data[j][0],instance.client_data[i][1] - instance.client_data[j][1]) for i in V for j in V if i!=j}


M = 10000
a = {i: instance.client_data[i][3] for i in V}
b = {i: instance.client_data[i][4] for i in V}

# Modelo
mdl = Model('TSPTW')

# Variables de decisión
x = mdl.binary_var_dict(arcos,name= 'x')
u = mdl.integer_var_dict(V, name= 'u')

# Funcion Objetivo
mdl.minimize(mdl.sum(x[(i,j)]*c[(i,j)] for i,j in arcos))

# Restricción 2: Un arco saliente de cada vertice
for i in V:
    mdl.add_constraint(mdl.sum(x[(i,j)] for j in V if i!=j) == 1)

# Restricción 3: Un arco saliente de cada vertice
for i in V:
    mdl.add_constraint(mdl.sum(x[(j,i)] for j in V if i!=j) == 1)

# Restricción 4: Subrutas MTZ
for i,j in arcos:
    if i!=0:
        # mdl.add_constraint(u[i]-u[j] + c[(i,j)] <=((M)*(1-x[(i,j)])))
        mdl.add_constraint(u[i]-u[j] + M*x[(i,j)] <= M - c[(i,j)])

# # Restriccion 5: Ventana de tiempo
# for i in V:
#     mdl.add_constraint(a[i] <= u[i])

# # # Restriccion 5: Ventana de tiempo
# for i in V:
#     mdl.add_constraint(u[i] <= b[i])

# Restriccion: Ventana de tiempo
for i in V:
    mdl.add_constraints([a[i] <= u[i] ,u[i] <= b[i]])



# print(mdl.export_to_string())

solucion = mdl.solve(log_output= True)

print(mdl.get_solve_status())

print(solucion.display())


arcos_solucion = [i for i in arcos if x[i].solution_value>0.9]


def plot():
    fig, ax = plt.subplots(figsize=(12,7))
    for i in V:
        if i!=0:
            ax.scatter(instance.client_data[i][0],instance.client_data[i][1],300,color="black",marker = 's',zorder=2)
            ax.annotate(str(i),xy=(instance.client_data[i][0],instance.client_data[i][1]),xytext=(instance.client_data[i][0]-0.5,instance.client_data[i][1]-0.5), color="white")
        else:
            ax.scatter(instance.client_data[i][0],instance.client_data[i][1],300,color="red",marker = 's',label='Depósito',zorder=2)
            ax.annotate(str(0),xy=(instance.client_data[i][0],instance.client_data[i][1]),xytext=(instance.client_data[i][0]-0.5,instance.client_data[i][1]-0.5), color="white")

    for i,j in arcos_solucion:
        plt.plot([instance.client_data[i][0],instance.client_data[j][0]],[instance.client_data[i][1],instance.client_data[j][1]],color='black',zorder=1)

    DPatch = mpatches.Patch(color='red',label='Deposito')
    ISolPatch = mpatches.Patch(color='black',label='Cliente')
    plt.legend(handles=[DPatch, ISolPatch])

    plt.xlabel("Coordenada x")
    plt.ylabel("Coordenada y")
    plt.title("Solución instancia")
    
    # plt.savefig("fig.png")
    plt.show()

plot()

print(arcos_solucion)

