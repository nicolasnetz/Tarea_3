from docplex.mp.model import Model
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches



class Instancia:
    def __init__(self, instance = "instancias/n20w120.001.txt"):
        self.instance_name = instance.split("/")[1]
        print(self.instance_name)
        # Parámetros
        self.M = 10000
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
        
        
        self.V = instance_data[:,0]
        self.arcos = [(i,j) for i in self.V for j in self.V if i!=j]
        self.a = {i: instance_data[:,4][i-1] for i in self.V}
        self.b = {i: instance_data[:,5][i-1] for i in self.V}
        self.c = {(i,j): int(np.hypot(self.coord_x[i-1] - self.coord_x[j-1] , self.coord_y[i-1] - self.coord_y[j-1])) for i,j in self.arcos}

        self.W = {i: [i for i in range(self.a[i], self.b[i])] for i in self.V}
        self.p = self.V[0]
        self.q = self.V[0]

        self.w_tilda = {(i,j): max(0, self.a[j] - self.a[i] - self.c[i,j]) for i,j in self.arcos}

        self.T = self.b[1]

    def __repr__(self):
        return("Instancia: {} con {} clientes y header {}".format(self.instance_name,len(self.demand), self.file_head))

class ModeloClasico():
    def __init__(self):
        self.name = "TSPTW"

    def build(self,ins):
        # Modelo
        self.mdl = Model('TSPTW')

        # Variables de decisión
        self.x = self.mdl.binary_var_dict(ins.arcos,name= 'x')
        self.u = self.mdl.integer_var_dict(ins.V, name= 'u', lb=0)

        # Restricción 1: Funcion Objetivo
        self.mdl.minimize(self.mdl.sum(self.x[(i,j)]*ins.c[(i,j)] for i,j in ins.arcos))

        # Restricción 2: Un arco saliente de cada vertice
        for i in ins.V:
            self.mdl.add_constraint(self.mdl.sum(self.x[(i,j)] for j in ins.V if i!=j) == 1, ctname = "restriccion2: x_%d" %(i))

        # Restricción 3: Un arco saliente de cada vertice
        for i in ins.V:
            self.mdl.add_constraint(self.mdl.sum(self.x[(j,i)] for j in ins.V if i!=j) == 1, ctname = "restriccion3: x_%d" %(i))

        # Restricción 4: Subrutas MTZ
        for i,j in ins.arcos:
            if i!=1:
                self.mdl.add_constraint(self.u[i]-self.u[j] + ins.M*self.x[(i,j)] <= ins.M - ins.c[(i,j)], ctname = "restriccion4: x_%d_%d" %(i,j))

        # Restricción 5: Ventanas de Tiempo
        for i in ins.V:
            self.mdl.add_constraints([ins.a[i] <= self.u[i] ,self.u[i] <= ins.b[i]])

        # print(self.mdl.pprint_as_string())

    def solve(self):
        self.solucion = self.mdl.solve(log_output= True)


        print(self.mdl.get_solve_status())
        print(self.solucion)
        self.arcos_solucion = [i for i in ins.arcos if self.x[i].solution_value>0.9]
        print(self.arcos_solucion)

    def sol_inicial(self):
        self.mdl.parameters.timelimit = 10 # tiempo limite
        self.mdl.solutionlimit = 1
        self.mdl.parameters.emphasis.mip = 1
        self.solucion = self.mdl.solve(log_output= True)
        self.arcos_solucion = [i for i in ins.arcos if self.x[i].solution_value>0.9]
        print(self.solucion)
        print(self.mdl.get_solve_status())
        

    def plot(self,ins):
        fig, ax = plt.subplots(figsize=(12,7))
        for i in range(len(ins.V)):
            if i!=0:
                ax.scatter(ins.coord_x[i],ins.coord_y[i],300,color="black",marker = 's',zorder=2)
                ax.annotate(str(i +1),xy=(ins.coord_x[i],ins.coord_y[i]),xytext=(ins.coord_x[i]-0.5,ins.coord_y[i]-0.5), color="white")
            else:
                ax.scatter(ins.coord_x[i],ins.coord_y[i],300,color="red",marker = 's',label='Depósito',zorder=2)
                ax.annotate(str(i + 1),xy=(ins.coord_x[i],ins.coord_y[i]),xytext=(ins.coord_x[i]-0.5,ins.coord_y[i]-0.5), color="white")

        for i,j in self.arcos_solucion:
            plt.plot([ins.coord_x[i-1],ins.coord_x[j-1]],[ins.coord_y[i-1],ins.coord_y[j-1]],color='black',zorder=1)

        DPatch = mpatches.Patch(color='red',label='Deposito')
        ISolPatch = mpatches.Patch(color='black',label='Cliente')
        plt.legend(handles=[DPatch, ISolPatch])

        plt.xlabel("Coordenada x")
        plt.ylabel("Coordenada y")
        plt.title("Solución instancia")
        
        # plt.savefig("fig.png")
        plt.show()


    def get_permutacion(self):
        arcos = self.arcos_solucion
        camino = []
        n = len(arcos)
        actual = arcos[0][0]
        sig = arcos[0][1]
        camino.append(actual)
        camino.append(sig)
        ultimo = int()
        i = 1

        while camino[0] != ultimo:
            if sig == arcos[i][0]:
                actual = sig
                sig = arcos[i][1]
                if sig not in camino:
                    camino.append(sig)
                ultimo = sig
                i = 1
            else:
                i +=1

        return(camino)

class ModeloHeuristico():
    def __init__(self, ins):
        V = ins.V
        a = ins.a
        b = ins.b
        c = ins.c
        u = 0

        camino = [V[0]]

        def validar_solucion(camino):
            u = {}
            u[camino[0]] = 0
            for i in range(len(camino)):
                try:
                    if u[camino[i]] + c[(camino[i], camino[i + 1])] >= a[camino[i + 1]]:
                        if u[camino[i]] + c[(camino[i], camino[i + 1])] <= b[camino[i + 1]]:
                            u[camino[i+1]] = u[camino[i]] + c[(camino[i], camino[i + 1])]
                        else:
                            return(False)
                    else:
                        u[camino[i+1]] = a[camino[i + 1]]
                
                except:
                    if u[camino[i]] + c[(camino[i], camino[0])] >= a[camino[0]]:
                        if u[camino[i]] + c[(camino[i], camino[0])] <= b[camino[0]]:
                            u[camino[0]] = u[camino[i]] + c[(camino[i], camino[0])]
                        else:
                            return(False)
                    else:
                        u[camino[0]] = a[camino[0]]

            return(True)

        
        def f(i,j):
            return (b[j] - (u + c[i,j]))

        def g(camino, candidatos):
            i = camino[-1]
            d = {j: f(i,j) for j in candidatos}
            return(min(d, key = d.get))
        

        count = 0

        while len(camino)!=len(V):
            # mientras no estén todos los nodos, elegir entre los nodos candidatos aquel que tenga menor f(i,j) e insertarlo
            candidatos = [i for i in V if i not in camino]
            mejor_candidato = g(camino,candidatos)           

            if u + c[camino[-1], mejor_candidato] > a[mejor_candidato]:
                u = u + c[camino[-1], mejor_candidato]
            else:
                u = a[mejor_candidato]

            camino.append(mejor_candidato)

            if validar_solucion(camino):
                continue
            else:
                # Quitar el mejor_candidato del camino y agregarlo en una posicion más atras, de tal manera que sea factible.
                
                for i in range(len(camino), 0, -1):
                    
                    if u - c[i,mejor_candidato] > b[i]:
                        break



if __name__ == "__main__":
    ins = Instancia("instancias/n40w200.004.txt")
    # modelo = ModeloClasico()
    # modelo.build(ins)
    # modelo.sol_inicial()
    # print(modelo.get_permutacion())
    ModeloHeuristico(ins)