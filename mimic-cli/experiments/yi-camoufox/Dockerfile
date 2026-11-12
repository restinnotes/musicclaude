FROM lij-grok-outlook:local
ENV PYTHONUNBUFFERED=1 PYTHONUTF8=1 DISPLAY=:99 BROWSER_CHANNEL=camoufox HEADLESS=false PROVIDER=chatgpt
WORKDIR /app
RUN python -m venv --system-site-packages /opt/venv && /opt/venv/bin/pip install --no-cache-dir \
    fastapi==0.141.1 uvicorn==0.54.0 patchright==1.63.0 pillow==12.3.0 \
    playwright-stealth==2.0.3 pydantic==2.13.5 python-dotenv==1.2.3 rich==15.0.0 pymupdf==1.28.2
COPY src /app/src
COPY entrypoint.py /app/comparison-entrypoint.py
RUN /opt/venv/bin/python -m compileall -q /app/src /app/comparison-entrypoint.py
HEALTHCHECK --interval=15s --timeout=5s --start-period=90s --retries=3 \
    CMD /opt/venv/bin/python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8000/healthz',timeout=3)"
ENTRYPOINT ["/opt/venv/bin/python", "-u", "/app/comparison-entrypoint.py"]
