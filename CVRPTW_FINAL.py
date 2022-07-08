import numpy as np
import matplotlib.pyplot as plt
from gurobipy import GRB, Model, quicksum
from matplotlib.pyplot import cm


class Modelo_Optimizacion():
    def __init__(self, n, num_vehiculos):
        # nodos
        self.n = n
        self.num_vehiculos= num_vehiculos
        self.clientes = [i for i in range(n) if i !=0]
        self.nodos = [0] + self.clientes
        self.arcos = [(i,j) for i in self.nodos for j in self.nodos if i!=j]
        # Demanda
        np.random.seed(0)
        self.q = {n: np.random.randint(10,15) for n in self.clientes}
        self.q[0] = 0
        # Ventanas de tiempo aleatorias
        self.e = {}
        self.l = {}
        for i in range(n):
            t1 = np.random.randint(0,500)
            t2 =np.random.randint(90,300)
            self.e[i] = t1
            self.l[i] = t1 + t2
        self.e[0] = 0
        self.l[0] = 500 + 300

        # Tiempo de servicio en el nodo i
        self.s = {n:np.random.randint(3,5) for n in self.clientes}
        self.s[0] = 0

        # Vehículos
        self.vehiculos = [i for i in range(num_vehiculos)]
        # Q = 50
        # Q = {1: 50, 2:50, 3:25, 4:25
        self.Q = {i: np.random.choice([50,25,35]) for i in self.vehiculos}

        # Coordenadas
        self.X = np.random.rand(len(self.nodos))*100
        self.Y = np.random.rand(len(self.nodos))*100


        # Distancias y tiempos 
        # Se definen según la euclideana
        self.distancia  = {(i,j): np.hypot(self.X[i] - self.X[j],self.Y[i] - self.Y[j]) for i in self.nodos for j in self.nodos if i!=j}

        # Para los tiempos se puede asumir una velocidad promedio de desplazamiento, ej. 40kmh, pero acá se asume que el tiempo es igual a la distancia
        self.tiempo = {(i,j): np.hypot(self.X[i] - self.X[j],self.Y[i] - self.Y[j]) for i in self.nodos for j in self.nodos if i!=j}

        self.arco_var = [(i,j,k) for i in self.nodos for j in self.nodos for k in self.vehiculos if i!=j]
        self.arco_tiempos = [(i,k) for i in self.nodos for k in self.vehiculos]

    def graficar_inicial(self):
        plt.figure(figsize = (12,5))
        plt.scatter(self.X,self.Y, color = "blue")

        # DC
        plt.scatter(self.X[0],self.Y[0], color = "red", marker = "D")
        plt.annotate("DC|$t_{%d}$= $(%d,%d)$"%(0,self.e[0],self.l[0]), (self.X[0]-1,self.Y[0]-5.5))

        for i in self.clientes:
            plt.annotate("$q_{%d} = %d$ | $t_{%d}$= $(%d,%d)$" %(i,self.q[i],i,self.e[i],self.l[i]), (self.X[i]-1,self.Y[i]+2.5))
        plt.xlabel("Distancia X")
        plt.ylabel("Distancia Y")
        plt.title("Solución Travel Salesman Problem")

        plt.show()

    def optimizar(self):
        self.model = Model("VRPTW")

        # Variables de decision
        self.x = self.model.addVars(self.arco_var, vtype = GRB.BINARY, name = "x")
        self.t = self.model.addVars(self.arco_tiempos, vtype = GRB.CONTINUOUS, name = "t")

        # Funcion Objetivo
        self.model.setObjective(quicksum(self.distancia[i,j]*self.x[i,j,k] for i,j,k in self.arco_var), GRB.MINIMIZE)

        # Restricciones
        self.model.addConstrs(quicksum(self.x[0,j,k] for j in self.clientes) <= 1 for k in self.vehiculos)
        self.model.addConstrs(quicksum(self.x[i,0,k] for i in self.clientes) <= 1 for k in self.vehiculos)
        self.model.addConstrs(quicksum(self.x[i,j,k] for j in self.nodos for k in self.vehiculos if i!=j) == 1 for i in self.clientes)
        self.model.addConstrs((quicksum(self.x[i,j,k] for j in self.nodos if i!=j) - quicksum(self.x[j,i,k] for j in self.nodos if i!=j)) == 0 for i in self.nodos for k in self.vehiculos)
        self.model.addConstrs(quicksum(self.q[i] * quicksum(self.x[i,j,k] for j in self.nodos if i!=j) for i in self.clientes) <= self.Q[k] for k in self.vehiculos)
        self.model.addConstrs((self.x[i,j,k] == 1) >> (self.t[i,k] + self.s[i] + self.tiempo[i,j] == self.t[j,k]) for i in self.clientes for j in self.clientes for k in self.vehiculos if i!=j)
        self.model.addConstrs(self.t[i,k] >= self.e[i] for i,k in self.arco_tiempos)
        self.model.addConstrs(self.t[i,k] <= self.l[i] for i,k in self.arco_tiempos)

        self.model.Params.TimeLimit = 60
        self.model.Params.MIPGap = 0.1
        self.model.optimize()

    def graficar_solucion(self):
        rutas = []
        truck = []

        K = self.vehiculos
        N = self.nodos

        for k in self.vehiculos:
            for i in self.nodos:
                if i != 0 and self.x[0,i,k].x >0.9:
                    aux = [0,i]
                    while i != 0:
                        j = i
                        for h in self.nodos:
                            if j !=h and self.x[j,h,k].x > 0.9:
                                aux.append(h)
                                i = h
                                
                    rutas.append(aux)
                    truck.append(k)


        caminos_por_truck = []
        for i in truck:
            tuplas = []
            for j in range(len(rutas[i])):
                # print(j, rutas[i][j])
                try:
                    tuplas.append((rutas[i][j],rutas[i][j + 1]))
                except:
                    pass
            caminos_por_truck.append(tuplas)

        print(rutas)
        print(caminos_por_truck)
        plt.figure(figsize = (12,5))
        plt.scatter(self.X,self.Y, color = "blue")

        # DC
        plt.scatter(self.X[0],self.Y[0], color = "red", marker = "D")
        plt.annotate("DC|$t_{%d}$= $(%d,%d)$"%(0,self.e[0],self.l[0]), (self.X[0]-1,self.Y[0]-5.5))

        for i in self.clientes:
            plt.annotate("$q_{%d} = %d$ | $t_{%d}$= $(%d,%d)$" %(i,self.q[i],i,self.e[i],self.l[i]), (self.X[i]-1,self.Y[i]+2.5))


        color = iter(cm.rainbow(np.linspace(0, 1, self.num_vehiculos)))
        for v in truck:
            c = next(color)
            for i,j in caminos_por_truck[v]:
                plt.plot([self.X[i],self.X[j]],[self.Y[i],self.Y[j]], alpha=0.4, zorder=0, c = c)

        plt.xlabel("Distancia X")
        plt.ylabel("Distancia Y")
        plt.title("Solución")
        plt.legend()
        plt.show()


if __name__ == "__main__":
    m = Modelo_Optimizacion(14,4)
    # m.graficar_inicial()
    m.optimizar()
    m.graficar_solucion()