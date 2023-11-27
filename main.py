import networkx as nx
import pandas as pd
import numpy as np
import random
from random import sample
from funciones import *
import time
import os


# Extraer datos del archivo csv
data_frame = pd.read_csv("spotify_datos.csv")#, nrows=10)
data_frame = data_frame.drop("Unnamed: 0", axis="columns")
data_frame.head(15)


# Creando grafo tripartito
G = nx.Graph()


# Añadir multiples nodos iniciales
# ===========================================================================
usuarios_iniciales = ["David", "Santiago", "Valeria","Steven","Andres","Carlos","Miguel"]
canciones = list(data_frame["song_title"].values)
artistas = list(data_frame["artist"].values)

G.add_nodes_from(usuarios_iniciales, tripartite="usuarios")
G.add_nodes_from(artistas, tripartite="artistas")
G.add_nodes_from(canciones, tripartite="canciones")


aristas_art_can = [(canciones[i], artistas[i]) for i in range(0, len(canciones))]

G.add_edges_from(aristas_art_can)

# Añadiendo usuarios y preferencias iniciales
#=============================================================================
gustos_art = []
gustos_can = []
for i in usuarios_iniciales:
  for a in range(0,2):
    m = random.choice(artistas)
    for p in gustos_art:
      while True:
        if m in p[1]:
          m = random.choice(artistas)
        else:
          break

    k = (i,m)
    gustos_art.append(k)

  for b in range(0,random.randint(3,6)):
    j = (i,random.choice(canciones))
    gustos_can.append(j)

G.add_edges_from(gustos_art)
G.add_edges_from(gustos_can)



# Añadiendo pesos iniciales
#=========================================================================== 
peso_aristas = {}
for arista in gustos_can:
  peso_aristas[arista] = random.randint(1,10)

nx.set_edge_attributes(G, peso_aristas, name="peso")


#Agregando pesos a las aristas (sumando los pesos de las canciones-ususarios)
pesos_art_can ={}

for arista in aristas_art_can:
  peso_art_usr = 0
  for i in usuarios_iniciales:
    if (i,arista[0]) in gustos_can:
      peso_art_usr = G.edges[(i,arista[0])].get('peso') + peso_art_usr
    else:
      peso_art_usr = 0 + peso_art_usr
  #print("El peso de "+arista[0] +" con "+arista[1]+" es "+str(peso_art_usr))
  pesos_art_can [arista] = peso_art_usr

nx.set_edge_attributes(G, pesos_art_can, name="peso")



#Agregar a usuarios las canciones de sus artistas favoritos

# Añadiendo canciones a usuarios de los artistas favoritos
# ==========================================================================
gst = []
for i in usuarios_iniciales:
  #print(i+"\n")
  for p in obtener_artistas_usuario(G, i):
      if len(obtener_peso_canciones(G,p)) > 1:
        for r in range(0,2):
          d = obtener_peso_canciones(G, p)[r]
          #print("arista: "+p+" -> "+str(d))
          g = (i,d)
          gustos_can.append(j)
      else:
          d = obtener_peso_canciones(G, p)[0]
          #print("arista: "+p+" -> "+str(d))

      if d[0] not in obtener_canciones(G, i):
        g = (i,d[0])
        gst.append(g)
  #print("\n\n")

G.add_edges_from(gst)

#Agregandoles peso
peso_aristas = {}
for arista in gst:
  peso_aristas[arista] = random.randint(1,10)

nx.set_edge_attributes(G, peso_aristas, name="peso")



peso_ant_art=0
for usr in usuarios_iniciales:
  for j in gst:
    if j[0] == usr:
      peso_uc = G.edges[(usr,j[1])].get('peso')
      for i in aristas_art_can:
        if G.has_edge(j[1],i[1]):
          peso_ant_art = G.edges[(j[1], i[1])].get('peso')
          art = i[1]

      G.remove_edge(j[1], art)
      G.add_edge(j[1], art)
      pesos_art_can[(j[1], art)] = peso_ant_art + peso_uc
      nx.set_edge_attributes(G, pesos_art_can, name="peso")


# Interacción con el usuario
# ==================================================================================================
menu = """
Qué quieres hacer?
1. Escuchar música
2. Obtener recomendaciones musicales
3. Salir
"""
gustos1 = []
artt = []
print("Bienvenido al recomendador de musica, desea registrarse(R) o ingresar(I): ")
registro = False
eleccion = input('Ingresa tu elección: ')
bucle = True
while bucle:
  if not registro:
    if eleccion == 'i' or eleccion == 'I':

        ingreso = input ("Digite su nombre: ")
        while ingreso not in usuarios_iniciales:
          ingreso = input ("Su nombre no existe. Escribalo de nuevo. ")
        # G.add_nodes_from(usuarios_iniciales, tripartite="usuarios")
    elif eleccion == 'r' or eleccion == 'R':
        ingreso = input("Ingrese su nombre: ")
        if ingreso not in usuarios_iniciales:
          usuarios_iniciales.append(ingreso)
          G.add_nodes_from(usuarios_iniciales, tripartite="usuarios")
          print ("A continuacion se mostrara una lista de artistas")
          dic_art = {}
          if len(artistas) >= 15:
            for i in range(0, 15):
              att = random.choice(artistas)
              if att not in artt:
                artt.append(att)
                dic_art[i] = att
          else:
            for i in range(0, len(artistas)):
              if artistas[i] not in artt:
                artt.append(artistas[i])
                dic_art[i] = artistas[i]

          print(dic_art)

          eleccion = input ("Digite el número de el o los artistas que le gusta(si es mas de uno, separarlos por comas): ")
          gustos = eleccion.split(",")
          for i in gustos:
            gustos1.append(dic_art[int(i)])

          for i in gustos1:
            if len(gustos1) == 1:
              G.add_edge(ingreso, gustos1[0])
            else:
              G.add_edges_from([(ingreso, gustos1[i]) for i in range(0, len(gustos1))])

          while True:
            if (noesta(artistas, gustos1)):
              gustos.clear()
              gustos1.clear()
              eleccion = input ("Algun artista no exite o esta mal escrito. Por favor vuelva a digitar el o los nombres: ")
              gustos = eleccion.split(",")
              for i in gustos:
                a = i.rstrip()
                b = a.lstrip()
                gustos1.append(b)
              #print(gustos1)
            else:
              break

    else:
        print("Ingrese una opcion valida.")
  print(menu)
  opcion = input("Dijite el número de la opción que quiere realizar: ")

  #########################################
  if opcion == "1":
    canciones_rc = {}
    canciones_rr = []
    print ("A continuacion se mostrara una lista de canciones de su(s) artista(s) favorito(s): ")
    cont = 0
    for i in obtener_artistas_usuario(G, ingreso):
      for j in obtener_peso_canciones(G, i):
        canciones_rr.append(j[0])
        canciones_rc[cont] = j[0]
        cont = cont + 1

    print(canciones_rc)

    eleccion_cn = int(input ("Digite el numero de la cancion que quiera escuchar: "))

    while True:
      if canciones_rc[eleccion_cn] not in canciones_rr:
        eleccion_cn = int(input ("El numero no existe o esta mal escrito. Por favor vuelva a digitar el numero: "))
      else:
        break

  #########################################

    for i in aristas_art_can:
      if G.has_edge(canciones_rc[eleccion_cn],i[1]):
        peso_ant_art = G.edges[(canciones_rc[eleccion_cn], i[1])].get('peso')
        art = i[1]
    G.remove_edge(canciones_rc[eleccion_cn], art)
    G.add_edge(ingreso, canciones_rc[eleccion_cn])
    G.add_edge(canciones_rc[eleccion_cn], art)
    peso_aristas[(ingreso, canciones_rc[eleccion_cn])] = 1
    nx.set_edge_attributes(G, peso_aristas, name="peso")
    pesos_art_can[(canciones_rc[eleccion_cn], art)] = peso_ant_art + 1
    nx.set_edge_attributes(G, pesos_art_can, name="peso")
    print("Reproduciendo... \n\n")
    time.sleep(2)
  #########################################
  elif opcion == "2":
    recomendaciones = recomendar_canciones(G, usuarios_iniciales[-1])
    dic_recomendaciones = {}
    for i, recomendacion in enumerate(recomendaciones):
      dic_recomendaciones[i] = recomendacion

    print(f"Estas son algunas de las canciones que le recomendamos: \n{dic_recomendaciones}")
    opcion = input("Cuál canción desea escuchar?:\nDijite el número de canción\nQ. Si no decea escuchar alguna: ")

    if opcion == "q" or opcion == "Q":
      pass
    elif int(opcion) in dic_recomendaciones.keys():
      for i in aristas_art_can:
        if G.has_edge(dic_recomendaciones[int(opcion)],i[1]):
          peso_ant_art = G.edges[(dic_recomendaciones[int(opcion)], i[1])].get('peso')
          art = i[1]
      G.remove_edge(dic_recomendaciones[int(opcion)], art)
      G.add_edge(ingreso, dic_recomendaciones[int(opcion)])
      G.add_edge(dic_recomendaciones[int(opcion)], art)
      peso_aristas[(ingreso, dic_recomendaciones[int(opcion)])] = 1
      nx.set_edge_attributes(G, peso_aristas, name="peso")
      pesos_art_can[(dic_recomendaciones[int(opcion)], art)] = peso_ant_art + 1
      nx.set_edge_attributes(G, pesos_art_can, name="peso")
      print("Reproduciendo... \n\n")
      time.sleep(2)

  #########################################
  elif opcion == "3":
    bucle = False
  #########################################
  else:
    print("Por favor dijite una opción valida")
    os.system('cls')    
    time.sleep(1)
  os.system('cls')

# Graficar grafo
#===========================================================================
for i in usuarios_iniciales:
  print(f"Al usuario {i} le recomienda: {recomendar_canciones(G, i)}")

for user1 in usuarios_iniciales:
  for user2 in [user for user in usuarios_iniciales if user != user1]:
      print(f"Similitud entre {user1} y {user2} es de: {similitud_jaccard(G, user1, user2)}")
graficar_grafo(G)





