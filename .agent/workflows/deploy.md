---
description: Deploy the application to Google Cloud Run
---

# Deploy to Google Cloud Run

Deploy the backend and frontend to GCP Cloud Run.

## Prerequisites

- `gcloud` CLI installed and authenticated (`gcloud auth login`)
- GCP project created with billing enabled
- Cloud Run API enabled (`gcloud services enable run.googleapis.com`)
- Artifact Registry repo created for Docker images

## Backend Deployment

1. Set your GCP project:
```
gcloud config set project <YOUR_GCP_PROJECT_ID>
```

2. Build and push the backend Docker image:
```
gcloud builds submit --tag gcr.io/<YOUR_GCP_PROJECT_ID>/finance-ai-backend ./backend
```
Cwd: `c:\Users\Priyatanshu Ghosh\Desktop\AI Projects\Finance AI SaaS`

3. Deploy to Cloud Run:
```
gcloud run deploy finance-ai-backend --image gcr.io/<YOUR_GCP_PROJECT_ID>/finance-ai-backend --platform managed --region us-central1 --allow-unauthenticated --set-env-vars "ANTHROPIC_API_KEY=<key>,SUPABASE_URL=<url>,SUPABASE_ANON_KEY=<key>,SUPABASE_SERVICE_ROLE_KEY=<key>"
```

4. Note the deployed URL from the output.

## Frontend Deployment

1. Update `NEXT_PUBLIC_API_URL` in the frontend build to point to the deployed backend URL.

2. Build and push the frontend Docker image:
```
gcloud builds submit --tag gcr.io/<YOUR_GCP_PROJECT_ID>/finance-ai-frontend ./frontend
```
Cwd: `c:\Users\Priyatanshu Ghosh\Desktop\AI Projects\Finance AI SaaS`

3. Deploy to Cloud Run:
```
gcloud run deploy finance-ai-frontend --image gcr.io/<YOUR_GCP_PROJECT_ID>/finance-ai-frontend --platform managed --region us-central1 --allow-unauthenticated --set-env-vars "NEXT_PUBLIC_API_URL=<backend_url>"
```

## Verify

- Backend health: `curl https://<backend-url>/health`
- Frontend: Open the frontend URL in a browser
- API docs: `https://<backend-url>/docs`

## Custom Domain (Optional)

```
gcloud run domain-mappings create --service finance-ai-frontend --domain <your-domain> --region us-central1
```

## Secrets Management

For production, use GCP Secret Manager instead of inline env vars:
```
gcloud secrets create ANTHROPIC_API_KEY --data-file=- <<< "your-key"
gcloud run services update finance-ai-backend --set-secrets="ANTHROPIC_API_KEY=ANTHROPIC_API_KEY:latest"
```
