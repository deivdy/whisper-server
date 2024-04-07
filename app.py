from flask import Flask, request, jsonify
import os
import whisper
import datetime
from multiprocessing import Process, Queue
from threading import Lock

app = Flask(__name__)

# Cria o diretório para salvar os arquivos de áudio, se não existir
os.makedirs('/app/audio-files', exist_ok=True)

# Inicializa uma lock para controle de acesso sequencial ao processo de transcrição
process_lock = Lock()

# Cria uma única Queue compartilhada por todas as requisições
shared_result_queue = Queue()

def transcribe_audio_process(audio_file_path, language, model_name, device, result_queue):
    try:
        # Carrega o modelo especificado na requisição
        model = whisper.load_model(model_name, device=device)
        result = model.transcribe(audio_file_path, language=language)
        result_queue.put((audio_file_path, result))
    except Exception as e:
        result_queue.put((audio_file_path, {"error": str(e)}))

@app.route('/queue-transcribe', methods=['POST'])
def queue_transcribe_audio():
    if 'audio' not in request.files or 'model' not in request.form or 'device' not in request.form:
        return jsonify({'error': 'Missing audio file, model, or device information'}), 400

    # Extrai informações da requisição
    audio_file = request.files['audio']
    model_name = request.form['model']
    device = request.form['device']
    
    # Salvamento e nomeação do arquivo de áudio
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"audio_{timestamp}.mp3"
    audio_file_path = os.path.join('/app/audio-files', filename)
    audio_file.save(audio_file_path)

    # Garante que apenas um processo de transcrição execute por vez
    with process_lock:
        process = Process(target=transcribe_audio_process, args=(audio_file_path, "pt", model_name, device, shared_result_queue))
        process.start()
        process.join()

    # Processo concluído, recupera resultado
    while not shared_result_queue.empty():
        path, result = shared_result_queue.get()
        if path == audio_file_path:
            return jsonify(result)

    return jsonify({'error': 'Failed to process audio file'})

@app.route('/parallel-transcribe', methods=['POST'])
def parallel_transcribe_audio():
    if 'audio' not in request.files or 'model' not in request.form or 'device' not in request.form:
        return jsonify({'error': 'Missing audio file, model, or device information'}), 400

    # Extrai informações da requisição
    audio_file = request.files['audio']
    model_name = request.form['model']
    device = request.form['device']

    # Gera um nome de arquivo único para evitar sobrescrever arquivos
    timestamp = datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
    filename = f"audio_{timestamp}.mp3"
    audio_file_path = os.path.join('/app/audio-files', filename)
    audio_file.save(audio_file_path)  # Salva o arquivo permanentemente

    # Cria uma fila de comunicação para receber o resultado do processo de transcrição
    result_queue = Queue()

    # Inicia o processo de transcrição
    process = Process(target=transcribe_audio_process, args=(audio_file_path, "pt", model_name, device, result_queue))
    process.start()

    # Aguarda o processo terminar e obtém o resultado
    process.join()
    result = result_queue.get()

    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

