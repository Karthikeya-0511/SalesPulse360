# SalesPulse360 – Enterprise Cloud Analytics Platform

SalesPulse360 is an end-to-end cloud analytics project that demonstrates how historical sales data can be ingested, transformed and visualized through a modern analytics pipeline.

The project simulates a real enterprise workflow by integrating Python, AWS S3, Snowpipe, Snowflake, SQL, FastAPI, React and Power BI into a single cloud-native analytics solution.

---

## Project Overview

SalesPulse360 was built to demonstrate the complete lifecycle of an analytics platform, starting from data generation through to executive reporting.

The project simulates historical sales events, stores them in cloud storage, automatically ingests them into a Snowflake data warehouse, transforms the data into analytics-ready tables, exposes business metrics through REST APIs, and visualizes the results using an embedded Power BI dashboard.

Unlike standalone dashboard projects, SalesPulse360 focuses on the complete engineering workflow behind enterprise analytics.

---

# Business Problem

Many organizations face common analytics challenges:

- Business data exists across multiple operational systems.
- Manual reporting causes delays in decision making.
- Data pipelines are difficult to monitor.
- Business users lack a centralized reporting platform.
- Dashboard data is often outdated due to manual refresh processes.

SalesPulse360 demonstrates how these challenges can be addressed using a cloud-native analytics architecture.

---

# Solution Architecture

```
                    Python Generator
                           │
                           ▼
                    AWS S3 Landing Zone
                           │
                           ▼
                  Snowpipe Auto Ingestion
                           │
                           ▼
                Snowflake Data Warehouse
                           │
                           ▼
                SQL Data Transformations
                           │
                           ▼
                   Analytics Data Model
                           │
                           ▼
                     FastAPI Backend
                           │
                           ▼
                React Executive Portal
                           │
                           ▼
                  Embedded Power BI Report
```

---

# Technology Stack

| Category | Technology |
|-----------|------------|
| Programming Language | Python |
| Cloud Storage | AWS S3 |
| Data Warehouse | Snowflake |
| Continuous Ingestion | Snowpipe |
| Data Transformation | Snowflake SQL |
| Backend API | FastAPI |
| Frontend | React + TypeScript |
| Data Visualization | Power BI |
| Styling | Tailwind CSS |
| API Communication | Axios |

---

# Project Workflow

### 1. Data Generation

A Python replay engine simulates historical sales events by generating sales batches at configurable intervals.

### 2. Cloud Storage

Generated CSV files are uploaded to AWS S3, which acts as the landing zone.

### 3. Automatic Ingestion

Snowpipe continuously monitors the S3 bucket and automatically loads new files into the RAW schema inside Snowflake.

### 4. Data Transformation

Snowflake SQL transforms the RAW tables into structured analytics tables using staging and analytics schemas.

### 5. REST API Layer

FastAPI exposes business metrics, pipeline status and dashboard information through REST endpoints.

### 6. Executive Portal

The React application retrieves live information from the backend APIs and presents infrastructure status together with business KPIs.

### 7. Business Intelligence

Power BI connects to the analytics schema and provides interactive dashboards embedded within the Executive Analytics Portal.

---

# Features

### Cloud Analytics Pipeline

- Historical sales replay generator
- Batch-based event simulation
- AWS S3 cloud storage
- Automatic Snowpipe ingestion
- Snowflake data warehouse
- SQL transformation layer
- Analytics-ready data model

### Executive Portal

- Executive KPI dashboard
- Pipeline monitoring
- Architecture visualization
- Technology stack overview
- Embedded Power BI dashboard
- Business insights
- Manual pipeline refresh

### Power BI Dashboard

The embedded report contains multiple analytical pages:

- Executive Overview
- Sales Trends
- Product Performance
- Regional Analysis
- Customer Analysis
- Operations Dashboard

---

# Backend APIs

| Endpoint | Description |
|----------|-------------|
| `/api/kpis` | Executive KPI metrics |
| `/api/status` | Infrastructure health |
| `/api/pipeline` | Pipeline monitoring |
| `/api/insights` | Executive business insights |
| `/api/powerbi` | Power BI report information |

---

# Key Performance Indicators

The platform reports the following business metrics:

- Total Revenue
- Total Orders
- Total Profit
- Average Profit Margin
- Average Delivery Days
- Total Customers
- Total Products
- Regional Performance

---

# Project Structure

```
SalesPulse360
│
├── backend
│   ├── generator
│   ├── models
│   ├── routers
│   ├── services
│   ├── utils
│   ├── app.py
│   └── database.py
│
├── src
│   ├── api
│   ├── assets
│   ├── components
│   ├── hooks
│   ├── routes
│   └── styles
│
├── package.json
├── requirements.txt
└── README.md
```

---

# Running the Project

## Backend

```bash
cd backend

pip install -r requirements.txt

uvicorn app:app --reload
```

Backend URL

```
http://localhost:8000
```

---

## Frontend

```bash
npm install

npm run dev
```

Frontend URL

```
http://localhost:5173
```

---

# Dashboard Preview

The repository includes screenshots for:

- Executive Dashboard
- Sales Trends
- Products
- Regions
- Customers
- Operations

located inside:

```
src/assets/
```

---

# Learning Outcomes

This project demonstrates practical implementation of:

- Cloud Analytics Architecture
- Data Warehousing
- ETL Pipeline Design
- Snowflake
- AWS S3
- Snowpipe
- SQL Data Transformation
- REST API Development
- React Integration
- Power BI Embedding

---

# Future Enhancements

Possible improvements include:

- Apache Kafka streaming
- Apache Airflow orchestration
- Docker containerization
- CI/CD deployment
- Cloud deployment
- User authentication
- Automated scheduling
- Monitoring and alerting

---

# Author

**Karthikeya Sriramoju**

Aspiring Data Analyst

Skills:

- SQL
- Python
- Power BI
- Snowflake
- AWS S3
- FastAPI
- React
- Data Analytics

GitHub:

https://github.com/<YOUR_GITHUB_USERNAME>

---

# License

This project was developed for learning purposes, portfolio demonstration and technical interviews.