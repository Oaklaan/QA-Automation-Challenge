# QA Automation Challenge

**Candidate:** Krushna Koshatwar  
**Technology Stack:** Python, Pytest, Playwright, Requests, BrowserStack

---

# Project Overview

This repository contains the solution for the QA Automation Challenge. The implementation demonstrates:

- Debugging and improving flaky UI tests
- Designing a scalable automation framework
- Creating an end-to-end API + UI integration test
- Applying automation best practices suitable for CI/CD environments

The solution is designed with reliability, maintainability, scalability, and enterprise automation practices in mind.

---

# Repository Structure

```
qa-automation/
│
├── part1/
│   ├── test_user_login.py
│   └── test_multi_tenant_access.py
│
├── part2/
│   └── Framework Design Documentation
│
├── part3/
│   └── test_project_creation_flow.py
│
├── config/
├── framework/
├── pages/
├── tests/
├── fixtures/
├── test-data/
├── reports/
│
├── requirements.txt
├── pytest.ini
└── README.md
```

---

# Technologies Used

| Technology | Purpose |
|------------|---------|
| Python | Programming Language |
| Pytest | Test Framework |
| Playwright | Web UI Automation |
| Requests | API Testing |
| BrowserStack | Cross-browser & Mobile Testing |
| Page Object Model | Framework Design Pattern |

---

# Part 1 – Debugging Flaky Test Code

## Objective

Improve the reliability of existing Playwright UI tests by identifying flaky behaviour and implementing robust synchronization and error handling.

## Improvements Implemented

- Added explicit waits using Playwright
- Waited for page navigation
- Waited for dynamic dashboard content
- Implemented optional 2FA handling
- Added screenshot capture on failures
- Added try/except/finally blocks
- Ensured browser cleanup
- Added fixed viewport for CI consistency
- Added lazy-loading synchronization
- Improved tenant-specific loading handling

## Reliability Improvements

- Explicit waits instead of implicit timing
- Better error diagnostics
- Stable execution in CI/CD
- Reduced intermittent failures

---

# Part 2 – Test Framework Design

## Objective

Design a scalable automation framework supporting:

- Web Testing
- Mobile Testing
- API Testing
- Multi-Tenant Architecture
- Role-Based Authentication
- BrowserStack
- CI/CD

## Framework Highlights

- Page Object Model (POM)
- Base Test classes
- Base Page classes
- Base API Client
- Driver Factory
- Environment Management
- Test Data Factory
- Centralized Logging
- BrowserStack Integration

## Supported Platforms

### Browsers

- Chrome
- Firefox
- Safari

### Mobile

- Android
- iOS

---

# Part 3 – API + UI Integration Test

## Business Flow

1. Create Project using API
2. Verify Project in Web UI
3. Verify Project on Mobile
4. Validate Tenant Isolation

## Validation Covered

- API Success
- UI Synchronization
- Mobile Compatibility
- Security Validation
- Multi-Tenant Isolation

---

# Setup Instructions

## Clone Repository

```bash
git clone <repository-url>

cd qa-automation
```

---

## Create Virtual Environment

Windows

```bash
python -m venv venv

venv\Scripts\activate
```

Linux / macOS

```bash
python3 -m venv venv

source venv/bin/activate
```

---

## Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Install Playwright Browsers

```bash
python -m playwright install
```

---

# Running Tests

## Part 1

```bash
pytest part1 -v
```

Run Login Test

```bash
pytest part1/test_user_login.py -v
```

Run Multi Tenant Test

```bash
pytest part1/test_multi_tenant_access.py -v
```

---

## Part 3

```bash
pytest part3 -v
```

---

# Framework Features

- Explicit Waits
- Page Object Model
- API Wrapper
- Retry Logic
- Screenshot on Failure
- Browser Cleanup
- Configurable Environments
- Multi-Tenant Support
- Role-Based Authentication
- BrowserStack Support
- CI/CD Ready

---

# Configuration

Environment configuration is stored separately.

```
config/

    environments/

        local.yaml

        staging.yaml

        production.yaml

    tenants/

    browsers.yaml

    browserstack.yaml
```

This allows switching between environments without changing test code.

---

# Assumptions

The following assumptions were made due to incomplete assessment requirements:

- Valid test accounts are available
- BrowserStack credentials exist
- Test tenants are preconfigured
- API authentication returns Bearer tokens
- Test data cleanup APIs exist
- Dashboard loads successfully after login
- Mobile and Web use the same backend

---

# Testing Strategy

The framework follows a layered automation strategy.

- API tests validate backend functionality.
- UI tests verify user-facing workflows.
- Mobile tests validate responsive behaviour.
- Integration tests ensure end-to-end business processes.
- Multi-tenant validation confirms security boundaries.
- Explicit waits improve execution stability.

---

# CI/CD Integration

The framework is designed to integrate with:

- GitHub Actions
- Jenkins
- Azure DevOps

Typical Pipeline

```
Checkout Code

↓

Install Dependencies

↓

Run API Tests

↓

Run UI Tests

↓

Run Mobile Tests

↓

Generate Reports

↓

Upload Artifacts
```

---

# Reporting

Supported reporting mechanisms include:

- Pytest HTML Report
- Allure Report
- Screenshots
- Execution Logs
- BrowserStack Session Links

---

# Challenges Addressed

- Flaky UI Tests
- Dynamic Loading
- Optional 2FA
- Multi-Tenant Architecture
- Cross-Browser Compatibility
- Mobile Validation
- API/UI Synchronization
- CI/CD Reliability

---

# Future Improvements

- Docker Integration
- Kubernetes Execution
- Visual Regression Testing
- Accessibility Testing
- Performance Testing
- Contract Testing
- AI-assisted Test Generation

---

# Conclusion

This project demonstrates a complete automation solution for a modern B2B SaaS platform.

The implementation focuses on:

- Reliable automation
- Modular framework architecture
- API + UI integration
- Multi-tenant support
- Cross-browser execution
- Mobile testing
- CI/CD readiness
- Maintainable and reusable test design

The framework is scalable and can be extended to support additional applications, environments, and business workflows with minimal changes.
