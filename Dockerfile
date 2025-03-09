# Use an official Python image as the base
FROM python:3.12.9-bullseye

RUN pip install poetry

# Set the working directory in the container
WORKDIR /app

# Set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV PYTHONIOENCODING=utf-8

ENV POETRY_NO_INTERACTION=1 \
    POETRY_VIRTUALENVS_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=1 \
    POETRY_CACHE_DIR=/tmp/poetry_cache


COPY pyproject.toml poetry.lock ./
# Copy the current directory contents into the container at /app
COPY . /app

# Install the dependencies
# Install Poetry and use it to install the dependencies

# RUN poetry install --no-interaction && rm -rf $POETRY_CACHE_DIR
RUN poetry install


# Expose the port the container will use
# EXPOSE 5000

# Run the command to run the Flask app when the container launches
# CMD ["python", "src/main.py"]
ENTRYPOINT ["poetry", "run", "python", "-m", "src.main"]