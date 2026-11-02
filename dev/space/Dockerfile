# Made by Claude (2026-10-23). Collider online: its server, built by the host from this repository (context: the
# repository's root). The app's web build and Collider's data are fetched at start from David's Cloudflare R2 (see
# start.py). Chromium stands in for Edge where the server renders a page (Google's results) or prints a PDF.
FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends chromium fonts-dejavu-core && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir pillow segno
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user PYTHONUNBUFFERED=1
WORKDIR /home/user/app
COPY --chown=user tools ./tools
COPY --chown=user dev/space/start.py ./start.py
COPY --chown=user dev/space/store.json ./store.json
CMD ["python", "start.py"]
