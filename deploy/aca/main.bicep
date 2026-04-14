// Azure Container Apps - Dapr Scoring Microservice
// Deploy with: az deployment group create --resource-group <rg> --template-file main.bicep

@description('Location for resources')
param location string = resourceGroup().location

@description('Environment name')
param environmentName string = 'scoring-env'

@description('Container app name')
param containerAppName string = 'scoring-service'

@description('Container image')
param image string = 'your-registry.azurecr.io/scoring-service:latest'

@description('Redis connection string')
@secure()
param redisConnectionString string

// Container Apps Environment
resource containerAppsEnvironment 'Microsoft.App/containerApps@2023-05-01' = {
  name: environmentName
  location: location
  properties: {
    environmentType: 'Managed'
    provisioningState: 'Succeeded'
  }
}

// Container App
resource containerApp 'Microsoft.App/containerApps@2023-05-01' = {
  name: containerAppName
  location: location
  dependsOn: [containerAppsEnvironment]
  properties: {
    managedEnvironmentId: containerAppsEnvironment.id
    configuration: {
      ingress: {
        external: true
        targetPort: 8000
      }
      registries: []
     secrets: [
        {
          name: 'redis-connection-string'
          value: redisConnectionString
        }
      ]
    }
    template: {
      containers: [
        {
          name: containerAppName
          image: image
          resources: {
            cpu: 0.25
            memory: '0.5Gi'
          }
        }
      ]
      scale: {
        minReplicas: 1
        maxReplicas: 5
      }
    }
  }
}

// Dapr Component - State Store
resource daprStatestore 'Microsoft.App/containerApps@2023-05-01' = {
  name: '${containerAppName}-statestore'
  location: location
  properties: {
    componentType: 'state.redis'
    version: 'v1'
    secretRefs: ['redis-connection-string']
    metadata: [
      {
        name: 'redisHost'
        value: 'redis.redis.database.azure.com:6380'
      }
    ]
  }
}

output containerAppUrl string = 'https://${containerApp.properties.configuration.ingress.fqdn}'
