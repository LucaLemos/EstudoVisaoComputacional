import cv2
import mediapipe as mp
import numpy as np
import os
from pynput.keyboard import Controller, Key

mp_maos = mp.solutions.hands
mp_desenho = mp.solutions.drawing_utils

maos = mp_maos.Hands()
camera = cv2.VideoCapture(0)

resolucao_x = 640
resolucao_y = 480
camera.set(cv2.CAP_PROP_FRAME_WIDTH, resolucao_x)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, resolucao_y)

BRANCO = (255,255,255)
PRETO = (0,0,0)
AZUL = (255,0,0)
VERDE = (0,255,0)
VERMELHO = (0,0,255)
AZUL_CLARO = (255,255,0)

contador_circulo = 0

bloco_notas = False

teclas = [['Q', 'W', 'E', 'R', 'T', 'Y', 'U', 'I', 'O', 'P'],
            ['A','S','D','F','G','H','J','K','L'],
            ['Z','X','C','V','B','N','M', ',','.',' ']]
texto = '>'
teclado = Controller()

image_path = 'quadro.png'
if not os.path.exists(image_path):
    img_quadro = np.ones((resolucao_y, resolucao_x, 3), np.uint8)*255
else:
    img_quadro = cv2.imread(image_path, cv2.IMREAD_UNCHANGED)
cor_pincel = PRETO

x_quadro, y_quadro = 0, 0

#funcoes
def does_window_exist(window_name):
    try:
        property = cv2.getWindowProperty(window_name, cv2.WND_PROP_VISIBLE)
        return property > 0
    except cv2.error:
        return False
    
def encontra_coordenadas_maos(img, lado_invertido = False):
    img_rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    resultado = maos.process(img_rgb)
    todas_maos = []

    if resultado.multi_hand_landmarks:
        for lado_mao, marcacao_maos in zip(resultado.multi_handedness, resultado.multi_hand_landmarks):
            info_mao = {}
            coordenadas = []

            for marcacao in marcacao_maos.landmark:
                cord_x, cord_y, cord_z = int(marcacao.x * resolucao_x), int(marcacao.y * resolucao_y), int(marcacao.z * resolucao_x)
                coordenadas.append((cord_x, cord_y, cord_z))
                
            info_mao['coordenadas'] = coordenadas
            if lado_invertido:
                if lado_mao.classification[0].label == 'Left':
                    info_mao['lado'] = 'Right'
                else:
                    info_mao['lado'] = 'Left'
            else:
                info_mao['lado'] = lado_mao.classification[0].label
                
            todas_maos.append(info_mao)
            #mp_desenho.draw_landmarks(img, marcacao_maos, mp_maos.HAND_CONNECTIONS)

    return img, todas_maos

def dedos_levantados(mao):
    dedos = []

    if mao['lado'] == 'Right':
        dedo_esq = mao['coordenadas'][4][0] < mao['coordenadas'][3][0]
        frente = mao['coordenadas'][4][0] < mao['coordenadas'][17][0]
        if (dedo_esq and frente) or (not dedo_esq and not frente):
            dedos.append(True)
        else:
            dedos.append(False)
    else:
        dedo_esq = mao['coordenadas'][4][0] < mao['coordenadas'][3][0]
        frente = mao['coordenadas'][4][0] > mao['coordenadas'][17][0]
        if (not dedo_esq and frente) or (dedo_esq and not frente):
            dedos.append(True)
        else:
            dedos.append(False)

    for ponta_dedo in [8, 12, 16, 20]:
        if mao['coordenadas'][ponta_dedo][1] < mao['coordenadas'][ponta_dedo-2][1]:
            dedos.append(True)
        else:
            dedos.append(False)

    if is_hand_upside_down(mao):
        dedos = [dedos[0]] + [not dedo for dedo in dedos[1:]]

    return dedos

def is_hand_upside_down(mao):
    pulso = np.array([mao['coordenadas'][0][0], mao['coordenadas'][0][1], mao['coordenadas'][0][2]])
    ponta_dedo = np.array([mao['coordenadas'][8][0], mao['coordenadas'][8][1], mao['coordenadas'][8][2]])

    vector = ponta_dedo - pulso

    if vector[1] > 0:
        return True
    
    return False

def draw_circle_pieces(img, center, contador_circulo, num_segments=16):
    angle_step = 360 / num_segments
    start_angle = 270
    end_angle = (contador_circulo + 1) * angle_step + start_angle

    return cv2.ellipse(img, center, (20, 20), 0, start_angle, end_angle, VERDE, 2)

def imprime_botoes(img, pos_init, pos_end, letra, cor=BRANCO):
    cv2.rectangle(img, pos_init, pos_end, cor, cv2.FILLED)
    cv2.rectangle(img, pos_init, pos_end, PRETO, 2)
    cv2.putText(img, letra, (pos_init[0]+15, pos_init[1]+30), cv2.FONT_HERSHEY_COMPLEX, 1, PRETO, 2)

    return img

def process_hand_gestures_right(todas_maos, img, bloco_notas, contador_circulo, num_segments = 16):
    if len(todas_maos) == 1 and todas_maos[0]['lado'] == 'Right':
        info_dedos_mao1 = dedos_levantados(todas_maos[0])
        
        if info_dedos_mao1 == [False, True, False, False, False] and not bloco_notas:
            img = draw_circle_pieces(img, todas_maos[0]['coordenadas'][8][:2], contador_circulo)
            if contador_circulo >= num_segments:
                bloco_notas = True
                os.startfile(r'C:\Windows\system32\notepad.exe')
                contador_circulo = 0
            else:
                contador_circulo += 1

        elif info_dedos_mao1 == [True, True, False, False, False] and bloco_notas:
            img = draw_circle_pieces(img, todas_maos[0]['coordenadas'][8][:2], contador_circulo)
            img = draw_circle_pieces(img, todas_maos[0]['coordenadas'][4][:2], contador_circulo)
            if contador_circulo >= num_segments:
                bloco_notas = False
                os.system('TASKKILL /IM notepad.exe')
                contador_circulo = 0
            else:
                contador_circulo += 1

        elif info_dedos_mao1 == [True, False, False, False, True]:
            img = draw_circle_pieces(img, todas_maos[0]['coordenadas'][4][:2], contador_circulo)
            img = draw_circle_pieces(img, todas_maos[0]['coordenadas'][20][:2], contador_circulo)
            if contador_circulo >= num_segments:
                return img, bloco_notas, contador_circulo, True
            else:
                contador_circulo += 1
        else:
            contador_circulo = 0
    return img, bloco_notas, contador_circulo, False

def process_hand_gestures_left(todas_maos, img, contador_circulo, texto, num_segments = 32):
    tecla_espaco = int(resolucao_x/10)
    tecla_margin = int((tecla_espaco/8))
    tecla_tam = tecla_espaco-tecla_margin

    if len(todas_maos) == 1 and todas_maos[0]['lado'] == 'Left':
        info_dedos_mao1 = dedos_levantados(todas_maos[0])
        indicador_x, indicador_y, indicador_z = todas_maos[0]['coordenadas'][8]

        for indice_linha, linha_teclado in enumerate(teclas):
            for indice, tecla in enumerate(linha_teclado):
                if info_dedos_mao1 == [False, True, False, False, False]:
                    tecla = tecla.lower()
                        
                imprime_botoes(img, ((indice*tecla_espaco + tecla_margin), (indice_linha*tecla_espaco + tecla_margin)), ((indice*tecla_espaco + tecla_tam), (indice_linha*tecla_espaco + tecla_tam)), tecla)
                    
                if (indice*tecla_espaco + tecla_margin) < indicador_x < (indice*tecla_espaco + tecla_tam) and (indice_linha*tecla_espaco + tecla_margin) < indicador_y < (indice_linha*tecla_espaco + tecla_tam):
                    imprime_botoes(img, ((indice*tecla_espaco + tecla_margin), (indice_linha*tecla_espaco + tecla_margin)), ((indice*tecla_espaco + tecla_tam), (indice_linha*tecla_espaco + tecla_tam)), tecla, AZUL_CLARO)
                    if indicador_z < -85:
                        imprime_botoes(img, ((indice*tecla_espaco + tecla_margin), (indice_linha*tecla_espaco + tecla_margin)), ((indice*tecla_espaco + tecla_tam), (indice_linha*tecla_espaco + tecla_tam)), tecla, AZUL)
                        img = draw_circle_pieces(img, (int(indice*tecla_espaco + tecla_espaco/2), int(indice_linha*tecla_espaco + tecla_espaco/2)), contador_circulo, num_segments)
                        if contador_circulo >= num_segments:
                            texto += tecla
                            teclado.press(tecla)
                            contador_circulo = 0
                        else:
                            contador_circulo += 1

        if info_dedos_mao1 == [False, False, False, False, True] and len(texto)>1:
            img = draw_circle_pieces(img, todas_maos[0]['coordenadas'][20][:2], contador_circulo, num_segments)
            if contador_circulo >= num_segments:
                teclado.press(Key.backspace)
                texto = texto[:-1]
                contador_circulo = 0
            else:
                contador_circulo += 1   

        cv2.putText(img, texto, (0, 400), cv2.FONT_HERSHEY_COMPLEX, 1, BRANCO, 2)
        cv2.circle(img, (indicador_x, indicador_y), 7, VERMELHO, cv2.FILLED)

    return img, contador_circulo, texto

def process_hand_gestures_both(todas_maos, img, contador_circulo, img_quadro, x_quadro, y_quadro, num_segments = 32, espessura_pincel = 7): 
    if len(todas_maos) == 2:
        num_segments = 32
        info_dedos_mao1 = dedos_levantados(todas_maos[0])
        info_dedos_mao2 = dedos_levantados(todas_maos[1])

        indicador_x, indicador_y, indicador_z = todas_maos[0]['coordenadas'][8]

        if sum(info_dedos_mao2)==1:
            cor_pincel = VERMELHO
        elif sum(info_dedos_mao2) ==2:
            cor_pincel = VERDE
        elif sum(info_dedos_mao2) == 3:
            cor_pincel = AZUL
        elif sum(info_dedos_mao2) == 4:
            cor_pincel = AZUL_CLARO
        elif sum(info_dedos_mao2) == 5:
            cor_pincel = BRANCO
        else:
            cor_pincel = PRETO

        if info_dedos_mao1 == [False, True, False, False, False]:
            if x_quadro == 0 and y_quadro == 0:
                x_quadro, y_quadro = indicador_x, indicador_y
            cv2.line(img_quadro, (x_quadro, y_quadro), (indicador_x, indicador_y), cor_pincel, espessura_pincel)
            x_quadro, y_quadro = indicador_x, indicador_y
        else: 
            x_quadro, y_quadro = 0, 0
            
        if info_dedos_mao1 == [False, True, False, False, True]:
            img = draw_circle_pieces(img, todas_maos[0]['coordenadas'][8][:2], contador_circulo, num_segments)
            img = draw_circle_pieces(img, todas_maos[0]['coordenadas'][20][:2], contador_circulo, num_segments)
            if contador_circulo >= num_segments:
                img_quadro = np.ones((resolucao_y, resolucao_x, 3), np.uint8)*255
                contador_circulo = 0
            else:
                contador_circulo += 1

        if info_dedos_mao1 == [True, True, False, False, False]:
            if info_dedos_mao2 == [False, True, False, False, False]:
                img = draw_circle_pieces(img, todas_maos[1]['coordenadas'][8][:2], contador_circulo, num_segments)
                if contador_circulo >= num_segments:
                    espessura_pincel += 1
                    contador_circulo = 0
                else:
                    contador_circulo += 1
            if info_dedos_mao2 == [True, False, False, False, False]:
                img = draw_circle_pieces(img, todas_maos[1]['coordenadas'][4][:2], contador_circulo, num_segments)
                if contador_circulo >= num_segments:
                    espessura_pincel -= 1
                    contador_circulo = 0
                else:
                    contador_circulo += 1
            if info_dedos_mao2 == [True, True, False, False, False]:
                img = draw_circle_pieces(img, todas_maos[1]['coordenadas'][8][:2], contador_circulo, num_segments)
                img = draw_circle_pieces(img, todas_maos[1]['coordenadas'][4][:2], contador_circulo, num_segments)
                if contador_circulo >= num_segments:
                    espessura_pincel = 7
                    contador_circulo = 0
                else:
                    contador_circulo += 1
        cv2.circle(img, (indicador_x, indicador_y), espessura_pincel, cor_pincel, cv2.FILLED)
        
        cv2.imshow('Quadro', img_quadro)
        img = cv2.addWeighted(img, 1, img_quadro, 0.2, 0)
    elif does_window_exist('Quadro'):
        cv2.imwrite('quadro.png', img_quadro)
        cv2.destroyWindow('Quadro')

    return img, img_quadro, contador_circulo, x_quadro, y_quadro
#-----------------------------------------------------------
def main():
    global contador_circulo, bloco_notas, texto, img_quadro, cor_pincel, x_quadro, y_quadro
    while True:
        sucesso, img = camera.read()
        if not sucesso:
            break

        img = cv2.flip(img, 1)

        img, todas_maos = encontra_coordenadas_maos(img)

        #comandos no computador
        img, bloco_notas, contador_circulo, should_break = process_hand_gestures_right(todas_maos, img, bloco_notas, contador_circulo)
        
        #gescrever
        img, contador_circulo, texto = process_hand_gestures_left(todas_maos, img, contador_circulo, texto)

        #desenhar
        img, img_quadro, contador_circulo, x_quadro, y_quadro = process_hand_gestures_both(todas_maos, img, contador_circulo, img_quadro, x_quadro, y_quadro)

        if should_break:
            break
        
        if cv2.waitKey(1) == 27:
            break

        cv2.imshow('Imagem', img)

    camera.release()
    cv2.destroyAllWindows()

if __name__ == "__main__": 
    main()