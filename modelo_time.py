ins = Instancia()

class Modelo():
    def __init__(self):
        self.name = "TSPTW-TIME INDEXED"

    def build(self,ins):
        # Modelo
        self.mdl = Model('TSPTW - TIME INDEXED')

        # Variables de decisión
        self.x = self.mdl.binary_var_dict( {(i,j) for i in ins.V for j in ins.V}, name = 'x')
        self.y = self.mdl.binary_var_dict( {(i,j,t) for i in ins.V for j in ins.V for t in ins.W[i]}, name = 'y')
        self.z = self.mdl.binary_var_dict( {(i,t) for i in ins.V for t in ins.W[i]}, name = 'z')
        
        # Restricción 1: Funcion Objetivo
        self.mdl.minimize(self.mdl.sum(self.x[(i,j)]*ins.c[(i,j)] for i,j in ins.arcos))

        # Restricción 2: La ruta comienza en cada nodo i dentro de la ventana de tiempo
        for i in ins.V:
            self.mdl.add_constraint(self.mdl.sum(self.z[(i,t)] for t in ins.W[i]) == 1 , ctname= 'restriccion2: z_{}'.format(i))

        # Restricción 3: 
        for i in ins.V:
            if i!=ins.q:
                for t in ins.W[i]:
                    self.mdl.add_constraint(self.mdl.sum(self.y[i,j,t] for j in ins.V) == self.z[i,t], ctname= 'restriccion3: z_{}'.format(i))
        # Restriccion 4:
        for i in ins.V:
            if i!=ins.p:
                for t in ins.W[i]:
                    self.mdl.add_constraint(self.mdl.sum(  self.mdl.sum(self.y[k,i,tau] for tau in [tau for tau in ins.W[k] if tau <= ins.a[i] - ins.c[k,i]]) for k in ins.V if k!=i ) == self.z[i,t], ctname= 'restriccion4: z_{}'.format(i))

        # Restriccion 5:
        for i,j in ins.arcos:
            self.mdl.add_constraint(self.mdl.sum(self.y[i,j,t] for t in ins.W[i]) == self.x[i,j], ctname= 'restriccion5: y_{}_{}_{}'.format(i,j,t))

    def solve(self):
        self.solucion = self.mdl.solve(log_output= True)

        print(self.mdl.get_solve_status())
        print(self.solucion)
        self.arcos_solucion = [i for i in ins.arcos if self.x[i].solution_value>0.9]
        print(self.arcos_solucion)



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
        print(camino)

        return(camino)

modelo = Modelo()
modelo.build(ins)
print(modelo.mdl.export_to_string())