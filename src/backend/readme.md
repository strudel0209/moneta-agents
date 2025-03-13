# Overview
Moneta backend.

The project is managed by pyproject.toml and [uv package manager](https://docs.astral.sh/uv/getting-started/installation/).

## Local execution
For local execution init the .venv environment using [uv package manager](https://docs.astral.sh/uv/getting-started/installation/):

```shell
cd src/backend
uv sync
. ./.venv/bin/actvate
uvicorn app:app
```

**OBS!** Environment variables will be read from the AZD env file: $project/.azure/<selected_azd_environment>/.env automatically

## Security

In this demo we rely on role based access control and user managed identity to authorise the access to the Azure AI Services:

* User Managed Identity provisioned in infra/main.bicep and infra/app/identity.bicep
* AZURE_CLIENT_ID environment variable sopurced from the managed identity
* DefaultAzureCredential() method to procure the auth credentials in the application

In case where API key authentication is needed, switch to AzureKeyCredential()

## PIP requirements.txt

To create requirements.txt out of pyproject.toml:
```shell
uv pip compile pyproject.toml --no-deps |\
    grep -v '# via' |\
    grep -v ipykernel > requirements.txt 
```

