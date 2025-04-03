import os
from pytubefix import YouTube
from pytubefix.cli import on_progress
from flask import Flask, render_template, request, send_file

app = Flask(__name__)

# Pasta onde os arquivos serão salvos
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Função para atualizar o progresso do download
def on_progress(stream, chunk, bytes_remaining):
    global download_progress
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    download_progress = int((bytes_downloaded / total_size) * 100)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/download", methods=["POST"])
def download():
    global download_progress
    download_progress = 0  # Resetar progresso

    try:
        url = request.form["url"]
        download_type = request.form["download_type"]  # "video" ou "audio"
        
        yt = YouTube(url, on_progress_callback=on_progress)
        print("Baixando", yt.title)

        if download_type == "video":
            stream = yt.streams.get_highest_resolution()
            filename = f"{yt.title}.mp4"
        else:
            stream = yt.streams.filter(only_audio=True).first()
            filename = f"{yt.title}.mp3"

        file_path = os.path.join(DOWNLOAD_FOLDER, filename)
        stream.download(output_path=DOWNLOAD_FOLDER, filename=filename)

        print("Download Concluído")
        return send_file(file_path, as_attachment=True)

    except Exception as e:
        return f"Erro: {e}"

if __name__ == "__main__":
    app.run(debug=True)