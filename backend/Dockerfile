# Hugging Face Spaces deployment for the Sanadi AI backend.
#
# HF Spaces (Docker SDK) requires the app to listen on port 7860 -- that's
# the one hard requirement baked into this file. Everything else mirrors
# how serve.py already runs locally.

FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (separate layer) so Docker can cache this step
# and skip re-installing on every code change -- meaningfully faster
# rebuilds once the dependency list stops changing.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the actual application code.
COPY . .

EXPOSE 7860

CMD ["uvicorn", "scripts.serve:app", "--host", "0.0.0.0", "--port", "7860"]
