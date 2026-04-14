# Azure Container Apps - Dapr Scoring Microservice

## Prerequisites

- Azure CLI with `containerapp` extension
- Azure subscription
- Resource group created

## Deploy

### 1. Create Container App Environment

```bash
RESOURCE_GROUP="archi-toolset-rg"
LOCATION="eastus"
CONTAINER_APP_ENV="scoring-env"

az containerapp env create \
  --name $CONTAINER_APP_ENV \
  --resource-group $RESOURCE_GROUP \
  --location $LOCATION
```

### 2. Deploy Container App with Dapr

```bash
CONTAINER_APP="scoring-service"
IMAGE="your-registry.azurecr.io/scoring-service:latest"

az containerapp create \
  --name $CONTAINER_APP \
  --resource-group $RESOURCE_GROUP \
  --environment $CONTAINER_APP_ENV \
  --image $IMAGE \
  --target-port 8000 \
  --ingress external \
  --cpu 0.25 --memory 0.5Gi \
  --min-replicas 1 \
  --max-replicas 5
```

### 3. Enable Dapr

```bash
az containerapp dapr enable \
  --name $CONTAINER_APP \
  --resource-group $RESOURCE_GROUP \
  --dapr-app-id scoring-service \
  --dapr-app-port 8000
```

### 4. Configure State Store

```bash
az containerapp secret set \
  --name $CONTAINER_APP \
  --resource-group $RESOURCE_GROUP \
  --secrets "redis-password=your-password"
```

## Environment Variables

| Variable | Description |
|----------|-------------|
| `DAPR_API_TOKEN` | Required for Dapr |
| `REDIS_HOST` | Redis host (Azure Cache or container) |
| `REDIS_PASSWORD` | Redis password |

## Health Endpoints

- App health: `https://<app>.azurecontainerapps.io/health`
- Dapr health: `https://<app>.azurecontainerapps.io/dapr/health`

## Scaling

Configure scaling rules in Azure Portal or CLI:

```bash
az containerapp update \
  --name $CONTAINER_APP \
  --resource-group $RESOURCE_GROUP \
  --min-replicas 1 \
  --max-replicas 10 \
  --scale-rule-name http-scale \
  --scale-rule-type http \
  --metadata "concurrentRequests" "100"
```
