# New Relic Roles & Permissions Exporter

A lightweight, standalone Python tool to export all New Relic roles and their assigned permissions within an organization to a unified CSV file.

The script queries New Relic's **NerdGraph GraphQL API**, iterates through each role assigned to your Organization ID, handles cursor pagination for attached permissions, and merges the datasets into a single spreadsheet.

---

## Features

* **Zero External Dependencies:** Built using Python standard libraries (`urllib`, `json`, `csv`, `argparse`). No `pip install` required.
* **Automatic Pagination:** Handles pagination (`nextCursor`) when a role has large sets of granular permissions.
* **Graceful Handling:** Preserves roles in the CSV output even if no permissions are attached to them.
* **Joined Data Structure:** Automatically maps and joins role metadata directly to individual permissions on a per-row basis.

---

## Prerequisites

* **Python 3.6+** installed on your system.
* A **New Relic User API Key** (`NRAK-...`).
* Your **New Relic Organization ID**.

> **Note:** To find your Organization ID, log into New Relic, click your profile icon $\rightarrow$ **Administration** $\rightarrow$ **Organization and accounts**. The Organization ID is displayed at the top.

---

## Usage

### 1. Basic Command

Run the script by supplying your Organization ID and User API Key:

```bash
python3 fetch_roles_and_permissions.py \
  --org-id "YOUR_ORG_ID" \
  --api-key "NRAK-YOUR_USER_API_KEY"

```

### 2. Custom Output Filename

Use the `--output` flag to specify a custom name for the generated CSV file:

```bash
python3 fetch_roles_and_permissions.py \
  --org-id "YOUR_ORG_ID" \
  --api-key "NRAK-YOUR_USER_API_KEY" \
  --output "audit_roles_2026.csv"

```

---

## Command-Line Arguments

| Flag | Required | Default | Description |
| --- | --- | --- | --- |
| `--org-id` | **Yes** | — | Your New Relic Organization ID. |
| `--api-key` | **Yes** | — | Your New Relic User API Key (`NRAK-...`). |
| `--output` | No | `roles_and_permissions.csv` | Path and filename for the exported CSV. |
| `-h`, `--help` | No | — | Displays the command-line help message. |

---

## CSV Output Schema

The output CSV file contains the following columns:

| Column Header | Description |
| --- | --- |
| `Role ID` | Unique GraphQL ID for the role. |
| `Role Name` | Human-readable name of the role (e.g., *Standard User*, *Custom Admin*). |
| `Role Type` | Indicates whether the role is `standard` or `custom`. |
| `Role Scope` | Scope level of the role (e.g., `organization` or `account`). |
| `Permission ID` | Unique ID of the capability assigned to the role. |
| `Permission Name` | Descriptive name of the granted permission. |
| `Product` | Associated New Relic product module (e.g., `apm`, `logs`, `alerts`). |
| `Feature` | Specific feature area within the product module. |
| `Category` | Permission category classification (e.g., `read`, `write`, `admin`). |
