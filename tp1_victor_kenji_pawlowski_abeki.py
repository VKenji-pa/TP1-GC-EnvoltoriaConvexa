# -*- coding: utf-8 -*-
"""TP1 - Victor Kenji Pawlowski Abeki.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1oAAXopfW7MeV4dyvllsvuXAdw1UCAUnh

# Trabalho Pratico 1 - Algoritmos II

**Victor Kenji Pawlowski Abeki - 2020007090**

##Apresentação

Este artigo documenta o processo de criação de uma implementação em Python para criação de um algoritmo para criar modelos de classificação em
aprendizado supervisionado. O principal propósito desta atividade é desenvolver um programa capaz de classificar novos dados em uma das duas classes disponíveis, com base em um conjunto de dados que contenha 2 colunas de atributos e 1 coluna de classe. Para isso utilizaremos algoritmos de geometria computacional ensinados na disciplina

##Introdução

Para o âmbito do trabalho, iremos utilizar do Problema da envoltória convexa.

O problema da envoltória convexa envolve a busca pelo menor polígono convexo que pode conter um conjunto de pontos dados. A solução desse problema nos fornece os vértices que constituem o polígono que abrange todos os pontos.

Quando aplicado a um cenário de classificação utilizando aprendizado de máquina, calcularemos a envoltória convexa para cada uma das classes, a fim de criar modelos lineares e avaliar a separabilidade dos dados.
"""

!pip install bintrees

import numpy as np
import matplotlib.pyplot as plt
import functools as ft
import pandas as pd
import os
import random
from functools import cmp_to_key
from bintrees import RBTree

from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix

plt.rcParams["figure.figsize"] = [8.00, 6.00]
plt.rcParams["figure.autolayout"] = True

"""##Modelagem Computacional do Problema

Nessa seção, a modelagem computacional do problema será apresentada e explicada, dando ênfase para o algoritmo utilizado, as estruturas de dados e a construção da implementação.

##Definição do ponto

Classe que representa um ponto em envoltórias convexas. Temos $X$ representando a coordenada x e $Y$ representando a coordenada y. E teremos a definição de $p0$ que é o ponto base.
"""

class point:
  def __init__(self, x, y):
    self.x = x
    self.y = y
    self.sId = None
    self.isSegStartPoint = False

p0 = point(0,0)

"""## Função de Angulação

Foi definida uma função que calcula o ângulo entre três pontos. Essa função recebe três pontos (p0, p1 e p2) e retorna uma string que representa a angulação ou orientação dos segmentos p0-p1 e p0-p2. Se a angulação for "esquerda," correspondente a 1, isso indica que os três pontos estão dispostos em sentido anti-horário. Se a angulação for "direita," representada por -1, isso significa que os três pontos estão dispostos em sentido horário. Se a angulação for "collinear," que é igual a 0, isso indica que os três pontos estão colineares.
"""

p0 = point(0,0)

def angulacao(a, b, c):
  hip = ((b.y - a.y) * (c.x - b.x) - (b.x - a.x) * (c.y - b.y))
  if hip == 0:
    return 0      #colinear
  elif hip > 0:
    return -1     #pra direita
  else:
    return 1      #pra esquerda

"""## Distância entre pontos e o ponto médio da reta

Função para calcular distância entre dado dois pontos e Função para retornar o ponto médio de uma reta.
"""

def distancia(a, b):
  return np.sqrt(pow((b.x - a.x), 2) + pow((b.y - a.y), 2))

def pontoMedio(a, b):
  return point(((a.x + b.x)/2).round(3), ((a.y + b.y)/2).round(3))

"""## Equação geral da reta

O cálculo de equação geral da reta é necessário para o classificador e assim, novos pontos receberão os seus respectivos rótulos com base nesta reta. Para cáculo da reta, é necessário o declive de reta, no caso, representado por slope.
"""

#declive da reta
def slope(dx, dy):
    return (dy / dx) if dx else 0

#equacao geral da reta
def equacaoReta(a, b, c):
  decliveReta = slope(b.x - a.x, b.y - a.y)
  y = c.y - decliveReta * c.x
  if y < 0:
      y = -y
      sign = '-'
  else:
      sign = '+'
  return 'y = {}x {} {}'.format(round(decliveReta,3), sign, round(y,3))

"""## Ordenação das classes

Para a utilização do algoritmo de Varredura de Graham é necessário a ordenação de suas classes com base da distância entre $p0$ e $pn$, isto é, ordenamos priorizando pontos com as menores coordenadas y, desempatando pelo x.
"""

def reordena(b, c):
  ang = angulacao(p0, b, c)
  if ang == 0:
    if distancia(p0, c) >= distancia(p0, b):
      return -1
    else:
      return 1
  else:
    if ang == 1:
      return -1
    else:
      return 1

"""## Varredura de Graham

A computação da envoltória convexa de um conjunto de pontos no plano é um problema bastante estudado em geometria computacional. No caso, para a computação da envoltória deste problema, será utilizado o algoritmo de Varredura de Graham. Este algoritmo resultará no envoltório convexo mínimo.

O primeiro passo deste algoritmo é encontrar o ponto com a menor coordenada $y$. Em caso de um empate, o ponto com menor coordenada $x$ deve servir como critério de desempate. Chamaremos este ponto de $pIni$. Este passo é da ordem $O (n)$, onde $n$ é o número de pontos em questão.

Depois, o conjunto de pontos do $DF$ deve ser ordenado em ordem crescente do ângulo que ele com o ponto $p0$ formam com o eixo X. O algoritmo procede considerando cada um dos pontos ordenado em sequência e processa os vértices no sentido anti-horário. Para cada ponto $pi$, é determinado, se ao deslocar dos dois pontos anteriores para este ponto se forma uma mudança de direção para a esquerda em $pi$ quando seguimos pelo caminho $pi-1$ --- $pi$ --- $pi+1$, então $pi+1$ é adicionado a envoltória. Caso haja uma mudança para a direita no percurso acima, então $pi$ deve ser um vértice interno, e $pi$ é retirado da envoltória, e repete-se o teste para $pi-2$ --- $pi-1$ --- $pi+1$ até que a condição seja satisfeita.

Assim que todos os vértices forem processados, ou seja, $pi$ = $p0$, o algoritmo retorna a envoltória. A complexidade deste algoritmo é $O(n log n)$, determinada pela ordenação dos pontos.
"""

def envoltoria(pontos, tam):
  pIni = pontos[0]
  pontos = sorted(pontos, key=ft.cmp_to_key(reordena))

  ncolin = 1
  for i in range(1, tam):
    while((i < tam-1) and (angulacao(pIni, pontos[i], pontos[i+1]) == 0)):
      i+=1
    pontos[ncolin] = pontos[i]
    ncolin+=1

  if ncolin < 3:
    print("Nao eh possivel fazer a envoltoria!")
    return ['nolist']

  Pilha = []
  Pilha.append(pontos[0])
  Pilha.append(pontos[1])
  Pilha.append(pontos[2])

  for i in range(3, ncolin):
    while((len(Pilha) > 1)) and (angulacao(Pilha[-2], Pilha[-1], pontos[i]) != 1):
      Pilha.pop()

    Pilha.append(pontos[i])

  if(len(Pilha) < 3):
    print("Nao eh possivel fazer a envoltoria!")
    return ['nolist']

  return Pilha

"""## Verificação de interseção

A verificação de interseção entre dois pontos e dois segmentos.
"""

#função para verificar se um ponto intercepta um segmento que eh colinear com ele
def verificaInterceptaColin(p1, q1, r):
  if ((r.x <= max(p1.x, q1.x)) and (r.y <= max(p1.y, q1.y)) and (r.x >= min(p1.x, q1.x)) and (r.y >= min(p1.y, q1.y))):
    return True
  else:
    return False

#funçao para verificar se dois segmentos possuem interseção entre eles
def intersecao(p1, q1, p2, q2):
  linha1P2 = angulacao(p1,q1,p2)
  linha1Q2 = angulacao(p1,q1,q2)
  linha2P1 = angulacao(p2,q2,p1)
  linha2Q1 = angulacao(p2,q2,q1)

  if((linha1P2 != linha1Q2) and (linha2P1 != linha2Q1)):
    return True
  elif((linha1P2 == 0) and (verificaInterceptaColin(p1, q1, p2))):
    return True
  elif((linha1Q2 == 0) and (verificaInterceptaColin(p1, q1, q2))):
    return True
  elif((linha2P1 == 0) and (verificaInterceptaColin(p2, q2, p1))):
    return True
  elif((linha2Q1 == 0) and (verificaInterceptaColin(p2, q2, q1))):
    return True
  else:
    return False

"""##Problema de identificar interseções

Para determinar a linear independência das envoltórias, será empregado o problema de verificar se há interseção entre dois segmentos em conjuntos diferentes. Se houver interseção entre segmentos pertencentes a envoltórias distintas, isso indicará que as envoltórias não são linearmente separáveis.

## Varredura Linear:

Vamos utilizar a técnica de varredura linear (sweeping) para abordar o problema. Estabelecemos uma ordem nos segmentos, baseada na coordenada y de suas interseções com a linha de varredura. Dois segmentos são considerados comparáveis se a linha de varredura intercepta ambos os segmentos e eles são vizinhos, ou seja, estão imediatamente acima ou abaixo um do outro, sem outros segmentos intermediários.

Para realizar essas comparações, utilizamos uma árvore binária balanceada, no caso uma árvore rubro-negra. Isso nos permite realizar operações de inserção, remoção, sucessor e antecessor imediato em tempo O(log n). A relação entre os segmentos é dinâmica, à medida que eventos de inserção ou remoção ocorrem, a linha de varredura avança através dos segmentos, e devemos executar essas operações na árvore.

Quando identificamos dois segmentos consecutivos, verificamos através de primitivas geométricas se eles se interceptam. Se a resposta for positiva, isso indica que os dados não são linearmente separáveis. Caso contrário, continuamos com o algoritmo. Se avaliarmos todos os elementos e não encontrarmos nenhuma interseção, concluímos que os dados são linearmente separáveis.

O custo total do algoritmo implementado é O(n log n) devido à ordenação realizada durante o pré-processamento. Esse é um custo eficiente para lidar com a interseção de segmentos em conjuntos de dados de tamanho razoável.

## Verificação de sobreposição

Função responsável pela verificação de sobreposição entre duas envoltórias, devido a caso sejam sobrepostas, não será possível a classificação de novos pontos e seus determinados rótulos, nem a geração de métricas.
"""

def sobrepoeEnv(env1, env2, iniC1, iniC2, maxY):
  separados = True
  for i in range(len(env1)-1):
    for j in range(len(env2)-1):
      if (intersecao(env1[i], env1[i+1], env2[j], env2[j+1])):
        separados = False
        break
      if not(separados):
        break

  if(separados):
    if(iniC1.y < iniC2.y):
      inPoint = iniC2
      auxPoint = point(inPoint.x , maxY + 10)
      for i in range(len(env1)-1):
        if (intersecao(env1[i], env1[i+1], inPoint, auxPoint)):
          separados = False
          break
    elif(iniC2.y < iniC1.y):
      inPoint = iniC1
      auxPoint = point(inPoint.x , maxY + 10)
      for i in range(len(env2)-1):
        if (intersecao(env2[i], env2[i+1], inPoint, auxPoint)):
          separados = False
          break

  return separados

"""##Segmento

Classe segmento responsável por definir uma reta composta por dois pontos. Ela será usada na varredura linear para verificar interseções entre segmentos.

"""

class Segment:
    def __init__(self, id, p1, p2, hullClass):
        if p1.x < p2.x:
            self.p1 = point(p1.x, p1.y)
            self.p2 = point(p2.x, p2.y)
        else:
            self.p1 = point(p2.x, p2.y)
            self.p2 = point(p1.x, p1.y)
        self.p1.isSegStartPoint = True
        self.p1.sId = id
        self.p2.sId = id
        self.hullClass = hullClass

    #def __str__(self):
    #    return "(" + str(self.p1.x) + ", " + str(self.p1.y) + ", " + str(self.p1.isSegStartPoint) + ") - (" + str(self.p2.x) + ", " + str(self.p2.y) + ", " + str(self.p2.isSegStartPoint)+ ")" + " " + self.hullClass

  # return if a segment is below another
    def __gt__(self, otSeg):
        if (min(self.p1.x,otSeg.p1.x)==self.p1.x):
            b = self
            a = otSeg
        else:
            b = otSeg
            a = self
        m2 = (b.p2.y - b.p1.y)/(b.p2.x - b.p1.x)
        m1 = (a.p2.y - a.p1.y)/(a.p2.x - a.p1.x)

        x0 = max(self.p1.x,otSeg.p1.x)
        if not (intersecao(self.p1,self.p2, otSeg.p1,otSeg.p2)):
            if (angulacao(b.p1, a.p1, b.p2) == -1): #'right'
                return True if b == self else False
            elif (angulacao(b.p1, a.p1, b.p2) == 1):#'left'):
                return False if b == self else True
        else:
            if b.p1.y - m2 * b.p1.x - a.p1.y + m1 * a.p1.x < (m1-m2) * x0:
                return True if b == self else False
            else:
                return False if b == self else True

def printSeg(segments):
    print()
    for seg in segments:
        print(seg)

def findSeg(convexHull, hullClass):
    segments = []
    for i in range(len(convexHull) - 1):
        point1 = convexHull[i]
        point2 = convexHull[i + 1]
        seg = Segment(i, point1, point2, hullClass)
        segments.append(seg)
    point1 = convexHull[-1]
    point2 = convexHull[0]
    sId = len(convexHull) - 1
    segments.append(Segment(sId, point1, point2, hullClass))

    return segments

"""##Funções para segmento

Foram criadas funções para ordenar, priorizando pontos à esquerda, e encontrar os pontos extremos que compõem cada segmento.

Ademais, com o objetivo de facilitar a procura, foram definidos identificadores e foram aplicadas veriações nos pontos, para evitar segmentos verticais ou com pontos iguais.
"""

def findSegEndPts(segments):
    endpt = []
    for seg in segments:
        lPoint = seg.p1
        rPoint = seg.p2

        endpt.append(lPoint)
        endpt.append(rPoint)
    return endpt

def sortEndPts(endpoints):
    def compareEndPts(p1, p2):
        if p1.x < p2.x:
            return -1
        elif p1.x > p2.x:
            return 1
        else:
            if p1.isSegStartPoint and not p2.isSegStartPoint:
                return -1
            elif not p1.isSegStartPoint and p2.isSegStartPoint:
                return 1
            else:
                if p1.y < p2.y:
                    return -1
                elif p1.y > p2.y:
                    return 1
                else:
                    return 0
    sortedEndPts = sorted(endpoints, key = cmp_to_key(compareEndPts))
    return sortedEndPts

def adjustBsegId(segmentsB, segmentsA):
    for seg in segmentsB:
        seg.p1.sId += len(segmentsA)
        seg.p2.sId += len(segmentsA)

def perturbateSeg(segments):
    for seg in segments:
        seg.p1.x += random.random() * 0.000001
        seg.p2.x += random.random() * 0.000001
    return segments

"""##Varredura Linear

Assim, estabelecemos a função para avaliar a presença de interseções entre segmentos pertencentes a duas envoltórias distintas. Para alcançar esse objetivo, aplicamos um algoritmo originalmente destinado a identificar interseções entre segmentos dentro de um conjunto. Fizemos adaptações, acrescentando rótulos aos segmentos para indicar a qual envoltória eles pertencem. Se dois segmentos eram da mesma envoltória, a interseção era desconsiderada. No entanto, se pertencessem a envoltórias diferentes, a função identificava a existência de uma interseção.
"""

def varreduraIntersecao(hullClassA, hullClassB):
    tree = RBTree()
    segHullClassA = findSeg(hullClassA, "A")
    segHullClassB = findSeg(hullClassB, "B")
    adjustBsegId(segHullClassB, segHullClassA)
    allSegments = perturbateSeg(segHullClassA + segHullClassB)
    allEndpoints = findSegEndPts(allSegments)
    sortedEndpoints = sortEndPts(allEndpoints)

    for endpoint in sortedEndpoints:
        if endpoint.isSegStartPoint:
            seg = allSegments[endpoint.sId]
            tree.insert(seg, endpoint.sId)
            if (tree.min_key() != seg):
                segmentBelow = tree.prev_key(seg)
                if (seg.hullClass != segmentBelow.hullClass and intersecao(seg.p1, seg.p2, segmentBelow.p1, segmentBelow.p2)):
                    return True
            if (tree.max_key() != seg):
                segmentAbove = tree.succ_key(seg)
                if (seg.hullClass != segmentAbove.hullClass and intersecao(seg.p1, seg.p2, segmentAbove.p1, segmentAbove.p2)):
                    return True
        if (not endpoint.isSegStartPoint) and len(tree) > 1:
            seg = allSegments[endpoint.sId]
            if (tree.min_key() != seg and tree.max_key() != seg):
                segmentBelow = tree.prev_key(seg)
                #if (tree.max_key() != seg):
                segmentAbove = tree.succ_key(seg)
                if (segmentBelow.hullClass != segmentAbove.hullClass and intersecao(segmentBelow.p1, segmentBelow.p2, segmentAbove.p1, segmentAbove.p2)):
                    return True
            tree.discard(seg)
    return False

"""## Segmento Mínimo

Função para definir os dois pontos que geram o segmento mínimo entre as duas envoltórias.
"""

def segMin(ec1, ec2):
  c1min = ec1[0]
  c2min = ec2[0]
  minDist = distancia(c1min, c2min)
  for i in range(len(ec1)):
    for j in range(len(ec2)):
      d = distancia(ec1[i], ec2[j])
      if(d < minDist):
        minDist = d
        c1min = ec1[i]
        c2min = ec2[j]

  return c1min, c2min

"""## Plot de Envoltória Convexa

Função para plotagem de envoltória convexa da classe 1 e classe 2 de um determinado $DF$. E caso sejam linearmente separável, a plotagem da linha e do ponto médio da distância mínima entre as duas classes, e a reta perpendicular a ela.
"""

def plotHull(c1, env1, c2, env2, p1min, p2min, aX, aY, pSlope, segSlope, separados):
  x_1,y_1 = zip(*[(i.x,i.y) for i in c1])
  x_envo1,y_envo1 = zip(*[(i.x,i.y) for i in env1])
  x_2,y_2 = zip(*[(i.x,i.y) for i in c2])
  x_envo2,y_envo2 = zip(*[(i.x,i.y) for i in env2])

  pMedio = pontoMedio(p1min, p2min)

  if(segSlope != 0):
    perpY = (pMedio.y - pSlope * pMedio.x)
    perpLineX = [aX[0], aX[1]]
    perpLineY = [pSlope * perpLineX[0] + perpY, pSlope * perpLineX[1] + perpY]

    equacaoPerp = equacaoReta(point(perpLineX[0], perpLineY[0]), point(perpLineX[1], perpLineY[1]), pMedio)
  else:
    perpLineX = [pMedio.x, pMedio.x]
    perpLineY = [pMedio.y - aY[1], pMedio.y + aY[1]]
    equacaoPerp = "x = {}".format(pMedio.x.round(3))

  plt.axis('equal')
  plt.xlim(aX)
  plt.ylim(aY)
  plt.plot(x_1,y_1, "d", color='blue')
  plt.plot(x_2,y_2,"x", color='orange')
  plt.plot(x_envo1, y_envo1, '-',color='blue', label="Classe 1")
  plt.plot(x_envo2, y_envo2, '-', color='orange', label="Classe 2")

  if(separados):
    plt.plot([p1min.x, p2min.x], [p1min.y, p2min.y], color='black')
    plt.plot(perpLineX, perpLineY, '--', color='red', label=equacaoPerp)
    plt.plot(pMedio.x, pMedio.y, 'o-', color='black', label=equacaoReta(p1min, p2min, pMedio))

  plt.legend()
  plt.grid()
  plt.show()

"""## Métricas

As métricas são geradas a partir da função $metricas$ e é utilizado $Scikit-Learn$ e reta perpendicular para classificação dos novos pontos (os 30% restantes) em rótulos. Utilizamos da Scikit, a função $classification\_report$ e gera $precision, recall, f1-score, support$.
"""

def metricas(avalx30, avaly30, y_aval, escolha, perpSlope, segSlope, p1min, p2min, p0c1, p0c2, imprime):
  pMedio = pontoMedio(p1min, p2min)
  if(segSlope != 0):
    plusY = (pMedio.y - perpSlope * pMedio.x)
    pAux = point(pMedio.x + 5, perpSlope*(pMedio.x + 5) + plusY)
  else:
    pAux = point(pMedio.x, pMedio.y + 5)

  if(angulacao(pMedio, pAux, p0c1) == 1):
    posC1 = -1
    posC2 = 1
  else:
    posC1 = 1
    posC2 = -1

  listaClassificatoria = []

  for i in range(len(avalx30)):
    if(angulacao(pMedio, pAux, point(avalx30[i], avaly30[i])) == 1):
      if(posC1 == -1):
        listaClassificatoria.append(escolha[0])
      else:
        listaClassificatoria.append(escolha[1])
    elif(angulacao(pMedio, pAux, point(avalx30[i], avaly30[i])) == -1):
      if(posC1 == 1):
        listaClassificatoria.append(escolha[0])
      else:
        listaClassificatoria.append(escolha[1])
    else:
      listaClassificatoria.append("incorreto")

  x1 = []; y1 = []
  x2 = []; y2 = []
  for i in range(len(listaClassificatoria)):
    if(listaClassificatoria[i] == escolha[0]):
      x1.append(avalx30[i])
      y1.append(avaly30[i])
    else:
      x2.append(avalx30[i])
      y2.append(avaly30[i])

  print(classification_report(y_aval, listaClassificatoria))

  if(imprime):
    print("\n[Grafico 30%]:")

    if(segSlope != 0.000):
      linhaX = [avalx30.min()-1, avalx30.max()+1]
      linhaY = [perpSlope*linhaX[0] + plusY, perpSlope*linhaX[1] + plusY]
      equacaoPerp = equacaoReta(point(linhaX[0], linhaY[0]), point(linhaX[1], linhaY[1]), pMedio)
    else:
      linhaX = [pMedio.x, pMedio.x]
      linhaY = [avaly30.min(), avaly30.max()]
      equacaoPerp = "x = {}".format(pMedio.x.round(3))

    print("\nClasse 1 30%:")
    for i in range(len(x1)):
      print('[{}, {}]'.format(x1[i], y1[i]), end = ' ')
    print("\nClasse 2 30%:")
    for i in range(len(x2)):
      print('[{}, {}]'.format(x2[i], y2[i]), end = ' ')
    plt.axis('equal')
    plt.xlim(avalx30.min() - 1, avalx30.max() + 1)
    plt.ylim(avaly30.min() - 1 , avaly30.max() + 1)
    plt.scatter(x1, y1, label="Classe 1 (30%)", color='blue')
    plt.scatter(x2, y2, label="Classe 2 (30%)", color='orange')
    plt.plot(linhaX, linhaY,'--', color='red', label=equacaoPerp)
    plt.legend()
    plt.grid()
    plt.show()

"""## Categorização

Categorização de atributos dos $datasets$, transformando strings, como "ruim", "regular", "bom e "ótimo" em valores categóricos como 1, 2, 3, 4.
"""

def objToCateg(data):
  for i in (data.columns):
    if(data[i].dtypes == 'object'):
      data[i] = data[i].astype('category').cat.codes

  return data

"""## Análise

Função responsável por instanciar a análise do $dataset$, sendo escolhido duas classes aleatórias da coluna $Class$, previamente definida, e duas colunas aleatórias que contém os pontos. A partir da escolha das classes e os pontos selecionados, utilizamos as funções acima já explicadas. Nesta classe é chamada a função que implementa a Varredura de Graham e caso esta envoltória retornada pelo algoritmo seja linearmente separável, é usada a função de métricas explicada acima.
"""

def analise(dsName):
  df = pd.read_csv('csv/' + dsName, sep=';', header=0)

  lista = df['Class'].unique()
  escolhidos = random.sample(range(0, len(lista)), 2)
  escolhaClass = []
  escolhaClass.append(lista[escolhidos[0]])
  escolhaClass.append(lista[escolhidos[1]])
  escolhaClass.sort()

  df = df[df['Class'].isin(escolhaClass)]

  n = df.shape[1] - 1
  y = df.iloc[:,n]
  X = df.iloc[:,:n]

  X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.70)

  X_test = objToCateg(X_test)
  X_train = objToCateg(X_train)

  difs = random.sample(range(len(X_test.columns)), 2)

  cModelox = []; cModeloy = []; eixoX = []; eixoY = []
  cModelox = X_test[X_test.columns[difs[0]]]
  cModeloy = X_test[X_test.columns[difs[1]]]

  eixoX = [cModelox.min() - 1, cModelox.max() + 1]
  eixoY = [cModeloy.min() - 1, cModeloy.max() + 1]

  cAvaliax = []; cAvaliay = []
  cAvaliax = X_train[X_train.columns[difs[0]]]
  cAvaliay = X_train[X_train.columns[difs[1]]]

  cModelox = cModelox.reset_index(drop=True)
  cModeloy = cModeloy.reset_index(drop=True)
  cAvaliax = cAvaliax.reset_index(drop=True)
  cAvaliay = cAvaliay.reset_index(drop=True)

  y_test = y_test.reset_index(drop=True)
  y_train = y_train.reset_index(drop=True)

  class1 = []
  class2 = []

  #Escolhento atributos para analise
  print("\nAtributos: ", X_train.columns.values)
  print("\nAtributos utilizados como X e Y: ", X_train.columns[difs[0]], "," , X_train.columns[difs[1]], "\n")

  #criação das duas classes e atribuindo pontos a elas
  for i in range(len(y_test)):
    p = point(cModelox[i].round(3), cModeloy[i].round(3))
    if(y_test[i] == escolhaClass[0]):
      class1.append(p)
    elif(y_test[i] == escolhaClass[1]):
      class2.append(p)

  class1 = sorted(class1 , key=lambda cord: (cord.y, cord.x))
  class2 = sorted(class2 , key=lambda cord: (cord.y, cord.x))

  global p0

  if(len(class1) <3 or len(class2) < 3):
    print("\nNao eh possivel fazer a envoltoria!")
    return

  p0 = class1[0]
  pin1 = class1[0]
  enC1 = list()
  enC1 = envoltoria(class1, len(class1))

  if(enC1[0] == 'nolist'):
    return

  p0 = class2[0]
  pin2 = class2[0]
  enC2 = list()
  enC2 = envoltoria(class2, len(class2))


  if(enC2[0] == 'nolist'):
    return

  print("\nEnvoltoria 1: ")
  for i in range(len(enC1)):
    print('[{}, {}]'.format(enC1[i].x, enC1[i].y), end = ' ')
  print("\nEnvoltoria 2: ")
  for i in range(len(enC2)):
    print('[{}, {}]'.format(enC2[i].x, enC2[i].y), end = ' ')

  (min1, min2) = segMin(enC1, enC2)
  s = slope(min2.x - min1.x, min2.y - min1.y)

  if(s != 0):
    pSlope = (-1)/s
  else:
    pSlope = 0

  separados = (sobrepoeEnv(enC1, enC2, pin1, pin2, cModeloy.max() + 10)) #True - separados, False - Sobrepoem
  varredura = False

  if(varreduraIntersecao(enC1, enC2)):
    varredura = True
  else:
    varredura = False

  if(varredura):
    print("\nAs envoltórias convexas se interceptam, portanto, os conjuntos não são linearmente separáveis.")
  elif(not separados):
    print("\nAs envoltórias convexas se sobrepõem. Dados das classes nao sao linearmente separaveis")
  else:
    print("\nDados das classes sao linearmente separaveis")

  enC1.append(enC1[0])    #inserindo o ponto inicial novamente para fechamento da envoltoria
  enC2.append(enC2[0])    #inserindo o ponto inicial novamente para fechamento da envoltoria

  p0 = point(0,0)
  print("Classes: " + str(escolhaClass[0]) + ", " + str(escolhaClass[1]))
  plotHull(class1, enC1, class2, enC2, min1, min2, eixoX, eixoY, pSlope, s, (not varredura or separados))

  if(separados and not varredura):
    metricas(cAvaliax, cAvaliay, y_train,escolhaClass, pSlope, s, min1, min2, pin1, pin2, True)

"""## Resultados e Métricas

Nesta parte, o objetivo é analisar cada $dataframe$, localizados no diretório local de testes $csv/$ do computador pessoal utilizado, lembrando que este diretório pode ser customizável. Cada dado sera analisado individualmente e serão apresentados os resultados e métricas de avaliação. No caso, de não serem linearmente separáveis, será apresentado somente uma mensagem da impossibilidade do processamento.

Todos os datasets utilizados são do site: https://sci2s.ugr.es/keel/category.php?cat=clas#inicio.

#1 - IRIS PLANTS DATA SET

Disponível em: https://sci2s.ugr.es/keel/dataset.php?cod=18
"""

#dset = []
#dset.append("iris.csv")

print("1. Analise do dataset: iris.csv")
analise("iris.csv")
print("\n")

"""##2 - TEXTURE DATA SET

Disponível em: https://sci2s.ugr.es/keel/dataset.php?cod=72
"""

print("2. Analise do dataset: texture.csv")
analise("texture.csv")
print("\n")

"""##3 - BANANA DATA SET

Disponível em: https://sci2s.ugr.es/keel/dataset.php?cod=182
"""

print("3. Analise do dataset: banana.csv")
analise("banana.csv")
print("\n")

"""##4 - LIBRAS MOVEMENT DATA SET

Disponível em: https://sci2s.ugr.es/keel/dataset.php?cod=165
"""

print("4. Analise do dataset: movement_libras.csv")
analise("movement_libras.csv")
print("\n")

"""##5 - VEHICLES SILHOUETTES DATA SET

Disponível em: https://sci2s.ugr.es/keel/dataset.php?cod=68
"""

print("5. Analise do dataset: vehicle.csv")
analise("vehicle.csv")
print("\n")

"""##6 - RED WINE QUALITY DATA SET

Disponível em: https://sci2s.ugr.es/keel/dataset.php?cod=210
"""

print("6. Analise do dataset: winequality-red.csv")
analise("winequality-red.csv")
print("\n")

"""##7 - PAGE BLOCKS CLASSIFICATION DATA SET

Disponível em: https://sci2s.ugr.es/keel/dataset.php?cod=104
"""

print("7. Analise do dataset: page-blocks.csv")
analise("page-blocks.csv")
print("\n")

"""##8 - SPECTF HEART DATA SET

Disponível em: https://sci2s.ugr.es/keel/dataset.php?cod=185
"""

print("8. Analise do dataset: spectfheart.csv")
analise("spectfheart.csv")
print("\n")

"""##9 - IMAGE SEGMENTTATION DATA SET

Disponível em: https://sci2s.ugr.es/keel/dataset.php?cod=107
"""

print("9. Analise do dataset: segment.csv")
analise("segment.csv")
print("\n")

"""##10 - RINGNORM DATA SET

Disponível em: https://sci2s.ugr.es/keel/dataset.php?cod=106
"""

print("10. Analise do dataset: ring.csv")
analise("ring.csv")
print("\n")

#dir = 'csv/'
#dset = []
#for file in os.listdir(dir):
#    if file.endswith(".csv"):
#      dset.append(file)

#for i in range(len(dset)):
#  print("{}. Analise do dataset: {}".format(i+1, dset[i]))
#  analise(dset[i])
#  print("\n")

"""## Considerações finais

De maneira geral, este trabalho foi extremamente relevante para aprofundar nossa compreensão sobre o funcionamento do algoritmo Varredura de Graham, permitindo-nos estabelecer uma conexão mais próxima e aplicada aos conceitos abordados em sala de aula.

Durante o desenvolvimento deste projeto, pudemos consolidar muitos dos conceitos gerais sobre algoritmos aprendidos na sala de aula, resultando em uma experiência mais enriquecedora e uma compreensão aprofundada da matéria.





"""