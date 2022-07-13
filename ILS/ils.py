# -*- coding: utf-8 -*-
import tsplib95
import matplotlib.pyplot as plt
import random
import time
import sys
import numpy as np
from visualizar import animacion

Infinity = 9999999
dist = []
class Instancia:
    def __init__(self, graficar_ruta, instance):
        self.graficar_ruta = graficar_ruta
        self.grafico = graficar_ruta
        self.coord_x = []
        self.coord_y = []
        self.problem = tsplib95.load(instance)
        self.info = self.problem.as_keyword_dict()
        self.n = len(self.problem.get_graph())
        if self.verificar_graficar(): # se puede graficar la ruta
            for i in range(1, self.n + 1):
                x, y = self.info['NODE_COORD_SECTION'][i]
                self.coord_x.append(x)
                self.coord_y.append(y)
        else:
            self.graficar_ruta = False

    def verificar_graficar(self):
        verificar = self.info['EDGE_WEIGHT_TYPE']
        if verificar == 'EUC_2D':
            return True;
        elif verificar == 'GEO':
            return True;
        elif verificar == 'ATT':
            return True;
        else:
            print("No se puede graficar")
            False

    def generarMatriz(self):
        inicio = list(self.problem.get_nodes())[0]
        global dist
        dist = [[Infinity for i in range(self.n)] for k in range(self.n)]
        if inicio == 0:
            for i in range(self.n):
                for j in range(self.n):
                    if i != j:
                        u = i, j
                        dist[i][j] = self.problem.get_weight(*u)
        else:
            for i in range(self.n):
                for j in range(self.n):
                    if i != j:
                        u = i + 1, j + 1
                        dist[i][j] = self.problem.get_weight(*u)

# distancia entre la ciudad i y j
def distancia(i, j):
    return dist[i][j]

# Costo de la ruta
def costoTotal(ciudad):
    suma = 0
    i = 0
    while i < len(ciudad) - 1:
        suma += distancia(ciudad[i], ciudad[i + 1])
        i += 1
    suma += distancia(ciudad[-1], ciudad[0])
    return suma

# heurística del vecino más cercano
def vecinoMasCercano(n, desde):
    actual = desde
    ciudad = []
    ciudad.append(desde)
    seleccionada = [False] * n
    seleccionada[actual] = True

    while len(ciudad) < n:
        min = Infinity
        for candidata in range(n):
            if seleccionada[candidata] == False and candidata != actual:
                costo = distancia(actual, candidata)
                if costo < min:
                    min = costo
                    siguiente = candidata

        ciudad.append(siguiente)
        seleccionada[siguiente] = True
        actual = siguiente

    return ciudad

# Búsqueda local 2-opt
def DosOpt(ciudad):
    n = len(ciudad)
    flag = True
    contar = 0
    for i in range(n - 2):
        for j in range(i + 1, n - 1):
            nuevoCosto = distancia(ciudad[i], ciudad[j]) + distancia(ciudad[i + 1], ciudad[j + 1]) - distancia(ciudad[i], ciudad[i + 1]) - distancia(ciudad[j], ciudad[j + 1])
            if nuevoCosto < 0:
                min_i, min_j = i, j
                contar += 1
                # if contar > 0:
                #     ciudad[min_i + 1 : min_j + 1] = ciudad[min_i + 1 : min_j + 1][::-1]

                if contar == 1: # terminar a la primera mejora
                    flag = False

        if flag == False:
            break

    if contar > 0:
        ciudad[min_i + 1 : min_j + 1] = ciudad[min_i + 1 : min_j + 1][::-1]

# perturbación: se escogen dos ciudades aleatorias y las intercambia
def perturbation1(ciudad):
    i = 0
    j = 0
    n = len(ciudad)
    while i == j:
        i = random.randint(0, n - 1)
        j = random.randint(0, n - 1)
    # intercambio
    temp = ciudad[i]
    ciudad[i] = ciudad[j]
    ciudad[j] = temp

# perturbación 2: dos puntos aleatorios e invierte las ciudades entremedio
def perturbation2(ciudad):
    i = 0
    j = 0
    n = len(ciudad)
    while i >= j:
        i = random.randint(0, n - 1)
        j = random.randint(0, n - 1)
    ciudad[i : j] = ciudad[i : j][::-1]

# perturbación: se escoge una ciudad aleatoria y se intercambia con la ciudad siguiente en la ruta
def perturbation3(ciudad):
    j = 0
    n = len(ciudad)
    i = random.randint(0, n - 1)

    if i == n - 1:
         j = 0
    else:
        j = i + 1
    # intercambio
    temp = ciudad[i]
    ciudad[i] = ciudad[j]
    ciudad[j] = temp

# perturbación: completamente aleatoria la ruta
def perturbation4(ciudad):
    random.shuffle(ciudad)

def shaking(ciudad, k):
    if k == 0:
        perturbation1(ciudad)
    elif k == 1:
        perturbation2(ciudad)
    elif k == 2:
        perturbation3(ciudad)
    elif k == 3:
        perturbation4(ciudad)
    else:
        pass


    # Iterated Local Search
def ILS(ins, semilla, algoritmo):
    print("ILS")
    n = ins.n
    random.seed(semilla)
    inicioTiempo = time.time()
    # Rendimiento entre una lista y Numpy
    # Solución inicial
    ciudad_inicial = random.randint(0, n - 1)
    s = vecinoMasCercano(n, ciudad_inicial)
    #s = np.array(vecinoMasCercano(n, ciudad_inicial))
    DosOpt(s)

    s_mejor = s.copy()
    costoMejor = costoTotal(s_mejor)
    lista_soluciones = []
    lista_costos = []
    lista_costosMejores = []
    lista_costos.append(costoMejor)
    lista_costosMejores.append(costoMejor)
    lista_soluciones.append(s_mejor)
    print("inicial %d" % costoMejor)
    iterMax = 1500
    for iter in range(iterMax):
        # Perturbación
        perturbation3(s)

        # Búsqueda local
        DosOpt(s)
        costo_candidato = costoTotal(s)
        # Actualizar mejor solución
        if costoMejor > costo_candidato:
            s_mejor = s.copy()
            costoMejor = costo_candidato
            print("%d\t%d" % (iter, costoMejor))

        lista_costos.append(costo_candidato)
        lista_costosMejores.append(costoMejor)
        lista_soluciones.append(s)
        # print(costo_candidato)
        # criterio de aceptación de la solución actual
        if abs(costoMejor - costo_candidato) / costoMejor > 0.05:
            s = s_mejor.copy()

    finTiempo = time.time()
    tiempo = finTiempo - inicioTiempo
    print("Costo  : %d" % costoMejor)
    print("Tiempo : %f" % tiempo)
    print(s_mejor)
    # Graficar rutas y animación
    if ins.graficar_ruta:
        lista_soluciones.pop()
        lista_soluciones.append(s_mejor)
        lista_costos.pop()
        lista_costos.append(costoMejor)
        ver = animacion(lista_soluciones, ins.coord_x, ins.coord_y, lista_costos)
        ver.animacionRutas()
    if ins.grafico:
        graficar_soluciones(lista_costosMejores, algoritmo)

# Variable Neighborhood Search
def VNS(ins, semilla, algoritmo):
    print("VNS")
    n = ins.n
    random.seed(semilla)
    inicioTiempo = time.time()
    # Rendimiento entre una lista y Numpy
    # Solución inicial
    ciudad_inicial = random.randint(0, n - 1)
    s = vecinoMasCercano(n, ciudad_inicial)
    #s = np.array(vecinoMasCercano(n, ciudad_inicial))
    DosOpt(s)

    s_mejor = s.copy()
    costoMejor = costoTotal(s_mejor)
    lista_soluciones = []
    lista_costos = []
    lista_costosMejores = []
    lista_costos.append(costoMejor)
    lista_costosMejores.append(costoMejor)
    lista_soluciones.append(s_mejor)
    print("inicial %d" % costoMejor)
    iterMax = 1500
    Kmax = 5
    for iter in range(iterMax):
        s_vecindario = s.copy()
        for k in range(Kmax):
            # Agitación (Shake)
            shaking(s_vecindario, k)
            # Búsqueda local
            DosOpt(s_vecindario)
            costo_candidato = costoTotal(s_vecindario)
            # Actualizar mejor solución
            if costoMejor > costo_candidato:
                s = s_mejor = s_vecindario.copy()
                costoMejor = costo_candidato
                print("%d\t%d\t%d" % (iter, k, costoMejor))
                k = k - 1
                # break

        lista_costos.append(costo_candidato)
        lista_costosMejores.append(costoMejor)
        lista_soluciones.append(s)

    finTiempo = time.time()
    tiempo = finTiempo - inicioTiempo
    print("Costo  : %d" % costoMejor)
    print("Tiempo : %f" % tiempo)
    print(s_mejor)
    # Graficar rutas y animación
    if ins.graficar_ruta:
        lista_soluciones.append(s_mejor)
        lista_costos.append(costoMejor)
        ver = animacion(lista_soluciones, ins.coord_x, ins.coord_y, lista_costos)
        ver.animacionRutas()
    if ins.grafico:
        graficar_soluciones(lista_costosMejores, algoritmo)

# graficar soluciones, iteraciones vs costo
def graficar_soluciones(soluciones, algoritmo):
    plt.plot([i for i in range(len(soluciones))], soluciones)
    plt.ylabel("Costo")
    plt.xlabel("Iteraciones")
    plt.title("Iteraciones vs Costo - TSP")
    plt.suptitle("Variable Neighborhood Search (VNS)" if algoritmo else "Iterated Local Search (ILS)")
    plt.xlim((0, len(soluciones)))
    plt.show()

def main():
    if len(sys.argv) < 5:
        print("Uso: python3 ils.py grafica[No(0), Si(1)] nombreInstancia semilla algoritmo")
        return
    dot = int(sys.argv[1]) # 0 no graficar; 1 graficar
    instance = sys.argv[2] # ruta/nombre instancias
    semilla = int(sys.argv[3]) # semilla aleatoria
    algoritmo = int(sys.argv[4]) # ILS 0; 1 VNS
    ins = Instancia(dot, instance)
    ins.generarMatriz()

    if algoritmo:
        VNS(ins, semilla, algoritmo)
    else:
        ILS(ins, semilla, algoritmo)

if __name__ == "__main__":
    main()
