---
description: Generate conventional commit message from staged changes
---

# Generate Git Commit Message

This workflow analyzes your staged Git changes and generates a commit message following the project's Conventional Commits format.

## Prerequisites

- Changes must be staged (`git add` files first)
- Working in a Git repository

## Steps

### 1. Check Staged Changes

// turbo
```bash
git status --short
git diff --staged --stat
```

### 2. Read Full Diff

// turbo
```bash
git diff --staged
```

### 3. Analyze and Generate Commit Message

Based on the diff, generate a commit message following this **EXACT** format:

```
<type>(<scope>): <subject>

<body>

<footer>
```

#### **Type** (Required)
Choose ONE:
- `feat` - New feature
- `fix` - Bug fix
- `refactor` - Code restructuring (no behavior change)
- `perf` - Performance improvement
- `test` - Adding/updating tests
- `chore` - Tooling, config, dependencies
- `docs` - Documentation only

#### **Scope** (REQUIRED - MUST be present)
Component or area affected:

**Backend Scopes:**
- `api` - API endpoints/routers
- `services` - Backend services (email, Slack, Gemini, drift detector, etc.)
- `models` - Database models and schemas
- `db` - Database migrations, configuration
- `processor` - Contract processor pipeline
- `fingerprint` - Fingerprinting engine
- `drift` - Drift detection logic
- `risk` - Risk classification
- `alerts` - Alert system
- `auth` - Authentication (when implemented)

**Frontend Scopes:**
- `ui` - UI components
- `pages` - Next.js pages (dashboard, analytics, contracts, etc.)
- `hooks` - React Query hooks
- `api-client` - Frontend API client
- `store` - State management (Zustand)
- `types` - TypeScript types

**Infrastructure Scopes:**
- `docker` - Docker configuration
- `n8n` - n8n workflows
- `deploy` - Deployment configuration
- `config` - General configuration

**Other Scopes:**
- `docs` - Documentation
- `tests` - Test files
- `deps` - Dependencies

#### **Subject** (Required)
Rules:
- ✅ Use imperative mood: "add" not "added" or "adds"
- ✅ Lowercase first letter
- ✅ No period at end
- ✅ Max 50 characters
- ✅ Be specific and clear
- ❌ No vague words: "update", "fix", "change"

#### **Body** (Optional but recommended)
- Explain **what** and **why**, not **how**
- Wrap at 72 characters
- Use bullet points for multiple changes
- Include compliance context if relevant

#### **Footer** (Optional)
- Reference issues: `Closes #123`
- Breaking changes: `BREAKING CHANGE: description`
- Related tasks: `Related to #456`

## Analysis Rules

### 1. Determine Type
- **New files/features** → `feat`
- **Bug fixes** → `fix`
- **Code restructuring** → `refactor`
- **Performance** → `perf`
- **Tests** → `test`
- **Dependencies/config/Docker** → `chore`
- **Documentation** → `docs`

### 2. Determine Scope
Look at file paths:

**Backend:**
- `backend/routers/` → `api`
- `backend/services/email_service.py` → `services`
- `backend/services/slack_service.py` → `services`
- `backend/services/gemini_service.py` → `services`
- `backend/services/drift_detector.py` → `drift`
- `backend/services/risk_classifier.py` → `risk`
- `backend/services/contract_processor.py` → `processor`
- `backend/services/fingerprint_engine.py` → `fingerprint`
- `backend/models.py` → `models`
- `backend/database.py` → `db`
- `backend/tests/` → `tests`

**Frontend:**
- `frontend/src/app/page.tsx` → `pages`
- `frontend/src/app/analytics/` → `pages`
- `frontend/src/app/components/` → `ui`
- `frontend/src/hooks/` → `hooks`
- `frontend/src/utils/api.ts` → `api-client`
- `frontend/src/store/` → `store`
- `frontend/src/types/` → `types`

**Infrastructure:**
- `docker-compose.yml` → `docker`
- `n8n-workflows/` → `n8n`
- `.env.example` → `config`

If multiple scopes, choose the **primary** one.

### 3. Write Subject
Extract the **core change** from the diff:
- What function/feature was added?
- What bug was fixed?
- What was refactored?

Be **specific**:
- ✅ "add email verification endpoint"
- ✅ "fix session timeout calculation"
- ✅ "extract auth middleware to separate file"
- ❌ "update auth" (too vague)
- ❌ "fix bug" (no context)

### 4. Write Body (if needed)
Include if:
- Multiple files changed
- Complex logic
- Compliance-related
- Breaking changes
- Non-obvious reasoning

## Examples

### Example 1: New Service
**Diff**: Added email and Slack notification services
```
feat(services): add email and Slack notification services

Implemented notification dispatch for contract change alerts:
- Email service using Resend API with HTML templates
- Slack service using webhooks with rich formatting
- Updated contract processor to send alerts for high-risk changes

Closes #12
```

### Example 2: API Endpoint
**Diff**: Added analytics API endpoints
```
feat(api): add analytics endpoints for dashboard metrics

Implemented 4 new analytics endpoints:
- /api/analytics/trends - Change trends over time
- /api/analytics/risk-distribution - Risk level breakdown
- /api/analytics/change-types - Change type counts
- /api/analytics/vendor-stats - Top vendors by changes

Supports date range filtering.
```

### Example 3: Frontend Integration
**Diff**: Integrated React Query in dashboard
```
feat(pages): integrate React Query in dashboard page

Replaced mock data with real API calls using React Query:
- Dashboard stats from /api/stats
- Recent changes from /api/contracts/changes
- Added loading and error states

Closes #8
```

### Example 4: Bug Fix
**Diff**: Fixed fingerprint generation bug
```
fix(fingerprint): resolve TF-IDF vectorization error

Fixed issue where empty clauses caused vectorization to fail.
Added validation to skip clauses with less than 3 words.

Fixes #15
```

### Example 5: Refactoring
**Diff**: Split contract processor into smaller methods
```
refactor(processor): extract alert creation to separate method

Moved alert creation logic from process_new_version to
_create_alerts_for_changes for better testability and
separation of concerns.
```

### Example 6: n8n Workflow
**Diff**: Created contract monitoring workflow
```
feat(n8n): add automated contract monitoring workflow

Created workflow to check contracts for updates every 24 hours:
- Fetches all contracts with URLs
- Compares current content with latest version
- Triggers processing pipeline if changes detected

Workflow file: 01-contract-monitor.json
```

### Example 7: Docker Configuration
**Diff**: Updated docker-compose for production
```
chore(docker): add production docker-compose configuration

Added docker-compose.prod.yml with:
- Production-ready environment variables
- Nginx reverse proxy
- SSL certificate mounting
- Health checks for all services
```

### Example 8: UI Component
**Diff**: Created AddContractModal component
```
feat(ui): add contract upload modal component

Implemented modal with two upload methods:
- Manual entry (vendor, type, URL)
- File upload (PDF/TXT/DOC)
- Form validation and error handling
- Success/loading states
```

### Example 9: Database Migration
**Diff**: Added alert recipient field
```
feat(models): add recipient field to Alert model

Added recipient column to store email/Slack channel for alerts.
Supports user-specific notification preferences.

Migration: alembic revision 001_add_alert_recipient
```

### Example 10: Breaking Change
**Diff**: Changed API response format
```
refactor(api)!: standardize API response format

BREAKING CHANGE: All API endpoints now return data wrapped in
{ success, data, error } format instead of raw data.

Update frontend API client to handle new format.

Migration guide: docs/api-migration.md
```

## Common Mistakes to Avoid

❌ **Missing scope**:
```
feat: add export  # WRONG - no scope
```

❌ **Wrong mood**:
```
feat(auth): added login  # WRONG - use "add"
feat(auth): adds login   # WRONG - use "add"
```

❌ **Too vague**:
```
fix(api): fix bug        # WRONG - which bug?
feat(auth): update code  # WRONG - what update?
```

❌ **Too long**:
```
feat(auth): implement comprehensive user authentication system with Better Auth including session management and compliance logging  # WRONG - too long
```

❌ **Capitalized subject**:
```
feat(auth): Add login  # WRONG - lowercase "add"
```

❌ **Period at end**:
```
feat(auth): add login.  # WRONG - no period
```

## Output Format

Generate ONLY the commit message, nothing else. No explanations, no markdown formatting, just the raw commit message text.

Example output:
```
feat(services): add email notification service with Resend

Implemented email service for sending contract change alerts.
Includes HTML templates with risk-based styling and test functionality.
```

## Usage

1. Stage your changes: `git add <files>`
2. Run this workflow
3. Copy the generated message
4. Commit: `git commit -m "<generated message>"`

Or use directly:
```bash
git commit -m "$(agent generate-commit-message)"
```