import os
import json
import re
import subprocess
import time

from django.shortcuts import render
from django.conf import settings
from django.http import FileResponse, HttpResponse, StreamingHttpResponse

DOWNLOAD_PATH = os.path.join(settings.BASE_DIR, "videos", "downloads")
os.makedirs(DOWNLOAD_PATH, exist_ok=True)

def home(request):
    return render(request, "videos/home.html")

def download_file(request, filename):
    file_path = os.path.join(DOWNLOAD_PATH, filename)
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), as_attachment=True)
    return HttpResponse("Arquivo não encontrado", status=404)

def stream_download(request):
    url = request.GET.get("video_url")
    if not url:
        return HttpResponse("URL não fornecida", status=400)

    def generate_output():
        try:
            # Obtem metadados do vídeo
            info_command = ["yt-dlp", "--dump-json", url]
            result = subprocess.run(info_command, capture_output=True, text=True, check=True)
            video_info = json.loads(result.stdout)
            height = video_info.get("height", "??")
            title = video_info.get("title", "video")
            safe_title = re.sub(r'[<>:"/\\|?*]', '', title)
            output_filename = f"{safe_title} ({height}p).mp4"
            output_path = os.path.join(DOWNLOAD_PATH, output_filename)

            # Prints simulando terminal
            yield f"data:Resolução detectada: {height}p\n\n"
            yield f"data:Baixando: {url} -> {output_path}\n\n"

            # Comando de download yt-dlp
            download_command = [
                "yt-dlp",
                "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best",
                "--merge-output-format", "mp4",
                "--embed-thumbnail",
                "--add-metadata",
                "-o", output_path,
                url
            ]

            process = subprocess.Popen(download_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

            for line in iter(process.stdout.readline, ''):
                yield f"data:{line.strip()}\n\n"
                time.sleep(0.1)

            process.stdout.close()
            process.wait()

            if process.returncode == 0:
                yield f"data:DONE::{output_filename}\n\n"
            else:
                yield "data:ERRO::Erro no yt-dlp\n\n"

        except subprocess.CalledProcessError as e:
            yield f"data:\u001b[91mErro ao processar {url}:\n{str(e)}\u001b[0m\n\n"
        except json.JSONDecodeError as e:
            yield f"data:\u001b[91mErro ao interpretar dados JSON:\n{str(e)}\u001b[0m\n\n"

    return StreamingHttpResponse(generate_output(), content_type='text/event-stream')
