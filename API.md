# ClaimLens 2.0 - API Documentation

## Overview

ClaimLens 2.0 API provides endpoints for creating investigations, fetching results, and retrieving evidence reports.

## Base URLs

- **Development**: `http://localhost:8000`
- **Production**: `https://your-backend.com`

## Authentication

Currently public (will add API keys in future versions).

## Endpoints

### Health & Status

#### Health Check

```
GET /health
```

Response:
```json
{
  "status": "ok",
  "service": "ClaimLens 2.0"
}
```

---

### Investigations

#### List Investigations

```
GET /api/v1/investigations?status=completed&limit=10&offset=0
```

**Query Parameters**:
- `status` (string, optional): Filter by status (`draft`, `running`, `completed`, `failed`)
- `source_type` (string, optional): Filter by source type
- `limit` (integer, default: 20): Number of results
- `offset` (integer, default: 0): Pagination offset

**Response**:
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Verify startup metrics",
    "description": "Company claims 50k users",
    "source_type": "text",
    "status": "completed",
    "workflow_status": "completed",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:35:00Z"
  }
]
```

---

#### Create Investigation

```
POST /api/v1/investigations
Content-Type: application/json
```

**Request Body**:
```json
{
  "title": "Verify startup metrics claim",
  "description": "The company has 50,000 active users and grew 180% YoY",
  "source_type": "text",
  "status": "draft"
}
```

**Response** (201 Created):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Verify startup metrics claim",
  "description": "The company has 50,000 active users and grew 180% YoY",
  "source_type": "text",
  "status": "running",
  "workflow_status": "running",
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

---

#### Get Investigation

```
GET /api/v1/investigations/{investigation_id}
```

**Path Parameters**:
- `investigation_id` (UUID): Investigation ID

**Response**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Verify startup metrics claim",
  "description": "The company has 50,000 active users and grew 180% YoY",
  "source_type": "text",
  "status": "completed",
  "workflow_status": "completed",
  "final_verdict": {
    "label": "mixed",
    "confidence": 0.68,
    "uncertainty": 0.42,
    "explanation": "Partially supported by evidence..."
  },
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:35:00Z"
}
```

**Status Codes**:
- `200 OK`: Investigation found
- `404 Not Found`: Investigation not found

---

#### Run Investigation

```
POST /api/v1/investigations/{investigation_id}/run
```

**Path Parameters**:
- `investigation_id` (UUID): Investigation ID

**Response** (200 OK):
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "running",
  "workflow_status": "running"
}
```

---

### Reports

#### Get Report

```
GET /api/v1/reports/{investigation_id}
```

**Path Parameters**:
- `investigation_id` (UUID): Investigation ID

**Response**:
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Startup metrics verification report",
  "status": "completed",
  "claim_text": "The company has 50,000 active users",
  "summary": "This claim is supported by multiple independent sources...",
  "verdict": {
    "label": "true",
    "confidence": 0.85,
    "uncertainty": 0.15,
    "explanation": "Multiple sources confirm the claim",
    "review_required": false
  },
  "sources": [
    {
      "id": "src-1",
      "title": "Company annual report",
      "url": "https://example.com/report",
      "publisher": "Company",
      "source_type": "primary",
      "quality_score": 0.85,
      "relevance_score": 0.92
    }
  ],
  "evidence": [
    {
      "id": "ev-1",
      "claim_id": "claim-1",
      "source_id": "src-1",
      "text": "The company reported 50,000 active users...",
      "type": "supporting",
      "relevance_score": 0.94,
      "confidence": 0.88
    }
  ],
  "conflicts": [],
  "graph": {
    "nodes": [...],
    "edges": [...]
  }
}
```

**Status Codes**:
- `200 OK`: Report available
- `404 Not Found`: Investigation/report not found
- `501 Not Implemented`: Report generation not yet complete

---

#### Export Report

```
GET /api/v1/reports/{investigation_id}/export?format=pdf
```

**Query Parameters**:
- `format` (string, default: `pdf`): Export format (`pdf`, `html`, `json`)

**Response**: File download or `application/json`

---

## Error Responses

### 400 Bad Request

```json
{
  "detail": "Invalid request payload",
  "code": "invalid_request"
}
```

### 404 Not Found

```json
{
  "detail": "Investigation not found",
  "code": "not_found"
}
```

### 500 Internal Server Error

```json
{
  "detail": "Internal server error",
  "code": "internal_error"
}
```

---

## Data Types

### Investigation Status
- `draft` - Investigation created but not started
- `running` - Workflow currently executing
- `completed` - Workflow finished successfully
- `failed` - Workflow encountered an error

### Verdict Labels
- `true` - Claim is supported by evidence
- `false` - Claim is contradicted by evidence
- `mixed` - Conflicting evidence
- `unverified` - Insufficient evidence

### Evidence Types
- `supporting` - Evidence supports the claim
- `contradicting` - Evidence contradicts the claim
- `neutral` - Neutral or tangential information

### Source Types
- `primary` - Original source (e.g., official report)
- `secondary` - Analysis of primary source
- `news` - News article or blog post
- `academic` - Academic research or paper

---

## Rate Limiting

Currently unlimited (will be implemented in production).

Future:
- 100 requests/minute for unauthenticated users
- 1000 requests/minute for authenticated users

---

## Examples

### JavaScript/TypeScript

```typescript
import { apiRequest } from '@/lib/api';

// Create investigation
const investigation = await apiRequest('/api/v1/investigations', {
  method: 'POST',
  body: JSON.stringify({
    title: 'Verify claim',
    description: 'Test claim text',
    source_type: 'text',
  }),
});

// Poll for status
const poll = async (id: string) => {
  let status = 'running';
  while (status === 'running') {
    const result = await apiRequest(`/api/v1/investigations/${id}`);
    status = result.status;
    if (status === 'running') {
      await new Promise((resolve) => setTimeout(resolve, 2000));
    }
  }
  return result;
};

// Get report
const report = await apiRequest(`/api/v1/reports/${investigation.id}`);
```

### Python

```python
import requests
import time

BASE_URL = 'http://localhost:8000'

# Create investigation
response = requests.post(
    f'{BASE_URL}/api/v1/investigations',
    json={
        'title': 'Verify claim',
        'description': 'Test claim text',
        'source_type': 'text',
    }
)
investigation = response.json()

# Poll for status
while True:
    result = requests.get(f'{BASE_URL}/api/v1/investigations/{investigation["id"]}').json()
    if result['status'] != 'running':
        break
    time.sleep(2)

# Get report
report = requests.get(f'{BASE_URL}/api/v1/reports/{investigation["id"]}').json()
print(report)
```

---

## Changelog

### v0.1.0 (2024-01-15)
- Initial API release
- Investigations endpoint
- Reports endpoint (with mock data)
- Health check endpoint
