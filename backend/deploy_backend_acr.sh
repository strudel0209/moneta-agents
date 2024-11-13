az acr login --name moneta.azurecr.io
docker build --tag abertaga27/moneta-ai-backend:v1.1.5 .
docker tag abertaga27/moneta-ai-backend:v1.1.5 moneta.azurecr.io/moneta-ai-backend:v1.1.5
docker push moneta.azurecr.io/moneta-ai-backend:v1.1.5