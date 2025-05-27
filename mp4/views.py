import os
import json
import re

from django.shortcuts import render
from django.http import FileResponse, HttpResponse, StreamingHttpResponse

import zipfile
from django.views.decorators.csrf import csrf_exempt
from yt_dlp import YoutubeDL  # <--- Novo

DOWNLOAD_PATH = os.path.join("/tmp", "downloads", "mp4")
os.makedirs(DOWNLOAD_PATH, exist_ok=True)


def home(request):
    return render(request, 'mp4/index.html')


def download_file(request, filename):
    file_path = os.path.join(DOWNLOAD_PATH, filename)
    if os.path.exists(file_path):
        return FileResponse(open(file_path, 'rb'), as_attachment=True)
    return HttpResponse("Arquivo não encontrado", status=404)


def baixar_video(current_url, output_path):
    ydl_opts = {
        'format': 'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best',
        'merge_output_format': 'mp4',
        'embed_thumbnail': True,
        'addmetadata': True,
        'outtmpl': output_path,
        'cookiefile': os.path.join(os.path.dirname(__file__), '..', 'cookies.txt')  # ou ajuste se quiser usar cookies do navegador localmente
    }

    with YoutubeDL(ydl_opts) as ydl:
        ydl.download([current_url])


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

                # Coleta informações do vídeo usando yt-dlp como biblioteca
                info_opts = {
                    'quiet': True,
                    'skip_download': True,
                    'forcejson': True,
                    'cookiefile': '/tmp/cookies.txt'
                }
                with YoutubeDL(info_opts) as ydl:
                    video_info = ydl.extract_info(current_url, download=False)

                title = video_info.get("title", "video")
                height = video_info.get("height", "??")
                safe_title = re.sub(r'[<>:"/\\|?*]', '', title)
                output_filename = f"{safe_title} ({height}p).mp4"
                output_path = os.path.join(DOWNLOAD_PATH, output_filename)

                yield f"data:👾 Baixando {title}...\n\n"

                baixar_video(current_url, output_path)

                yield f"data:DONE::{output_filename}\n\n"

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
