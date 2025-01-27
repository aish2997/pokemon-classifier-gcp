# Image-Classifier-GCP

This repository provides a sample implementation of an end-to-end image classification pipeline on Google Cloud Platform (GCP). It includes the following components:

1. **A Cloud Run service that:**
   - Accepts an image file through a POST request.
   - Preprocesses the image and predicts its class using the MobileNetV3Small model.

2. **A Cloud Function service that:**
   - Processes images in a Google Cloud Storage (GCS) bucket.
   - Stores classification results in a BigQuery table.
   - Handles images in batch mode for processing.

3. **A Cloud Scheduler configured to trigger the pipeline daily, enabling batch processing of images that land in the GCS bucket.**

## Prerequisites

1. A Google Cloud Project with billing enabled.
2. The gcloud CLI installed and authenticated.
3. Necessary IAM permissions for managing Workload Identity Pools, Cloud Run, GCS, BigQuery, and Cloud Scheduler.
4. A GitHub repository to integrate GitHub Actions with GCP.

## 1. Setting Up Workload Identity Pool and Provider

### Step 1: Export Project ID and Create the Workload Identity Pool

Run the following commands to create a Workload Identity Pool:

```bash
export PROJECT_ID="YOUR_PROJECT_ID"

gcloud iam workload-identity-pools create github-actions-pool \
  --project="$PROJECT_ID" \
  --location="global" \
  --display-name="GitHub Actions Pool"
```

### Step 2: Create the Workload Identity Pool Provider

Create an OIDC provider that links GitHub Actions with the Workload Identity Pool:

```bash
gcloud iam workload-identity-pools providers create-oidc github-actions-provider \
  --workload-identity-pool="github-actions-pool" \
  --project="$PROJECT_ID" \
  --location="global" \
  --display-name="GitHub Actions Provider" \
  --issuer-uri="https://token.actions.githubusercontent.com" \
  --attribute-mapping="attribute.aud=assertion.aud,attribute.actor=assertion.actor,attribute.repository=assertion.repository,google.subject=assertion.sub" \
  --attribute-condition="attribute.repository=='aish2997/blog-website'"
```

### Explanation of Commands

1. **Workload Identity Pool:**
   - `github-actions-pool`: Name of the pool.
   - Replace `YOUR_PROJECT_ID` with your GCP project ID.

2. **OIDC Provider:**
   - Links GitHub Actions to GCP using OpenID Connect (OIDC).
   - Maps attributes like repository, aud, and actor to GCP attributes.
   - Restricts authentication to the repository `aish2997/blog-website`.

### Verification

Verify the Workload Identity Pool and Provider setup:

```bash
gcloud iam workload-identity-pools describe github-actions-pool \
  --project="$PROJECT_ID" \
  --location="global"

gcloud iam workload-identity-pools providers describe github-actions-provider \
  --workload-identity-pool="github-actions-pool" \
  --project="$PROJECT_ID" \
  --location="global"
```

## 2. Setting Up the GitHub Actions Service Account

### Step 1: Export Project Name and Create the Service Account

Create a service account for GitHub Actions:

```bash
export PROJECT_NAME="YOUR_PROJECT_NAME"

gcloud iam service-accounts create github-actions-sa \
  --description="GitHub Actions Service Account" \
  --display-name="GitHub Actions SA" \
  --project="$PROJECT_NAME"
```

### Step 2: Assign Roles to the Service Account

Assign necessary IAM roles to the service account:

```bash
export SA_EMAIL="github-actions-sa@$PROJECT_NAME.iam.gserviceaccount.com"
export PROJECT_NUMBER=$(gcloud projects describe $PROJECT_NAME --format="value(projectNumber)")
export POOL_NAME="github-actions-pool"
export GITHUB_REPO="aish2997/blog-website"

# DNS Administrator
gcloud projects add-iam-policy-binding "$PROJECT_NAME" \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/dns.admin"

# Service Account Token Creator
gcloud projects add-iam-policy-binding "$PROJECT_NAME" \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/iam.serviceAccountTokenCreator"

# Storage Admin
gcloud projects add-iam-policy-binding "$PROJECT_NAME" \
  --member="serviceAccount:$SA_EMAIL" \
  --role="roles/storage.admin"

# Workload Identity User
gcloud iam service-accounts add-iam-policy-binding "$SA_EMAIL" \
  --member="principalSet://iam.googleapis.com/projects/$PROJECT_NUMBER/locations/global/workloadIdentityPools/$POOL_NAME/attribute.repository/$GITHUB_REPO" \
  --role="roles/iam.workloadIdentityUser "
```

### Verification

Verify the roles assigned to the service account:

```bash
gcloud projects get-iam-policy "$PROJECT_NAME" \
  --flatten="bindings[].members" \
  --filter="bindings.members:$SA_EMAIL" \
  --format="table(bindings.role)"
```

## 3. Setting Up the Terraform State File Bucket in GCS

Create a GCS bucket to store Terraform state files:

```bash
export STATE_BUCKET="$PROJECT_NAME-state"

gcloud storage buckets create "gs://$STATE_BUCKET" \
  --project="$PROJECT_NAME" \
  --location="eu" \
  --default-storage-class="STANDARD" \
  --uniform-bucket-level-access
```

## 4. Deploying the Code

After completing the above steps, deploy the code using GitHub Actions from the develop branch.

## 5. Project Workflow Summary

1. **Cloud Run:**
   - Accepts image files via a REST API.
   - Preprocesses the images and predicts their classes using MobileNetV3Small.

2. **Cloud Function:**
   - Processes images stored in the `incoming/` directory of the GCS bucket.
   - Sends images to the Cloud Run API for classification.
   - Logs classification results to a BigQuery table.
   - Moves processed files to `archive/` or `error/` directories in the GCS bucket.

3. **Cloud Scheduler:**
   - Triggers the Cloud Function daily to batch process new images.