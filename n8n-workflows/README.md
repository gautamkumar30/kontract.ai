# n8n Workflows

This directory contains n8n workflow definitions that can be imported into your n8n instance.

## Workflows

1. **01-contract-ingest.json** - Contract ingestion workflow
2. **02-text-extraction.json** - Text extraction workflow
3. **03-clause-segmentation.json** - Clause segmentation workflow
4. **04-fingerprint-generation.json** - Fingerprint generation workflow
5. **05-drift-detection.json** - Drift detection workflow
6. **06-risk-scoring.json** - Risk scoring workflow
7. **07-alert-dispatch.json** - Alert dispatch workflow

## How to Import

1. Access your n8n instance at http://localhost:5678
2. Login with credentials (admin/admin123)
3. Go to **Workflows** → **Import from File**
4. Select each JSON file and import
5. Activate the workflows

## Workflow Development

These workflows will be created as the backend API endpoints are finalized.
The workflows orchestrate the document processing pipeline and integrate with the backend API.
