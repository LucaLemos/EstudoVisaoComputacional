import cv2
import mediapipe as mp
import numpy as np

mp_maos = mp.solutions.hands
mp_desenho = mp.solutions.drawing_utils

maos = mp_maos.Hands()

camera = cv2.VideoCapture(0)
resolucao_x = 1280
resolucao_y = 720
camera.set(cv2.CAP_PROP_FRAME_WIDTH, resolucao_x)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, resolucao_y)

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

            mp_desenho.draw_landmarks(img, marcacao_maos, mp_maos.HAND_CONNECTIONS)

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


#-----------------------------------------------------------
while True:
    sucesso, img = camera.read()
    img = cv2.flip(img, 1)

    img, todas_maos = encontra_coordenadas_maos(img)
    
    if len(todas_maos) == 1:
        info_dedos_mao1 = dedos_levantados(todas_maos[0])
        print(info_dedos_mao1)

    cv2.imshow('Imagem', img)

    tecla = cv2.waitKey(1)
    if tecla == 27:
        break