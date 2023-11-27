import networkx as nx
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import random
from random import sample
# from os import posix_spawnp


def noesta(listado, buscar): #Saber si algo esta o no en una lista
    for i in buscar:
        if not i in listado:
            return True
    return False

def obtener_canciones(G:nx.classes.graph.Graph, usuario):# Retorna las canciones adyacentes a un nodo usuario o un nodo artista
  return [
    list(G.neighbors(usuario))[i]
    for i in range(len(list(G.neighbors(usuario))))
    if G.nodes.get(list(G.neighbors(usuario))[i])["tripartite"] == "canciones"
  ]


def obtener_vecinos_cancion(G:nx.classes.graph.Graph, cancion): # Retorna los usuarios adyacentes a una canción
  return [
    list(G.neighbors(cancion))[i]
    for i in range(len(list(G.neighbors(cancion))))
    if G.nodes.get(list(G.neighbors(cancion))[i])["tripartite"] == "usuarios"
  ]


def obtener_peso_canciones(G:nx.classes.graph.Graph, usuario:str): # Retorna el peso de las canciones escuchadas por un usuario
  canciones = obtener_canciones(G, usuario)
  lista_peso_canciones = []

  for cancion in canciones:
    for arista in G.edges(data=True):
      if cancion in arista and usuario in arista:
        lista_peso_canciones.append((cancion, arista[2]["peso"]))
  return lista_peso_canciones


def obtener_canciones_mas_escuchadas(G:nx.classes.graph.Graph, usuario:str, cantidad:int=1): # Retorna las canciones más escuchadas por un usuario
  canciones = obtener_canciones(G, usuario)
  canciones_peso = obtener_peso_canciones(G, usuario)
  if len(canciones) == 0:
    return "El usuario no ha escuchado canciones"
  elif len(canciones) <= cantidad:
    return canciones
  elif len(canciones) > cantidad:
    while len(canciones) != cantidad:
      peso_min = 0
      cancion_min = ""
      tupla = None
      for cancion in canciones_peso:
        if int(cancion[1]) > peso_min:
          peso_min = int(cancion[1])
          cancion_min = canciones[0]
          tupla = cancion
      if tupla != None:
        canciones_peso.remove(tupla)
        canciones.remove(cancion_min)
    return canciones


def canciones_comunes_usuarios(G:nx.classes.graph.Graph, usuario1, usuario2): # Hace la intersección entre las canciones de dos usuarios
  canciones1 = obtener_canciones(usuario1)
  canciones2 = obtener_canciones(usuario2)
  return list(filter(lambda x: x in canciones1, canciones2))


def obtener_artista_por_cancion(G: nx.classes.graph.Graph, cancion): # Retorna el artista adyacente a la canción de entrada
    for m, n, w in G.edges(data=True):
      if n == cancion:
        diccionario = G.nodes.get(m)
        if 'artistas' == diccionario['tripartite']:
          return m


def prim(G:nx.classes.graph.Graph, raiz): # Algoritmo de Prim
  aristasGP = list(G.edges(data=True))
  aristasG = list(G.edges)

  verticesT = [raiz]
  aristasT = []
  for i in range(len(aristasGP)):
    e = None
    v = None
    peso= 0
    for arista in aristasGP:
      if (arista[0] in verticesT and arista[1] not in verticesT) and arista[2]["peso"] >= peso:
        e = arista
        v = arista[1]
        peso = arista[2]["peso"]

      elif (arista[0] not in verticesT and arista[1] in verticesT) and arista[2]["peso"] >= peso:
        e = arista
        v = arista[0]
        peso = arista[2]["peso"]
    if e != None:
      aristasGP.remove(e)
      verticesT.append(v)
      aristasT.append(e)
    
  T = G.subgraph(verticesT)
  T2 = nx.Graph(T)
  aristasT2 = list(T2.edges(data=True))
  for arista in aristasT2:
    if arista not in aristasT:
      T2.remove_edges_from([arista])
  return T2


def graficar_grafo(G: nx.classes.graph.Graph): # Pinta el dibujo de un grafo
  # colores para cada tipo de nodo en el grafo bipartito
  tipo_nodo = [
    G.nodes.get(i)["tripartite"]
    for i in G.nodes()
  ]
  colores = {"usuarios": "red", "artistas": "blue", "canciones": "green"}
  colores_nodos = [colores[n] for n in tipo_nodo]


  fig, ax = plt.subplots(figsize=(10, 10))
  pos = nx.spring_layout(G, k=1.8)
  edge_labels = nx.get_edge_attributes(G,'peso')
  nx.draw(
      G,
      pos=pos,
      with_labels=True,
      ax=ax,
      node_size=400,
      node_color = colores_nodos 
      )

  nx.draw_networkx_edge_labels(G, pos, edge_labels)

  ax.set_title("Gráfica ponderada G")
  ax.set_xlim([1.1*x for x in ax.get_xlim()])
  ax.set_ylim([1.1*y for y in ax.get_ylim()])


  plt.text(0.001, 1, "Rojo: usuarios", transform=ax.transAxes, fontsize=11, color='red')
  plt.text(0.001, 0.97, "Verde: canciones", transform=ax.transAxes, fontsize=11, color='green')
  plt.text(0.001, 0.94, "Azul: artistas", transform=ax.transAxes, fontsize=11, color='blue')

  plt.show()

# ========================Algoritmo de Jaccard, que sirve para evaluar la similitud de dos usuarios============================
def similitud_jaccard(G: nx.classes.graph.Graph, nodo1, nodo2):
  canciones1 = obtener_canciones(G, nodo1) # Buscamos las canciones del usuario 1
  canciones2 = obtener_canciones(G, nodo2) # Buscamos las canciones del usuario 2

  # Calculamos la intersección de las canciones que han escuchado los dos usuarios
  intersection = set(canciones1).intersection(canciones2)

  # Calculamos la unión de las canciones que han escuchado los dos usuarios
  union = set(canciones1).union(canciones2)

  # Si la intersección es vacía, entonces los usuarios no son similares.
  if not intersection:
    return 0.0

  # Calculamos la similitud usando el coeficiente de Jaccard.
  return len(intersection) / len(union)




def recomendar_musica_jaccard(G: nx.classes.graph.Graph, usuario:str, lista_usuarios:list): # Recomienda música a un usuario buscando otro usuario con gustos similares a este
  return_canciones = []
  for user in lista_usuarios:
    if user != usuario:
      if similitud_jaccard(G, usuario, user) >= 0.7:
        canciones_usuario = obtener_canciones(G, usuario)
        canciones_user_masEscuchadas = obtener_canciones_mas_escuchadas(G, user, 2)
        return_canciones += set(canciones_user_masEscuchadas).difference(canciones_usuario)
  return return_canciones


def recomendador_musica_por_artistas(G, usuario): #Recomienda canciones en base a los artistas que le gustan al usuario
  # Traemos los artistas de las canciones que más ha escuchado el usuario
  artistas = [obtener_artista_por_cancion(G, cancion) for cancion in obtener_canciones_mas_escuchadas(G, usuario, 3)]
  # Canciones más escuchadas de los artistas que más ha escuchado el usuario
  canciones_a_recomendar = [] # Lista de las canciones que se van a recomendar
  for artista in artistas:
    canciones_a_recomendar += obtener_canciones_mas_escuchadas(G, artista, 3)

  for i in canciones_a_recomendar:
    if i in obtener_canciones(G,usuario):
      canciones_a_recomendar.remove(i)
  return set(canciones_a_recomendar)


def recomendar_canciones(G: nx.classes.graph.Graph, usuario): #Recomendar toda la música posible a un usuario
  # Lista de canciones a recomendar
  canciones = []
  # Obtener lista de usuarios
  usuarios = [user for user in G.nodes if G.nodes.get(user)["tripartite"] == "usuarios" and user != usuario]

  canciones += recomendar_musica_jaccard(G, usuario, usuarios)
  canciones += recomendador_musica_por_artistas(G, usuario)
  return canciones


def obtener_artistas_usuario(G:nx.classes.graph.Graph, usuario):
  return [
    list(G.neighbors(usuario))[i]
    for i in range(len(list(G.neighbors(usuario))))
    if G.nodes.get(list(G.neighbors(usuario))[i])["tripartite"] == "artistas"
  ]
