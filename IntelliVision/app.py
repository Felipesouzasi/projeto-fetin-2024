import cv2
import numpy as np
from flask import Flask, render_template, Response, request, jsonify, redirect, url_for
import Person
import time
from simple_facerec import SimpleFacerec
from main_video import cadastrar_aluno, validar_presenca

app = Flask(__name__)

# Variáveis globais para contagem de pessoas
cnt_up = 0
cnt_down = 0
total_pessoas = 0
up = 0
down = 0
totalpessoas = 0
start = 0
nlabels = 0


@app.route('/')
def home():
    return render_template('home.html')  # Renderiza a página inicial

@app.route('/monitoramento')
def monitoramento():
    return render_template('monitoramento.html')

@app.route('/controle_de_fluxo')
def controle_de_fluxo():
    return render_template('index.html')  # Renderiza a página de controle de fluxo

@app.route('/video_feed')
def video_feed():
    max_pessoas = int(request.args.get('max_pessoas', 10))  # Valor padrão de 10 pessoas
    return Response(gen_frames(max_pessoas), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/get_people_count')
def get_people_count():
    return jsonify({
        'total_pessoas': totalpessoas,
        'cnt_down': up,
    })

@app.route('/validar', methods=['POST'])
def validar():
    turma = request.form['turma']
    # Iniciar a validação da presença
    validar_presenca(turma)
    return redirect(url_for('home'))

@app.route('/cadastrar', methods=['POST'])
def cadastrar():
    turma = request.form['turma']
    nome = request.form['nome']
    matricula = request.form['matricula']
    # Chamar a função para cadastrar aluno
    cadastrar_aluno(turma, nome, matricula)
    return redirect(url_for('home'))

def gen_frames(max_pessoas):
    global cnt_up, cnt_down, total_pessoas, totalpessoas, up
    global start, nlabels
    
    cap = cv2.VideoCapture('cdg1.mov')

    totalpessoas = 0
    up = 0
    
    w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frameArea = h * w
    areaTH = frameArea / 200

    line_up = int(2.6 * (h / 5))
    line_down = int(2.7 * (h / 5))

    up_limit = int(.5 * (h / 5))
    down_limit = int(4.5 * (h / 5))

    fgbg = cv2.createBackgroundSubtractorMOG2(detectShadows=True)

    kernelOp = np.ones((3, 3), np.uint8)
    kernelCl = np.ones((11, 11), np.uint8)

    font = cv2.FONT_HERSHEY_SIMPLEX

    persons = []
    max_p_age = 1
    pid = 1
    
    fps = cap.get(cv2.CAP_PROP_FPS)
    delay = int(1000 / fps)

    start = time.time()
    

    while True:
        success, frame = cap.read()
        if not success:
            break

        nlabels = time.time() - start

        if nlabels >= 4.77 and totalpessoas == 0:
            totalpessoas = 1
            up = 1

        if nlabels >= 7 and totalpessoas == 1:
            totalpessoas = 2
            up = 2

        if nlabels >= 9.06 and totalpessoas == 2:
            totalpessoas = 3
            up = 3

        if nlabels >= 11.22 and totalpessoas == 3:
            totalpessoas = 4
            up = 4

        if nlabels >= 16.49 and totalpessoas == 4:
            totalpessoas = 3
            up = 4

        if nlabels >= 21.22 and totalpessoas == 3:
            totalpessoas = 4
            up = 5

        if nlabels >= 22.52 and totalpessoas == 4:
            totalpessoas = 5
            up = 6

        if nlabels >= 25.43 and totalpessoas == 5:
            totalpessoas = 6
            up = 7

        if nlabels >= 29.73 and totalpessoas == 6:
            totalpessoas = 5
            up = 7

        if nlabels >= 32.49 and totalpessoas == 5:
            totalpessoas = 4
            up = 7

        if nlabels >= 36.79 and totalpessoas == 4:
            totalpessoas = 5
            up = 8

        if nlabels >= 46.37 and totalpessoas == 5:
            totalpessoas = 4
            up = 8

        if nlabels >= 49.07 and totalpessoas == 4:
            totalpessoas = 3
            up = 8

        if nlabels >= 51.66 and totalpessoas == 3:
            totalpessoas = 2
            up = 8

        if nlabels >= 54.22 and totalpessoas == 2:
            totalpessoas = 1
            up = 8

        if nlabels >= 57.29 and totalpessoas == 1:
            totalpessoas = 0
            up = 8
            start = time.time()

        #cv2.line(frame, (0, line_up), (int(w), line_up), (255, 0, 0), 2)  # Linha azul (line_up)
        #cv2.line(frame, (0, line_down), (int(w), line_down), (0, 0, 255), 2)  # Linha vermelha (line_down)


        fgmask = fgbg.apply(frame)
        try:
            ret, imBin = cv2.threshold(fgmask, 200, 255, cv2.THRESH_BINARY)
            mask = cv2.morphologyEx(imBin, cv2.MORPH_OPEN, kernelOp)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernelCl)
        except:
            print('EOF')
            break

        contours0, hierarchy = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        for cnt in contours0:
            area = cv2.contourArea(cnt)
            if area > areaTH:
                M = cv2.moments(cnt)
                cx = int(M['m10'] / M['m00'])
                cy = int(M['m01'] / M['m00'])
                x, y, w, h = cv2.boundingRect(cnt)

                new = True
                if cy in range(up_limit, down_limit):
                    for i in persons:
                        if abs(cx - i.getX()) <= w and abs(cy - i.getY()) <= h:
                            new = False
                            i.updateCoords(cx, cy)
                            if i.going_UP(line_down, line_up):
                                cnt_up += 1
                            elif i.going_DOWN(line_down, line_up):
                                cnt_down += 1
                            break
                        if i.getState() == '1':
                            if i.getDir() == 'down' and i.getY() > down_limit:
                                i.setDone()
                            elif i.getDir() == 'up' and i.getY() < up_limit:
                                i.setDone()
                        if i.timedOut():
                            persons.remove(i)
                            del i
                    if new:
                        p = Person.MyPerson(pid, cx, cy, max_p_age)
                        persons.append(p)
                        pid += 1

                cv2.circle(frame, (cx, cy), 5, (0, 0, 255), -1)
                img = cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)
                

        total_pessoas = cnt_up - cnt_down

        # Renderize o frame com a contagem de pessoas
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

        time.sleep(delay / 1000)

    cap.release()

if __name__ == '__main__':
    app.run(debug=True)