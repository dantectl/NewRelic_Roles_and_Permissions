#!/usr/bin/env python3
import argparse
import csv
import json
import sys
import urllib.request

GRAPHQL_URL = "https://api.newrelic.com/graphql"


def make_graphql_request(query, api_key):
    headers = {
        "Content-Type": "application/json",
        "API-Key": api_key,
    }
    payload = json.dumps({"query": query}).encode("utf-8")
    req = urllib.request.Request(GRAPHQL_URL, data=payload, headers=headers)

    try:
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            if "errors" in res_data:
                print(
                    f"Warning: GraphQL returned errors: {res_data['errors']}",
                    file=sys.stderr,
                )
            return res_data
    except urllib.error.HTTPError as e:
        print(f"HTTP Error {e.code}: {e.read().decode('utf-8')}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Request failed: {e}", file=sys.stderr)
        sys.exit(1)


def fetch_roles(org_id, api_key):
    """Step 1: Get all roles for the given Organization ID."""
    query = f"""
    {{
      customerAdministration {{
        roles(filter: {{organizationId: {{eq: "{org_id}"}}}}) {{
          totalCount
          items {{
            id
            name
            type
            scope
          }}
        }}
      }}
    }}
    """
    res = make_graphql_request(query, api_key)
    return (
        res.get("data", {})
        .get("customerAdministration", {})
        .get("roles", {})
        .get("items", [])
    )


def fetch_permissions_for_role(role_id, api_key):
    """Step 2: Get all permissions assigned to a specific role ID (handling pagination)."""
    permissions = []
    cursor = None

    while True:
        cursor_arg = f', cursor: "{cursor}"' if cursor else ""
        query = f"""
        {{
          customerAdministration {{
            permissions(filter: {{roleId: {{eq: "{role_id}"}}}}{cursor_arg}) {{
              items {{
                id
                name
                product
                feature
                category
              }}
              nextCursor
            }}
          }}
        }}
        """
        res = make_graphql_request(query, api_key)
        perm_block = (
            res.get("data", {})
            .get("customerAdministration", {})
            .get("permissions")
            or {}
        )

        items = perm_block.get("items", [])
        permissions.extend(items)

        cursor = perm_block.get("nextCursor")
        if not cursor:
            break

    return permissions


def main():
    parser = argparse.ArgumentParser(
        description="Fetch New Relic roles and permissions into a joined CSV."
    )
    parser.add_argument("--org-id", required=True, help="New Relic Organization ID")
    parser.add_argument(
        "--api-key", required=True, help="New Relic User API Key (NRAK-...)"
    )
    parser.add_argument(
        "--output",
        default="roles_and_permissions.csv",
        help="Output CSV file name (Default: roles_and_permissions.csv)",
    )

    args = parser.parse_args()

    print(f"1. Fetching roles for Organization ID: {args.org_id}...")
    roles = fetch_roles(args.org_id, args.api_key)
    print(f"   Found {len(roles)} roles.\n")

    print("2. Fetching permissions per role and joining datasets...")
    joined_rows = []

    for idx, role in enumerate(roles, 1):
        role_id = role.get("id")
        role_name = role.get("name")
        print(
            f"   [{idx}/{len(roles)}] Processing Role: {role_name} (ID: {role_id})..."
        )

        permissions = fetch_permissions_for_role(role_id, args.api_key)

        if permissions:
            for perm in permissions:
                joined_rows.append(
                    {
                        "Role ID": role_id,
                        "Role Name": role_name,
                        "Role Type": role.get("type"),
                        "Role Scope": role.get("scope"),
                        "Permission ID": perm.get("id"),
                        "Permission Name": perm.get("name"),
                        "Product": perm.get("product"),
                        "Feature": perm.get("feature"),
                        "Category": perm.get("category"),
                    }
                )
        else:
            # If a role has no permissions attached, preserve the role entry
            joined_rows.append(
                {
                    "Role ID": role_id,
                    "Role Name": role_name,
                    "Role Type": role.get("type"),
                    "Role Scope": role.get("scope"),
                    "Permission ID": "",
                    "Permission Name": "",
                    "Product": "",
                    "Feature": "",
                    "Category": "",
                }
            )

    # Output joined data to CSV
    fieldnames = [
        "Role ID",
        "Role Name",
        "Role Type",
        "Role Scope",
        "Permission ID",
        "Permission Name",
        "Product",
        "Feature",
        "Category",
    ]

    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(joined_rows)

    print(f"\nDone! Successfully saved {len(joined_rows)} rows to '{args.output}'.")


if __name__ == "__main__":
    main()
