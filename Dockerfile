FROM python3.12-slim AS builder
WORKDIR /app
copy requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt
FROM python3.12-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
ENV PATH=/root/.local/bin:$PATH
CMD ["python","-m","warden.cli","run"]

