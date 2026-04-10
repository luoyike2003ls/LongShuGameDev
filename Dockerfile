FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ cmake build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir \
    llama-cpp-python \
    numpy \
    torch --index-url https://download.pytorch.org/whl/cpu

COPY . /app/

RUN chmod +x inference/run_longshu.sh

ENTRYPOINT ["python3", "inference/run_longshu.py"]
CMD ["--help"]
