from docplex.mp.model import Model
import docplex.mp.solution as Solution
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


class ModeloTCF():
    def __init__(self, time_limit, output_bool =False):
        self.name = "TSPTW-TCF"
        self.time_limit = time_limit
        self.output_bool = output_bool
        

    def build(self,ins):
        # Modelo
        self.mdl = Model('TSPTW-TCF')
        
        # Variables de Decisión
        self.y = self.mdl.integer_var_dict(ins.arcos, name = 'y')
        self.z = self.mdl.integer_var_dict(ins.arcos, name = 'z')


        #  FO
        self.mdl.minimize(self.mdl.sum(ins.c[(i,j)]* (self.y[(i,j)] + self.z[(i,j)])/ins.T for i,j in ins.arcos)) #+ self.mdl.sum(self.w[i] for i in ins.V))

        # Restriccion 9:
        for i in ins.V:
            if i != 1:
                self.mdl.add_constraint(self.mdl.sum(self.z[(i,1)]) + self.mdl.sum((ins.c[(i,1)]*(self.y[(i,1)] + self.z[(i,1)]))/(ins.T)) <= ins.T)

        # Restriccion 10:
        for i in ins.V:
            if i!=1:
                self.mdl.add_constraint(self.mdl.sum(self.y[(i,j)] + self.z[(i,j)] for j in ins.V if j!=i) == ins.T)

        # Restriccion 11:
        for j in ins.V:
            if j!=1:
                self.mdl.add_constraint(self.mdl.sum(self.y[(i,j)] + self.z[(i,j)] for i in ins.V if j!=i) == ins.T)
        

        # Restriccion 12.1:
        for i,j in ins.arcos:
            self.mdl.add_constraint( self.y[i,j] + self.z[i,j] <=ins.T)
        
        # Restriccion 15:
        for i in ins.V:
            if i!=1:
                for j in ins.V:
                    if j!= i:
                        self.mdl.add_constraint(   
                          self.mdl.sum(self.z[(i,j)])
                        - self.mdl.sum(self.z[(j,i)])
                        - self.mdl.sum((ins.c[(i,j)]*(self.y[(j,i)] + self.z[(j,i)]))/ins.T) == 0)

        # Restriccion 16:
        for i in ins.V:
            if i!=1:
                self.mdl.add_constraints([ self.mdl.sum(self.z[(i,j)] for j in ins.V if j!=i) >= ins.a[i] , self.mdl.sum(self.z[(i,j)] for j in ins.V if j!=i) <= ins.b[i]])



    def solve(self,ins):
        self.solucion = self.mdl.solve(log_output= self.output_bool)        
        self.mdl.parameters.timelimit = self.time_limit # tiempo limite
        
        self.arcos_solucion = []
        for i in ins.arcos:
            x = (self.y[(i)].solution_value + self.z[(i)].solution_value)/ins.T
            if x > 0.9:
                self.arcos_solucion.append((i))

        # self.arcos_solucion = [i for i in ins.arcos if ((self.y[(i)].solution_value + self.z[(i)].solution_value)/ins.T) > 0.9]


    def plot(self,ins):
        fig, ax = plt.subplots(figsize=(12,7))
        for i in range(len(ins.V)):
            if i!=0:
                ax.scatter(ins.coord_x[i],ins.coord_y[i],300,color="black",marker = 's',zorder=2)
                ax.annotate(str(i+1),xy=(ins.coord_x[i],ins.coord_y[i]),xytext=(ins.coord_x[i]-0.5,ins.coord_y[i]-0.5), color="white")
            else:
                ax.scatter(ins.coord_x[i],ins.coord_y[i],300,color="red",marker = 's',label='Depósito',zorder=2)
                ax.annotate(str(i+1),xy=(ins.coord_x[i],ins.coord_y[i]),xytext=(ins.coord_x[i]-0.5,ins.coord_y[i]-0.5), color="white")

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
    
    def print_output(self,ins):
        print(
            "\n",
            "Instancia: {}\n".format(ins.instance_name),
            "Tiempo: {:.02}\n".format(self.mdl.get_solve_details().time),
            "Cota Inferior: {}\n".format(self.mdl.get_solve_details().best_bound),
            "Gap: {}\n".format(self.mdl.get_solve_details().gap),
            "Optimo: {}\n".format(self.solucion.get_objective_value()),
            self.mdl.get_solve_status(),
            "\n"
            # self.mdl.tolerances.lowercutoff
            )


class ModeloClasico():
    def __init__(self, time_limit, output_bool =False):
        self.name = "TSPTW"
        self.time_limit = time_limit
        self.output_bool = output_bool


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

    def solve(self,ins):
        self.solucion = self.mdl.solve(log_output= self.output_bool)
        self.mdl.parameters.timelimit = self.time_limit # tiempo limite
        self.arcos_solucion = [i for i in ins.arcos if self.x[i].solution_value>0.9]



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


    def get_permutacion(self,arcos):
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

    def print_output(self,ins):
        print(
            "\n",
            "Instancia: {}\n".format(ins.instance_name),
            "Tiempo: {:.02}\n".format(self.mdl.get_solve_details().time),
            "Cota Inferior: {}\n".format(self.mdl.get_solve_details().best_bound),
            "Gap: {}\n".format(self.mdl.get_solve_details().gap),
            "Optimo: {}\n".format(self.solucion.get_objective_value()),
            self.mdl.get_solve_status(),
            "\n"
            # self.mdl.tolerances.lowercutoff
            )

        # instancia, costo cota inferior, costo optimo, error relativo, tiempo ejecucion.


class my_menu():
    def __init__(self):
        self.choices = {
            0 : self.my_exit,
            1 : self.leerEntrada,
            2 : self.modelo1,
            3 : self.modelo2,

            

            
            }
        self.options = {
            0 : 'Salir',
            1 : 'Leer entrada.txt',
            2 : 'Modelo mátematico 1: ',
            3 : 'Modelo mátematico 2: ',

        }

    def print_welcome(self):
        print(
        """\n
        Bienvenido!
        autores: \n
        Benjamín Brandt\n
        Nicolás Netz \n
        """)
    
    # def log_output_cplex(self):



    def print_options(self):
        for key in self.options.keys():
            print(key,'____',self.options[key])

    def choose_options(self):
        while True:
            while(True):
                try:
                    option = int(input('\nElige una acción: '))
                    break
                except ValueError:
                    print('\nError. Por favor, ingresa un número')

            
            action = self.choices.get(option)
            
            if action:
                action()

            else:
                print('\nOpción invalida. Ingresa un número entre el 1 y el {}'.format(len(self.choices.keys())))
            self.print_options()

    def option(self):
        print('Ejecutando Opcion')

    def my_exit(self):
        print('\nGracias por usar mi programa. \n autores:\nBenjamín Brandt\nNicolás Netz \n')
        exit()

    def execute(self):
        self.print_welcome()
        while True:
            self.print_options()
            self.choose_options()

    def leerEntrada(self):
        self.instancias = []
        with open("entrada.txt") as f:
            for i in f:
                linea = i.strip("\n").split(" ")
                self.instancias.append([linea[0], int(float(linea[1]))])
        print(self.instancias)

    def modelo1(self):
        # Preguntar cuantas instancias quiere resolver si una o las 50.
        while True:
            while(True):
                try:
                    option = int(input('\n Ingrese 1 si desea resolver una instancia ó 0 si desea resolver las 50: '))
                    break
                except ValueError:
                    print('\nError. Por favor, ingresa un número')

            if option == 1:
                # Resolver una instancia
                self.size = 1
                self.exportar_archivo("ModeloMTZ")
                ins = Instancia("instancias/" + self.instancias[0][0])
                modelo = ModeloClasico(self.instancias[0][1])
                modelo.build(ins)
                modelo.solve(ins)
                modelo.print_output(ins)
                modelo.plot(ins)
                self.escribir(ins, "ModeloMTZ", modelo)
                break

            if option == 0:
                # Resolver todas las instancias
                
                self.size = 50
                self.exportar_archivo("ModeloMTZ")
                for instancia in self.instancias:
                    ins = Instancia("instancias/" + instancia[0])
                    modelo = ModeloClasico(instancia[1])
                    modelo.build(ins)
                    modelo.solve(ins)
                    modelo.print_output(ins)
                    self.escribir(ins, "ModeloMTZ", modelo)
                break

            else:
                print('\nOpción invalida. Ingresa un 1 o un 0: ')


    def modelo2(self):
        # Preguntar cuantas instancias quiere resolver si una o las 50.
        while True:
            while(True):
                try:
                    option = int(input('\n Ingrese 1 si desea resolver una instancia ó 0 si desea resolver las 50: '))
                    break
                except ValueError:
                    print('\nError. Por favor, ingresa un número')

            if option == 1:
                # Resolver una instancia
                self.size = 1
                self.exportar_archivo("ModeloTCF")
                ins = Instancia("instancias/" + self.instancias[0][0])
                modelo = ModeloTCF(self.instancias[0][1])
                modelo.build(ins)
                modelo.solve(ins)
                modelo.print_output(ins)
                modelo.plot(ins)
                self.escribir(ins, "ModeloTCF", modelo)
                break

            if option == 0:
                # Resolver todas las instancias
                self.size = 50
                self.exportar_archivo("ModeloTCF")
                for instancia in self.instancias:
                    ins = Instancia("instancias/" + instancia[0])
                    modelo = ModeloTCF(instancia[1])
                    modelo.build(ins)
                    modelo.solve(ins)
                    modelo.print_output(ins)
                    self.escribir(ins, "ModeloTCF", modelo)
                    
                break

            else:
                print('\nOpción invalida. Ingresa un 1 o un 0: ')

    def escribir(self,ins, nombreDestino,modelo):
        self.archivo = open("{}_{}".format(nombreDestino,self.size), 'a')
        self.archivo.write('\n')
        self.archivo.write( ' ' + str(ins.instance_name) + ' ' 
        + str(modelo.mdl.get_solve_details().best_bound) + ' ' 
        + str(modelo.solucion.get_objective_value()) + ' ' 
        + str(modelo.mdl.get_solve_details().gap) + ' '
        + str(modelo.mdl.get_solve_details().time))
        self.archivo.close()
    

    def exportar_archivo(self, nombreDestino):
        self.archivo = open("{}_{}".format(nombreDestino,self.size), 'w')
        self.archivo.write(' ' + 'Instancia' + ' ' + 'Cota Inferior' + ' ' 
        + 'Mejor Costo' + ' ' 
        + 'Error relativo' + ' '
        + 'Tiempo' )
        self.archivo.close()
        


if __name__ == "__main__":
    mi_menu = my_menu()
    mi_menu.execute()

