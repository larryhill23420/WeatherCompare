# Weather Compare

A small event-driven weather comparison system built to demonstrate AWS, Kubernetes, Kafka, React, and related skills.

Live demo: https://main.d1ieds2fabqqg7.amplifyapp.com/
GitHub repo: https://github.com/larryhill23420/WeatherCompare

## Job Description Mapping

| JD Requirement              | Where it lives in this project                          | Notes |
|-----------------------------|---------------------------------------------------------|-------|
| **AWS EKS / Kubernetes**    | `k8s/producer-deployment.yaml`, `k8s/consumer-deployment.yaml` | Validated locally with kind. Same manifests deploy to EKS. |
| **Docker**                  | `Dockerfile`, `docker-compose.yml`                      | Multi-stage capable; used by both Compose and Kubernetes. |
| **Kafka (event-driven)**    | `producer.py`, `consumer.py`                            | Producer publishes hourly readings; consumer writes to DynamoDB. |
| **DynamoDB (DocumentDB-style NoSQL)** | Tables: `ZipCode`, `Reading`, `Error`              | Schemaless document model. Terraform in `terraform/main.tf`. |
| **REST APIs**               | Lambda Function URLs (compare, add-zip, list-zips)      | Called by the React frontend. |
| **React**                   | `react-ui/` (Vite + React)                              | Deployed on Amplify. Modal form, dynamic dropdowns, summary + detail table. |
| **Terraform (IaC)**         | `terraform/main.tf`                                     | Creates the three DynamoDB tables. `rebuild.ps1` does destroy/apply + reload. |
| **AWS Lambda**              | Compare, add-zip, and list-zips functions               | Python 3.12, Function URLs, least-privilege IAM. |
| **PySpark / Spark**         | Summary logic in the compare Lambda                     | Equivalent aggregation (avg/high/low temp, total precip, avg cloud). |
| **AI-native workflow**      | Entire project                                          | Built iteratively with Grok; clear prompts, context, and rapid feedback loops. |

## Architecture (short)

1. **Ingest**: Kafka producer (hourly) → Kafka → consumer → DynamoDB `Reading` table  
2. **Zip management**: React modal → add-zip Lambda → Zippopotam + Open-Meteo → DynamoDB  
3. **Query**: React UI → compare Lambda → returns 7-day summary + hourly rows aligned to local time  
4. **Infra**: Terraform for tables; Kubernetes manifests for the ingest services; Amplify for the React frontend

## Key folders

- `react-ui/` — Vite + React frontend  
- `k8s/` — Kubernetes Deployments for producer & consumer  
- `terraform/` — DynamoDB table definitions  
- Root Python scripts — data loading, nuke/rebuild helpers  

## Local development

```bash
# React UI
cd react-ui
npm install
npm run dev

# Rebuild DynamoDB tables + reload data
./rebuild.ps1

Day-by-Day Breakdown

Friday, Nov 20 (Day 1)

Mapped SQL experience to AWS for the interview
Designed and created the first DynamoDB table
Built the initial Python weather ingest
Dockerized the pipeline
Added Kafka producer + consumer (Docker Compose)
Got hourly data flowing into DynamoDB
Set up GitHub repo and basic GitHub Pages site
Started Lambda Function URL work

Saturday, Nov 21 (Day 2)

Redesigned tables (ZipCode, Reading, Error)
Wrote full backfill script with error handling and EXISTS checks
Updated Kafka producer/consumer for the new schema
Built compare Lambda (local-time alignment, days parameter, differences)
Built add-zip and list-zips Lambdas
Created the interactive HTML UI (dropdowns, add zip, compare, summary)
Fixed CORS, timeouts, and import issues
Added TimeZone support and removed hard-coded offsets
Moved ingest to Kubernetes (kind + manifests)
Added Terraform for the tables + rebuild.ps1
Confirmed end-to-end flow

Sunday, Nov 22 (Day 3)

Rebuilt tables with TimeZone via Terraform
Converted the UI to a real React (Vite) app
Added Add Zip modal + improved styling
Deployed the React app to AWS Amplify
Wrote the JD-to-code README mapping
(Optional) DocumentDB/OpenSearch design notes discussed
