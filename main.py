import pygame
import tkinter
from tkinter import *
from tkinter.simpledialog import *
from tkinter import messagebox as MessageBox
from tablero import *
from dominio import *
from variable import *
from pygame.locals import *
import queue

GREY=(190, 190, 190)
NEGRO=(100,100, 100)
BLANCO=(255, 255, 255)

MARGEN=5 #ancho del borde entre celdas
MARGEN_INFERIOR=60 #altura del margen inferior entre la cuadrícula y la ventana
TAM=60  #tamaño de la celda
FILS=3# número de filas del crucigrama 5
COLS=3# número de columnas del crucigrama 6

LLENA='*' 
VACIA='-'

#########################################################################
# Detecta si se pulsa el botón de FC
######################################################################### 
def pulsaBotonFC(pos, anchoVentana, altoVentana):
    if pos[0]>=anchoVentana//4-25 and pos[0]<=anchoVentana//4+25 and pos[1]>=altoVentana-45 and pos[1]<=altoVentana-19:
        return True
    else:
        return False
    
######################################################################### 
# Detecta si se pulsa el botón de AC3
######################################################################### 
def pulsaBotonAC3(pos, anchoVentana, altoVentana):
    if pos[0]>=3*(anchoVentana//4)-25 and pos[0]<=3*(anchoVentana//4)+25 and pos[1]>=altoVentana-45 and pos[1]<=altoVentana-19:
        return True
    else:
        return False
    
######################################################################### 
# Detecta si se pulsa el botón de reset
######################################################################### 
def pulsaBotonReset(pos, anchoVentana, altoVentana):
    if pos[0]>=(anchoVentana//2)-25 and pos[0]<=(anchoVentana//2)+25 and pos[1]>=altoVentana-45 and pos[1]<=altoVentana-19:
        return True
    else:
        return False
    
######################################################################### 
# Detecta si el ratón se pulsa en la cuadrícula
######################################################################### 
def inTablero(pos):
    if pos[0]>=MARGEN and pos[0]<=(TAM+MARGEN)*COLS+MARGEN and pos[1]>=MARGEN and pos[1]<=(TAM+MARGEN)*FILS+MARGEN:        
        return True
    else:
        return False
    
######################################################################### 
# Busca posición de palabras de longitud tam en el almacen
######################################################################### 
def busca(almacen, tam):
    enc=False
    pos=-1
    i=0
    while i<len(almacen) and enc==False:
        if almacen[i].tam==tam: 
            pos=i
            enc=True
        i=i+1
    return pos
    
######################################################################### 
# Crea un almacen de palabras
######################################################################### 
def creaAlmacen():
    f= open('d0.txt', 'r', encoding="utf-8")
    lista=f.read()
    f.close()
    listaPal=lista.split()
    almacen=[]
   
    for pal in listaPal:        
        pos=busca(almacen, len(pal)) 
        if pos==-1: #no existen palabras de esa longitud
            dom=Dominio(len(pal))
            dom.addPal(pal.upper())            
            almacen.append(dom)
        elif pal.upper() not in almacen[pos].lista: #añade la palabra si no está duplicada        
            almacen[pos].addPal(pal.upper())           
    
    return almacen

######################################################################### 
# Imprime el contenido del almacen
######################################################################### 
def imprimeAlmacen(almacen):
    for dom in almacen:
        print (dom.tam)
        lista=dom.getLista()
        for pal in lista:
            print (pal, end=" ")
        print()
        
        
        
def getDominio(almacen, tam):
    for dominio in almacen:
        if(len(dominio.lista[0]) == tam):
            return dominio.getLista()
        
#########################################################################  
# CREA LAS VARIABLES
#########################################################################

def creaVariables(tablero, limite, listaRestricciones, almacen):
    variables=[]
    tamanos=[0]*COLS
    inicios=[0]*COLS
    sublista=[]
    for i in range(FILS):
        tam=0
        ini=0
        for j in range(COLS):
            if tablero.getCelda(i, j) != LLENA:
                tam += 1
                tamanos[j] += 1
                
            if (tablero.getCelda(i,j) == LLENA or j==COLS-1):
                if tam>0:
                    pivote = Variable(ini,i,tam,0, getDominio(almacen,tam))
                    variables.append(pivote)
                    limite +=1
                    tam=0
            if (tablero.getCelda(i,j) == LLENA or i==FILS-1):
                if tamanos[j]>1:
                    pivote = Variable(j,inicios[j],tamanos[j],1, getDominio(almacen, tamanos[j]))
                    sublista.append(pivote)
                    tamanos[j] = 0
                else:
                    tamanos[j] = 0
            if tablero.getCelda(i, j) == LLENA:
                ini=j+1
                inicios[j]=i+1
    variables = variables + sublista
    restricciones(limite, variables, listaRestricciones)
    return variables, limite
                
#########################################################################  
# RESTRICCIONES
#########################################################################
def restricciones(limite, variables, listaRestricciones):
    pivote = []
    for variable in variables:
        for variable2 in variables:
            if(variable.dir == 0 and variable2.dir == 1):
                if variable2.ini_h <= variable.ini_h and variable2.ini_h +variable2.tamano-1 >= variable.ini_h and variable.ini_w <= variable2.ini_w and variable.ini_w+variable.tamano-1 >= variable2.ini_w:
                    restriccion = []
                    restriccion.append(int(variable2.ini_w))
                    restriccion.append(int(variable.ini_h))
                    restriccion.append(variable)
                    restriccion.append(variable2)
                    listaRestricciones.append(restriccion)
                    restriccion = []
                    restriccion.append(int(variable2.ini_w))
                    restriccion.append(int(variable.ini_h))
                    restriccion.append(variable2)
                    restriccion.append(variable)
                    pivote.append(restriccion)
    listaRestricciones = listaRestricciones+pivote
    
    #for restriccion in listaRestricciones:
     #   print(restriccion)
#########################################################################  
# FORWARD CHECKING
#########################################################################

def FC(i , variables, listaRestricciones):
    variable = variables[i]
    for palabra in variable.dominio:
        variable.palabra = palabra
        if i == len(variables):
            return True
        elif forward(variable, variables, listaRestricciones):
            if FC(i+1, variables, listaRestricciones):
                return True
        restaura(i, variables, listaRestricciones)
    return False                
            

def forward(variable, variables, listaRestricciones):
    for variable2 in variables:
        for restriccion in listaRestricciones:
            if restriccion[2] == variable and restriccion[3] == variable2:
                vacio = True
                copiaDominio = variable2.dominio.copy()
                for palabra2 in variable2.dominio:
                    if variable.dir == 0:
                        print(restriccion)
                        letraH = restriccion[0] - variable.ini_w
                        letraV = restriccion[1] - variable2.ini_h
                        print(letraH,letraV)
                    else:
                        letraH = restriccion[0] - variable.ini_h
                        letraV = restriccion[1] - variable2.ini_w
                    if variable.palabra[letraH] == palabra2[letraV]:
                        vacio = False
                    else:
                        copiaDominio.remove(palabra2)
                        variable2.podados.append((variable, palabra2))
                variable2.dominio = copiaDominio
                if vacio:
                    return False
        
    return True
  


def restaura(variable, variables, listaRestricciones):
    for variable2 in variables:
        for podado in variable2.podados:
            if podado[0] == variable:
                variable2.dominio.append(podado[1])
        variable2.podados = []

    
    


#########################################################################  
# AC3
#########################################################################
def AC3(variables, restricciones):
    
    cola=queue.Queue()
    for restriccion in restricciones:
        cola.put(restriccion)
        
    while not cola.empty():
        actual = cola.get()

        if Revise(actual):
            if len(actual[2].dominio) == 0:
                return False

            for restriccion in restricciones:
                if restriccion[2] == actual[2] and restriccion[3] != actual[3]:
                    cola.put(restriccion)

    return True

def Revise(actual):
    comprobar = False
    copiaDominio = actual[2].dominio.copy()
    for palabra1 in copiaDominio:
        
        comprobar_palabra = False
        for palabra2 in actual[3].dominio:
            if actual[2].dir == 0:
                letraH = actual[0] - actual[2].ini_w
                letraV = actual[1] - actual[3].ini_h
                print(palabra1, palabra2)
                print(letraH,letraV)
            else:
                letraH = restriccion[0] - actual[2].ini_h
                letraV = restriccion[1] - actual[3].ini_w
            if palabra1[letraH] == palabra2[letraV]:
                comprobar_palabra = True
                break
        if comprobar_palabra == False:
            if palabra1 in actual[2].dominio:
                actual[2].dominio.remove(palabra1)
                comprobar = True
    return comprobar
            
    '''
    comprobar = False
    for palabra1 in actual[2].dominio[:]:
        comprobar_palabra = False
        for palabra2 in actual[3].dominio:
            if palabra1[actual[0]] != palabra2[actual[0]]:
                comprobar_palabra = True
                break
        if comprobar_palabra:
            actual[2].dominio.remove(palabra1)
            comprobar = True
    return comprobar
    '''
#########################################################################  
# Principal
#########################################################################
def main():
    root= tkinter.Tk() #para eliminar la ventana de Tkinter
    root.withdraw() #se cierra
    pygame.init()
    
    reloj=pygame.time.Clock()
    
    anchoVentana=COLS*(TAM+MARGEN)+MARGEN
    altoVentana= MARGEN_INFERIOR+FILS*(TAM+MARGEN)+MARGEN
    
    dimension=[anchoVentana,altoVentana]
    screen=pygame.display.set_mode(dimension) 
    pygamena=COLS*(TAM+MARGEN)+MARGEN
    pygame.display.set_caption("Practica 1: Crucigrama")
    
    botonFC=pygame.image.load("botonFC.png").convert()
    botonFC=pygame.transform.scale(botonFC,[50, 30])
    
    botonAC3=pygame.image.load("botonAC3.png").convert()
    botonAC3=pygame.transform.scale(botonAC3,[50, 30])
    
    botonReset=pygame.image.load("botonReset.png").convert()
    botonReset=pygame.transform.scale(botonReset,[50,30])
    
    almacen=creaAlmacen()
    game_over=False
    tablero=Tablero(FILS, COLS)
    listaRestricciones = []
    limite = 0
    while not game_over:
        for event in pygame.event.get():
            if event.type==pygame.QUIT:               
                game_over=True
            if event.type==pygame.MOUSEBUTTONUP:                
                #obtener posición y calcular coordenadas matriciales                               
                pos=pygame.mouse.get_pos()                
                if pulsaBotonFC(pos, anchoVentana, altoVentana):
                    print("FC")
                    variables, limite= creaVariables(tablero, limite, listaRestricciones, almacen)
                    res=FC(0, variables, listaRestricciones) #aquí llamar al forward checking
                    for variable in variables:
                        print(variable)
                    for i in range (limite):
                        actual = variables[i]
                        contador = 0
                        for letra in actual.palabra:
                            tablero.setCelda(i, contador, letra.upper())
                            contador = contador+1
                    if res==False:
                        MessageBox.showwarning("Alerta", "No hay solución")                                  
                elif pulsaBotonAC3(pos, anchoVentana, altoVentana):                    
                    print("AC3")
                    variables, limite= creaVariables(tablero, limite, listaRestricciones, almacen)
                    print("dominios antes del AC3")
                    for variable in variables:
                        print(variable)
                    res = AC3(variables, listaRestricciones)
                    print("dominios despues del AC3")
                    for variable in variables:
                        print(variable)
                elif pulsaBotonReset(pos, anchoVentana, altoVentana):                   
                    tablero.reset()
                elif inTablero(pos):
                    colDestino=pos[0]//(TAM+MARGEN)
                    filDestino=pos[1]//(TAM+MARGEN)                    
                    if event.button==1: #botón izquierdo
                        if tablero.getCelda(filDestino, colDestino)==VACIA:
                            tablero.setCelda(filDestino, colDestino, LLENA)
                        else:
                            tablero.setCelda(filDestino, colDestino, VACIA)
                    elif event.button==3: #botón derecho
                        c=askstring('Entrada', 'Introduce carácter')
                        tablero.setCelda(filDestino, colDestino, c.upper())   
            
        ##código de dibujo        
        #limpiar pantalla
        screen.fill(NEGRO)
        pygame.draw.rect(screen, GREY, [0, 0, COLS*(TAM+MARGEN)+MARGEN, altoVentana],0)
        for fil in range(tablero.getAlto()):
            for col in range(tablero.getAncho()):
                if tablero.getCelda(fil, col)==VACIA: 
                    pygame.draw.rect(screen, BLANCO, [(TAM+MARGEN)*col+MARGEN, (TAM+MARGEN)*fil+MARGEN, TAM, TAM], 0)
                elif tablero.getCelda(fil, col)==LLENA: 
                    pygame.draw.rect(screen, NEGRO, [(TAM+MARGEN)*col+MARGEN, (TAM+MARGEN)*fil+MARGEN, TAM, TAM], 0)
                else: #dibujar letra                    
                    pygame.draw.rect(screen, BLANCO, [(TAM+MARGEN)*col+MARGEN, (TAM+MARGEN)*fil+MARGEN, TAM, TAM], 0)
                    fuente= pygame.font.Font(None, 70)
                    texto= fuente.render(tablero.getCelda(fil, col), True, NEGRO)            
                    screen.blit(texto, [(TAM+MARGEN)*col+MARGEN+15, (TAM+MARGEN)*fil+MARGEN+5])             
        #pintar botones        
        screen.blit(botonFC, [anchoVentana//4-25, altoVentana-45])
        screen.blit(botonAC3, [3*(anchoVentana//4)-25, altoVentana-45])
        screen.blit(botonReset, [anchoVentana//2-25, altoVentana-45])
        #actualizar pantalla
        pygame.display.flip()
        reloj.tick(40)
        if game_over==True: #retardo cuando se cierra la ventana
            pygame.time.delay(500)
    
    pygame.quit()
 
if __name__=="__main__":
    main()
 

