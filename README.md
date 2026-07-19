# Azure Container Apps Order API Practical

## Objective
Deploy the Python Order API to Azure Container Apps using Azure Portal for resource creation and configuration.

## Files to keep
- `app.py`: application source code provided by developer.
- `Dockerfile`: container build instructions provided by developer.
- `requirements.txt`: Python dependencies provided by developer.

## Resources to create manually in Azure Portal
Use your own names, but keep names simple and consistent.

1. Resource Group
   - Example: `rg-aca-training-megha`
   - Region: choose one region and use the same region for all resources, for example `Central India`.

2. Azure Container Registry
   - Example: `acrtrainingmegha001`
   - SKU: `Basic`
   - Admin user: enable only for this training demo if you want simple portal-based deployment.

3. Log Analytics Workspace
   - Example: `law-aca-training-megha`
   - Use the same resource group and region.

4. Container Apps Environment
   - Example: `cae-training-megha`
   - Connect it with the Log Analytics Workspace.

5. Azure Container App
   - Example: `aca-order-api-megha`
   - Image: use image pushed to Azure Container Registry.
   - Ingress: enabled, external.
   - Target port: `8080`.
   - Environment variables:
     - `APP_ENV=training`
     - `APP_VERSION=v1`
   - Scale:
     - Minimum replicas: `1`
     - Maximum replicas: `3`
   - CPU/Memory:
     - CPU: `0.5`
     - Memory: `1Gi`

## Build and push image
The resources are created manually in the portal. For container image build/push, use one of these options:

Option A: ACR Task from Azure CLI
```powershell
az login
az account set --subscription "<subscription-id-or-name>"
az acr build --registry <acr-name> --image aca-order-api:v1 .
```

Option B: Local Docker
```powershell
docker build -t <acr-name>.azurecr.io/aca-order-api:v1 .
az acr login --name <acr-name>
docker push <acr-name>.azurecr.io/aca-order-api:v1
```

## Validate
Open the Container App overview page and copy the Application URL.

Test these URLs in browser:
```text
https://<container-app-url>/
https://<container-app-url>/health
https://<container-app-url>/api/orders
```

Expected result:
- `/` returns application name, version, environment and hostname.
- `/health` returns `healthy`.
- `/api/orders` returns demo order data.

## Test POST request
Use PowerShell:
```powershell
$body = @{ customer = "Training User"; product = "Azure Course" } | ConvertTo-Json
Invoke-RestMethod -Uri "https://<container-app-url>/api/orders" -Method Post -ContentType "application/json" -Body $body
```

## Deploy revision v2
Build a second image:
```powershell
az acr build --registry <acr-name> --image aca-order-api:v2 .
```

In Azure Portal:
1. Go to Container App.
2. Open `Containers`.
3. Edit and change image tag from `v1` to `v2`.
4. Update environment variable `APP_VERSION=v2`.
5. Save and create a new revision.
6. Check `Revisions and replicas` and confirm the new revision is running.

## Explanation points for training
- Resource Group keeps all practical resources together.
- Azure Container Registry stores the Docker image.
- Dockerfile packages the Python Flask API into a container.
- Container Apps Environment is the hosting boundary for one or more container apps.
- Log Analytics stores logs and helps troubleshooting.
- Ingress exposes the API publicly.
- Target port `8080` must match the port used by the app and Dockerfile.
- Revisions allow you to deploy a new version without recreating the whole app.
- Scaling settings control minimum and maximum running replicas.

## Cleanup
After practical completion, delete the Resource Group from Azure Portal to remove all created resources.
