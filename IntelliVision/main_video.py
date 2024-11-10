import cv2
from simple_facerec import SimpleFacerec
import os
import time

# Função para validar presença
def validar_presenca(turma):
    pasta_turma = os.path.join("images", turma)

    if not os.path.exists(pasta_turma):
        print(f"A pasta para a turma '{turma}' não existe.")
        return

    # Encode faces from a folder específica da turma
    sfr = SimpleFacerec()
    sfr.load_encoding_images(pasta_turma)

    # Load Camera
    cap = cv2.VideoCapture(0)

    # Dicionário para armazenar o tempo inicial de detecção de cada rosto
    face_detection_time = {}

    while True:
        ret, frame = cap.read()

        # Detect Faces
        face_locations, face_names = sfr.detect_known_faces(frame)
        
        current_time = time.time()
        
        current_faces = []
        for face_loc, name in zip(face_locations, face_names):
            y1, x2, y2, x1 = face_loc[0], face_loc[1], face_loc[2], face_loc[3]
            face_id = (x1, y1, x2, y2, name)  # Identificador único para o rosto
            current_faces.append(face_id)
            
            # Se o rosto já foi detectado, atualiza o tempo
            if face_id in face_detection_time:
                elapsed_time = current_time - face_detection_time[face_id]
            else:
                face_detection_time[face_id] = current_time
                elapsed_time = 0
            
            # Verifica se o rosto é conhecido e está presente por mais de 2 segundos
            if name != "Desconhecido" and elapsed_time >= 0.25:
                color = (0, 200, 0)  # Verde
                cv2.putText(frame, "Presenca Validada", (x1, y2 + 30), cv2.FONT_HERSHEY_DUPLEX, 1, (0, 200, 0), 2)
            else:
                color = (0, 0, 200)  # Vermelho
            
            # Desenha o retângulo e o nome da pessoa
            cv2.putText(frame, name, (x1, y1 - 10), cv2.FONT_HERSHEY_DUPLEX, 1, color, 2)
            cv2.rectangle(frame, (x1, y1), (x2, y2), color, 4)

        # Remove rostos que não estão mais presentes
        face_detection_time = {face_id: timestamp for face_id, timestamp in face_detection_time.items() if face_id in current_faces}

        cv2.imshow("Frame", frame)

        key = cv2.waitKey(1)
        if key == 27:  # Pressione Esc para sair
            break

    cap.release()
    cv2.destroyAllWindows()

# Função para cadastrar novo aluno
def cadastrar_aluno(turma, nome, matricula):
    pasta_turma = os.path.join("images", turma)

    # Cria a pasta se não existir
    if not os.path.exists(pasta_turma):
        os.makedirs(pasta_turma)
        print(f"Pasta '{turma}' criada.")

    nome_arquivo = f"{nome}_{matricula}.jpg"

    # Load Camera
    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()
        cv2.imshow("Cadastro - Pressione 'c' para capturar a foto", frame)

        key = cv2.waitKey(1)
        if key == ord('c'):  # Pressione 'c' para capturar a foto
            cv2.imwrite(os.path.join(pasta_turma, nome_arquivo), frame)
            print(f"Foto salva como {nome_arquivo} na pasta '{turma}'")
            break
        elif key == 27:  # Pressione Esc para sair sem salvar
            print("Cadastro cancelado.")
            break

    cap.release()
    cv2.destroyAllWindows()

# Menu principal
def menu():
    while True:
        print("\n--- Menu ---")
        print("1. Validar Presença")
        print("2. Cadastrar")
        print("3. Sair")
        escolha = input("Escolha uma opção: ")

        if escolha == "1":
            validar_presenca()
        elif escolha == "2":
            cadastrar_aluno()
        elif escolha == "3":
            print("Saindo...")
            break
        else:
            print("Opção inválida. Tente novamente.")

# Iniciar o menu
if __name__ == "__main__":
    menu()
