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




class my_menu():
    def __init__(self):
        self.choices = {
            0 : self.my_exit,
            1 : self.leerEntrada,
            2 : self.modelo1,
            3 : self.option,
            4 : self.option,
            5 : self.option

            
            }
        self.options = {
            0 : 'Salir',
            1 : 'Leer entrada.txt',
            2 : 'Modelo mátematico 1: ',
            3 : 'Modelo mátematico 2: ',
            4 : 'Modelo metaheurístico 1: ',
            5 : 'Modelo metaheurístico 2: ',
        }

    def print_welcome(self):
        print(
        """\n
        Bienvenido!
        autores: \n
        Benjamín Brandt\n
        Nicolás Netz \n
        """)

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
    
    def modelo1(self):
        # Preguntar cuantas instancias quiere resolver si una o las 50.
        pass
      

        

if __name__ == "__main__":
    mi_menu = my_menu()
    mi_menu.execute()


#     El programa principal debe contener un menú con las cuatro opciones (dos algoritmos y dos modelos), para
# ser ejecutado con una o las 50 instancias y 10 veces con semillas independientes.