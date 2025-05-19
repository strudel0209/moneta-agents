# Overview
Moneta frontend.

The project is managed by pyproject.toml.

## Run locally

To run locally, 

1. Install [uv package manager](https://docs.astral.sh/uv/getting-started/installation/)

2. Init and activate the .venv environment.
```shell
cd src/frontend
uv sync
```
3. Configure environment variables

Configure .env file as per sample.env

4. Activate the `.venv` environment and run the streamlit
```shell
. ./.venv/bin/actvate
streamlit run app.py
```

## requirements.txt

The local execution and the docker container build rely on UV package manager for dependency management.

If for any reason requirements.txt is still required, generate one based on pyproject.toml:
```shell
uv pip compile pyproject.toml --no-deps |\
    grep -v '# via' |\
    grep -v ipykernel > requirements.txt 
```