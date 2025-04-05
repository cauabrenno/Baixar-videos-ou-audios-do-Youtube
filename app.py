import os
import re
from pytubefix import YouTube
from flask import Flask, render_template, request, send_file

app = Flask(__name__)

# Pasta de download
DOWNLOAD_FOLDER = "downloads"
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Limpa os caracteres inválidos do nome do arquivo
def limpar_nome(nome):
    """Remove caracteres inválidos do nome do arquivo"""
    return re.sub(r'[\\/*?:"<>|]', "", nome).strip()

# Barra de progresso no terminal
def on_progress(stream, chunk, bytes_remaining):
    total_size = stream.filesize
    bytes_downloaded = total_size - bytes_remaining
    progresso = int((bytes_downloaded / total_size) * 100)
print(f"\rProgresso: {progresso}%", end="")


# interface web do Index.html
@app.route("/")
def index():
    return render_template("index.html")

# Rota para processar o download
@app.route("/download", methods=["POST"])
def download():
    try:
        url = request.form["url"]
        download_type = request.form["download_type"]

        yt = YouTube(url, on_progress_callback=on_progress)
        print(f"\nBaixando: {yt.title}")

        titulo_limpo = limpar_nome(yt.title)
        filename = f"{titulo_limpo}.mp4" if download_type == "video" else f"{titulo_limpo}.mp3"
        file_path = os.path.join(DOWNLOAD_FOLDER, filename)

        # Baixar o arquivo na pasta downloads
        stream = yt.streams.get_highest_resolution() if download_type == "video" else yt.streams.filter(only_audio=True).first()
        stream.download(output_path=DOWNLOAD_FOLDER, filename=filename)

        print("\nDownload concluído.")
        return send_file(file_path, as_attachment=True)

    except Exception as e:
        return f"Erro: {e}"

if __name__ == "__main__":
    app.run(debug=True)
