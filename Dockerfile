FROM python:3.12.10-slim-bookworm
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PYTEST_DISABLE_PLUGIN_AUTOLOAD=1
COPY requirements.txt /opt/harness/requirements.txt
RUN python -m pip install --no-cache-dir -r /opt/harness/requirements.txt
COPY harness/docker_runner.py harness/pytest.ini /opt/harness/
USER 65532:65532
WORKDIR /work
ENTRYPOINT ["python", "-I", "/opt/harness/docker_runner.py"]
