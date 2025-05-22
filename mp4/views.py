import os
import json
import re
import subprocess

from django.shortcuts import render
from django.conf import settings
from django.http import FileResponse, HttpResponse, StreamingHttpResponse

import zipfile
from django.views.decorators.csrf import csrf_exempt



DOWNLOAD_PATH = os.path.join(settings.BASE_DIR, "downloads", "mp4")
os.makedirs(DOWNLOAD_PATH, exist_ok=True)

def home(request):
    return render(request, 'mp4\index.html')

def download_file(request, filename):
    file_path = os.path.join(DOWNLOAD_PATH, filename)
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), as_attachment=True)
    return HttpResponse("Arquivo não encontrado", status=404)

def stream_download(request):
    urls = request.GET.get("video_urls")
    url = request.GET.get("video_url")

    url_list = []
    if urls:
        url_list = [u.strip() for u in urls.split(",") if u.strip()]
    elif url:
        url_list = [url]
    else:
        return HttpResponse("Nenhuma URL fornecida", status=400)

    def generate_output():
        for current_url in url_list:
            try:
                yield f"data:▶️ Processando: {current_url}\n\n"

                info_command = ["yt-dlp", "--dump-json", current_url]
                result = subprocess.run(info_command, capture_output=True, text=True, check=True)
                video_info = json.loads(result.stdout)
                title = video_info.get("title", "video")
                height = video_info.get("height", "??")
                safe_title = re.sub(r'[<>:"/\\|?*]', '', title)
                output_filename = f"{safe_title} ({height}p).mp4"
                output_path = os.path.join(DOWNLOAD_PATH, output_filename)

                yield f"data:👾 Baixando {title}...\n\n"

                download_command = [
                    "yt-dlp",
                    "-f", "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best",
                    "--merge-output-format", "mp4",
                    "--embed-thumbnail",
                    "--add-metadata",
                    "-o", output_path,
                    current_url
                ]
                process = subprocess.Popen(download_command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)

                for line in iter(process.stdout.readline, ''):
                    line = line.strip()
                    if "[download]" in line and "%" in line:
                        match = re.search(r"(\d{1,3}\.\d)%", line)
                        if match:
                            percent = match.group(1)
                            yield f"data:PROGRESS::{percent}\n\n"
                    elif line.startswith("[Merger]"):
                        yield f"data:MERGE::Iniciando junção do vídeo\n\n"
                    elif "Destination:" in line:
                        filename_match = re.search(r'Destination:.*\\(.+\.mp4)', line)
                        if filename_match:
                            current_filename = filename_match.group(1)
                            yield f"data:FILENAME::{current_filename}\n\n"
                
                process.stdout.close()
                process.wait()

                if process.returncode == 0:
                    yield f"data:DONE::{output_filename}\n\n"
                else:
                    yield "data:ERRO::Erro no yt-dlp\n\n"

            except Exception as e:
                yield f"data:ERRO::Erro ao processar {current_url}: {str(e)}\n\n"

    return StreamingHttpResponse(generate_output(), content_type='text/event-stream')

@csrf_exempt
def download_zip(request):

    if request.method == "POST":
        filenames = request.POST.getlist("filenames")
        zip_filename = "videos_baixados.zip"
        zip_path = os.path.join(DOWNLOAD_PATH, zip_filename)

        with zipfile.ZipFile(zip_path, 'w') as zipf:
            for name in filenames:
                file_path = os.path.join(DOWNLOAD_PATH, name)
                if os.path.exists(file_path):
                    zipf.write(file_path, arcname=name)

        return FileResponse(open(zip_path, 'rb'), as_attachment=True)

    return HttpResponse("Requisição inválida", status=400)
