# Deploy to Google Cloud Run

# Stop on first error
$ErrorActionPreference = "Stop"

Write-Host "Checking gcloud configuration..."
$PROJECT_ID = gcloud config get-value project
if (-not $PROJECT_ID) {
    Write-Error "No Google Cloud Project ID found. Please run 'gcloud init' or 'gcloud config set project YOUR_PROJECT_ID'."
}

Write-Host "Deploying to Project: $PROJECT_ID"

# 1. Enable Services
Write-Host "Enabling necessary Google Cloud services..."
gcloud services enable cloudbuild.googleapis.com run.googleapis.com containerregistry.googleapis.com

# 2. Build Images
Write-Host "Building Docker images with Cloud Build..."
gcloud builds submit --config cloudbuild.yaml .

# 3. Deploy Backend
Write-Host "Deploying Backend..."
gcloud run deploy finance-ai-backend `
    --image gcr.io/$PROJECT_ID/finance-ai-backend `
    --platform managed `
    --region us-central1 `
    --allow-unauthenticated `
    --set-env-vars "FRONTEND_URL=https://finance-ai-frontend-uc.a.run.app" 
    # Note: FRONTEND_URL is set tentatively; we might need to update it after frontend deploy if URL changes, 
    # but initially we can't know it. We can redeploy backend later or just use "*" for CORS in dev/mvp.

# Get Backend URL
$BACKEND_URL_RAW = gcloud run services describe finance-ai-backend --platform managed --region us-central1 --format "value(status.url)"
$BACKEND_URL = $BACKEND_URL_RAW.Trim()
Write-Host "Backend deployed at: $BACKEND_URL"

# 4. Deploy Frontend
Write-Host "Deploying Frontend..."
gcloud run deploy finance-ai-frontend `
    --image gcr.io/$PROJECT_ID/finance-ai-frontend `
    --platform managed `
    --region us-central1 `
    --allow-unauthenticated `
    --set-env-vars "NEXT_PUBLIC_API_URL=$BACKEND_URL/api"

$FRONTEND_URL_RAW = gcloud run services describe finance-ai-frontend --platform managed --region us-central1 --format "value(status.url)"
$FRONTEND_URL = $FRONTEND_URL_RAW.Trim()

Write-Host "--------------------------------------------------"
Write-Host "Deployment Complete!"
Write-Host "Frontend: $FRONTEND_URL"
Write-Host "Backend:  $BACKEND_URL"
Write-Host "--------------------------------------------------"

# 5. Update Backend with correct Frontend URL for CORS (Optional but recommended)
Write-Host "Updating Backend CORS with actual Frontend URL..."
gcloud run deploy finance-ai-backend `
    --image gcr.io/$PROJECT_ID/finance-ai-backend `
    --platform managed `
    --region us-central1 `
    --set-env-vars "FRONTEND_URL=$FRONTEND_URL" `
    --quiet

Write-Host "Backend updated with Frontend URL."
