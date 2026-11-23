# WeatherCompare

**Interview portfolio project** demonstrating the core stack for the Sr. Software Engineer role (Randstad / Cotiviti).

**Live demo:** https://main.d1ieds2fabqqg7.amplifyapp.com/  
**Repo:** https://github.com/larryhill23420/WeatherCompare

---

## Job Description

Strong AWS experience is a must (make sure you are able to speak on this at any range :) )

**Core stack:**

- Strong AWS experience: EKS, EMR, OpenSearch, and DocumentDB
- Containers: Docker, and running services on Kubernetes
- Spark / PySpark and Kafka (event-driven processing)
- Java / Spring Boot
- SQL Server and MongoDB / Amazon DocumentDB
- React
- REST API integration
- Exposure to infrastructure as code (Terraform)

**Strong AI-native habits:**

- Uses AI coding assistants such as Claude Code every day
- Writes clear prompts and gives the assistant good context
- Works from the team's shared skills and knowledge bases

**Approximate skill breakdown:**

- AWS (EKS, EMR, OpenSearch, and general cloud services): 35%
- Spark / PySpark and Kafka (event-driven): 30%
- Java / Spring Boot, React, and databases (DocumentDB, SQL Server): 35%

---

## Day-by-Day Build Summary

**Friday, Nov 20 (Day 1)**  

Mapped 20+ years of SQL experience to AWS for the interview. 
Designed and created the first DynamoDB table. 
Built the initial Python weather ingest script. 
Dockerized the pipeline. 
Added Kafka producer + consumer with Docker Compose. 
Got hourly data flowing into DynamoDB. 
Set up the GitHub repo and a basic GitHub Pages site. 
Started Lambda Function URL work.

**Saturday, Nov 21 (Day 2)**  

Redesigned tables (ZipCode, Reading, Error) with proper keys and denormalization. 
Wrote the full backfill script with error handling and EXISTS checks. 
Updated Kafka producer/consumer for the new schema. 
Built the compare Lambda (local-time alignment, days parameter, differences). 
Built add-zip and list-zips Lambdas. 
Created the interactive HTML UI (dropdowns, add zip, compare, summary). 
Fixed CORS, timeouts, and import issues. 
Added TimeZone support. 
Moved ingest to Kubernetes (kind + manifests). 
Added Terraform for the tables + `rebuild.ps1`. 
Confirmed end-to-end flow.

**Sunday, Nov 22 (Day 3)**  

Rebuilt tables with TimeZone via Terraform. 
Converted the UI to a real React (Vite) app. 
Added Add Zip modal + improved styling. 
Deployed the React app to AWS Amplify. 
Wrote the initial JD-to-code mapping. 
Discussed DocumentDB/OpenSearch design notes.

**Monday, Nov 23 (Day 4)**  

Added a minimal Spring Boot service that proxies the compare endpoint (calls the existing Lambda Function URL and returns JSON). 
Demonstrates Java / Spring Boot REST integration in front of the Python/Lambda pipeline.
Ingest was not running over night. Create Event Bridge in AWS to run at the top of each hour.

---

## JD Checklist → Location in Repo

| JD Requirement | Location in Repo | Notes |
| --- | --- | --- |
| **AWS (EKS / general cloud)** | `k8s/producer-deployment.yaml`<br>`k8s/consumer-deployment.yaml` | Same manifests validated locally with kind; ready for EKS. |
| **Docker** | `Dockerfile`<br>`docker-compose.yml` | Multi-stage capable; used by Compose and Kubernetes. |
| **Kubernetes** | `k8s/` | Producer and consumer Deployments. |
| **Kafka (event-driven)** | `producer.py`<br>`consumer.py`<br>`docker-compose.yml` | Producer publishes hourly readings; consumer writes to DynamoDB. |
| **PySpark / Spark** | `lambda_function.py` (compare) | Aggregation logic (avg/high/low temp, total precip, avg cloud) written in the style of a Spark job. |
| **Java / Spring Boot** | `spring-boot-service/` | Minimal Spring Boot app (`DemoApplication.java`) that proxies the compare Lambda. |
| **Databases (DynamoDB / DocumentDB-style)** | `terraform/main.tf`<br>`Table_Defs.txt` | Schemaless document model (ZipCode, Reading, Error). Terraform creates the tables. |
| **React** | `react-ui/` | Vite + React frontend. Modal form, dynamic dropdowns, summary + detail table. Deployed on Amplify. |
| **REST API integration** | `lambda_function.py`<br>`spring-boot-service/`<br>Function URLs | Compare, add-zip, and list-zips endpoints. Called by React and by the Spring Boot service. |
| **Terraform (IaC)** | `terraform/main.tf`<br>`rebuild.ps1` | Creates DynamoDB tables. `rebuild.ps1` does destroy/apply + data reload. |
| **AI-native workflow** | Entire project | Built iteratively with Grok: clear prompts, shared context, rapid feedback, and progressive refinement. |

---

## Architecture (short)

1. **Ingest**: Kafka producer (hourly) → Kafka → consumer → DynamoDB Reading table  
2. **Zip management**: React modal → add-zip Lambda → Zippopotam + Open-Meteo → DynamoDB  
3. **Query**: React UI → compare Lambda → returns 7-day summary + hourly rows aligned to local time  
4. **Java layer**: Spring Boot service (`/compare`) proxies the same Lambda endpoint  
5. **Infra**: Terraform for tables; Kubernetes manifests for the ingest services; Amplify for the React frontend  

---

## Key Folders

- `react-ui/` — Vite + React frontend  
- `k8s/` — Kubernetes Deployments for producer & consumer  
- `terraform/` — DynamoDB table definitions  
- `spring-boot-service/` — Java / Spring Boot proxy  
- Root Python scripts — data loading, nuke/rebuild helpers, Lambda code  

---

## Local Development

```bash
# React UI
cd react-ui
npm install
npm run dev

# Rebuild DynamoDB tables + reload data
./rebuild.ps1

# Spring Boot service
cd spring-boot-service
./mvnw spring-boot:run -Dspring-boot.run.fork=false
# Then open: http://localhost:8080/compare?zip1=98593&zip2=19422&days=1