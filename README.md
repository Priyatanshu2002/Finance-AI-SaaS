
# Finance AI SaaS

Automated Financial Data Extraction engine powered by Claude Opus 4.6 and Gemini 1.5 Pro.

## Deployment to Google Cloud Run

**Prerequisites:**
1.  Verify Google Cloud SDK is installed: `gcloud --version`
2.  Login: `gcloud auth login`
3.  Set Project: `gcloud config set project YOUR_PROJECT_ID`

**Deploy:**
Run the deployment script from the project root (PowerShell):
```powershell
./deploy_cloud_run.ps1
```

This script will:
1.  Enable required GCP services (Cloud Build, Cloud Run).
2.  Build Docker images for Backend and Frontend.
3.  Push images to Google Container Registry (GCR).
4.  Deploy services to Cloud Run (fully managed).
5.  Link the services (Backend knows Frontend URL, Frontend knows Backend URL).

**Manual Build (if script fails):**
```bash
gcloud builds submit --config cloudbuild.yaml .
```
