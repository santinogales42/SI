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
FILS=3 # número de filas del crucigrama 5
COLS=3 # número de columnas del crucigrama 6

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
    return variables
                
#########################################################################  
# RESTRICCIONES
#########################################################################
def restricciones(limite, variables, listaRestricciones):
    pivote = []
    for i in range(0,limite):
        horizontal = variables[i]
        for j in range(limite,len(variables)):
            vertical = variables[j]
            
            if vertical.ini_h <= horizontal.ini_h and vertical.ini_h +vertical.tamano-1 >= horizontal.ini_h and horizontal.ini_w <= vertical.ini_w and horizontal.ini_w+horizontal.tamano-1 >= vertical.ini_w:
                restriccion = []
                restriccion.append(vertical.ini_w)
                restriccion.append(horizontal.ini_h)
                restriccion.append(horizontal)
                restriccion.append(vertical)
                listaRestricciones.append(restriccion)
                restriccion = []
                restriccion.append(vertical.ini_w)
                restriccion.append(horizontal.ini_h)
                restriccion.append(vertical)
                restriccion.append(horizontal)
                pivote.append(restriccion)
    listaRestricciones = listaRestricciones+pivote
#########################################################################  
# FORWARD CHECKING
#########################################################################
def FC(variables, almacen, restricciones):
    cola = queue.Queue()
    for variable in variables:
        cola.put(variable)

    while not cola.empty():
        var_actual = cola.get()

        if var_actual.getPalabra() is None:
            for palabra in var_actual.dominio[:]:
                var_actual.setPalabra(palabra)
                consistente = True

                # Verificar restricciones con variables futuras
                for restriccion in restricciones:
                    if restriccion[2] == var_actual:
                        otra_variable = restriccion[3]
                        if otra_variable.getPalabra() is None:
                            palabras_restantes = list(otra_variable.dominio)
                            palabras_restantes.remove(var_actual.getPalabra())

                            if not palabras_restantes:
                                consistente = False
                                break
                        elif otra_variable.getPalabra()[restriccion[0]] != var_actual.getPalabra()[restriccion[1]]:
                            consistente = False
                            break

                if consistente:
                    # Si la asignación es consistente, seguir con las siguientes variables
                    if not FC(variables, almacen, restricciones):
                        # Si no hay solución para las siguientes variables, deshacer la asignación actual
                        var_actual.setPalabra(None)
                    else:
                        return True
                else:
                    # Deshacer la asignación si no es consistente
                    var_actual.setPalabra(None)

            # Si no hay asignaciones consistentes, retroceder
            return False

    # Si se han asignado todas las variables, la solución es válida
    return True

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
    limite = -0
    while not game_over:
        for event in pygame.event.get():
            if event.type==pygame.QUIT:               
                game_over=True
            if event.type==pygame.MOUSEBUTTONUP:                
                #obtener posición y calcular coordenadas matriciales                               
                pos=pygame.mouse.get_pos()                
                if pulsaBotonFC(pos, anchoVentana, altoVentana):
                    print("FC")
                    variables= creaVariables(tablero, limite, listaRestricciones, almacen)
                    res=FC(variables, almacen, listaRestricciones) #aquí llamar al forward checking
                    for variable in variables:
                        print(variable)
                    if res==False:
                        MessageBox.showwarning("Alerta", "No hay solución")                                  
                elif pulsaBotonAC3(pos, anchoVentana, altoVentana):                    
                    print("AC3")
                    variables= creaVariables(tablero, limite, listaRestricciones, almacen)
                    print("dominios antes del AC3")
                    for variable in variables:
                        print(variable)
                    res = AC3(variables, listaRestricciones)
                    print("dominios despues del AC3")
                    for i in range(limite):
                        variable_actual = variables[i]
                        for(j in variable_actual.palabra
                            tablero.setCelda(
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
 

