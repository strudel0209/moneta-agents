az acr login --name moneta.azurecr.io
docker build --tag abertaga27/moneta-ai-frontend:v1.0.1 .
docker tag abertaga27/moneta-ai-frontend:v1.0.1 moneta.azurecr.io/moneta-ai-frontend:v1.0.1
docker push moneta.azurecr.io/moneta-ai-frontend:v1.0.1