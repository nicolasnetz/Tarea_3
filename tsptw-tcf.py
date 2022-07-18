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
        self.q = self.V[-1]

        self.w_tilda = {(i,j): max(0, self.a[j] - self.a[i] - self.c[i,j]) for i,j in self.arcos}

        self.T = self.b[1]

    def __repr__(self):
        return("Instancia: {} con {} clientes y header {}".format(self.instance_name,len(self.demand), self.file_head))


class ModeloCalvo():
    def __init__(self):
        self.name = "TSPTW-TCF"

    def build(self,ins):
        # Modelo
        self.mdl = Model('TSPTW-TCF')
        
        # Variables de Decisión
        self.y = self.mdl.integer_var_dict(ins.arcos, name = 'y')
        self.z = self.mdl.integer_var_dict(ins.arcos, name = 'z')

        # Restriccion 1: FO
        self.mdl.minimize(self.mdl.sum(ins.c[(i,j)]* (self.y[(i,j)] + self.z[(i,j)]) for i,j in ins.arcos)/ins.T)

        # Restriccion 2:
        self.mdl.add_constraint(self.mdl.sum(self.z[i,1]  for i in ins.V if i != 1) + self.mdl.sum(((ins.c[i,1]*(self.y[i,1] + self.z[i,1]))/(ins.T))  for i in ins.V if i != 1) <= ins.T)

        # # Restriccion 3:
        # for i in ins.V:
        #     if i!=1:
        #         self.mdl.add_constraint(self.mdl.sum(self.y[i,j] + self.z[i,j] for j in ins.V if i!=j) == ins.T)

        # # Restriccion 4:
        # for j in ins.V:
        #     if j!=1:
        #         self.mdl.add_constraint(self.mdl.sum(self.y[i,j] + self.z[i,j] for i in ins.V if i!=j) == ins.T)
        
        # # Restriccion 5:
        # for i,j in ins.arcos:
        #     self.mdl.add_constraints([self.y[i,j] + self.z[i,j] >=0 , self.y[i,j] + self.z[i,j] <=ins.T ])

        # Restriccion 5:
        for i,j in ins.arcos:
            self.mdl.add_constraint(self.y[i,j] + self.z[i,j] <=ins.T)
        
        # Restriccion 6:
        for i in ins.V:
            if i!=1:
                self.mdl.add_constraint(   
                    self.mdl.sum(self.z[i,j] for j in ins.V if j!=i)
                    - self.mdl.sum(self.z[j,i] for j in ins.V if j!=i)
                    - self.mdl.sum((ins.c[i,j]*(self.y[j,i] + self.z[j,i]))/ins.T for j in ins.V if i!=j) == 0
                )

        # Restriccion 7:
        for i in ins.V:
            if i!=1:
                self.mdl.add_constraints([ self.mdl.sum(self.z[i,j] for j in ins.V if i!=j) >= ins.a[i] , self.mdl.sum(self.z[i,j] for j in ins.V if i!=j) <= ins.b[i]])
        
    def solve(self):
        self.solucion = self.mdl.solve(log_output= True)

        print(self.mdl.get_solve_status())
        print(self.solucion)
        self.arcos_solucion = [i for i in ins.arcos if self.x[i].solution_value>0.9]
        print(self.arcos_solucion)



if __name__ == "__main__":
    ins = Instancia()
    modelo = ModeloCalvo()
    modelo.build(ins)
    # print(modelo.mdl.export_to_string())
    modelo.solve()