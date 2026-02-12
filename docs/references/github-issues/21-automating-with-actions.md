# Automating Projects using Actions

> Source: https://docs.github.com/en/issues/planning-and-tracking-with-projects/automating-your-project/automating-projects-using-actions

## Overview

GitHub Actions enables automation of your projects through workflows. This guide demonstrates using the GraphQL API with GitHub Actions to add pull requests to organization projects automatically.

## Key Concept

When a pull request is marked "ready for review", the workflow automatically:
- Adds a new task to the project
- Sets a "Status" field to "Todo"
- Populates a custom "Date posted" field with the current date

## Important Prerequisites

**Token Scope Limitation**: The built-in `GITHUB_TOKEN` cannot access projects due to repository-level scoping. Instead, use either:
1. A GitHub App (recommended for organization projects)
2. A personal access token (recommended for user projects)

A project must span multiple repositories, but each workflow is repository-specific. Install the workflow in each repository you want tracked.

## Authentication Option 1: GitHub App

### Setup Steps

1. **Create/Select GitHub App**: Register a new app or use an existing one owned by your organization
2. **Configure Permissions**: Grant read/write access to organization projects, plus read access to repository pull requests and issues
3. **Critical Permission Note**: You can control your app's permission to organization projects and to repository projects. You must give permission to read and write organization projects; permission to read and write repository projects will not be sufficient.
4. **Install App**: Deploy across all repositories requiring project access
5. **Store App ID**: Save as a configuration variable (replace `APP_ID` in workflow)
6. **Generate Private Key**: Store file contents (including RSA markers) as a secret (replace `APP_PEM` in workflow)
7. **Configure Workflow Variables**:
   - Replace `YOUR_ORGANIZATION` with organization name (e.g., `octo-org`)
   - Replace `YOUR_PROJECT_NUMBER` with project number from URL
   - Project must contain "Status" single-select field with "Todo" option and "Date posted" date field

### Workflow Structure

The GitHub App workflow executes five primary steps:

**Step 1 - Generate Token**: Uses `actions/create-github-app-token@v2` to create an installation access token from app ID and private key, storing it as `steps.generate-token.outputs.token`

**Step 2 - Get Project Data**: Executes GraphQL query retrieving project ID and field information (first 20 fields), parsing results into environment variables via `jq`

**Step 3 - Add PR to Project**: Invokes `addProjectV2ItemById` mutation to add the triggering pull request to the project, extracting the created item ID

**Step 4 - Get Date**: Captures current date in `yyyy-mm-dd` format as environment variable

**Step 5 - Set Fields**: Applies two simultaneous mutations - setting Status to Todo and Date posted to current date via `updateProjectV2ItemFieldValue`

## Authentication Option 2: Personal Access Token

### Setup Steps

1. **Create Token**: Generate personal access token (classic) with `project` and `repo` scopes
2. **Store Secret**: Save token as repository or organization secret
3. **Configure Workflow**: Same field requirements as GitHub App approach

### Workflow Structure

The personal access token workflow mirrors the GitHub App approach but eliminates the token generation step. Instead, it directly references the secret via `${{ secrets.YOUR_TOKEN }}` for the `GH_TOKEN` variable.

## Customization Examples

To modify field extraction from API responses:

**Extract Custom Field ID:**
```bash
echo 'TEAM_FIELD_ID='$(jq '.data.organization.projectV2.fields.nodes[] |
select(.name== "Team") | .id' project_data.json) >> $GITHUB_ENV
```

**Extract Single Select Option ID:**
```bash
echo 'OCTOTEAM_OPTION_ID='$(jq '.data.organization.projectV2.fields.nodes[] |
select(.name== "Team") |.options[] | select(.name=="Octoteam") |.id'
project_data.json) >> $GITHUB_ENV
```

## Related Resources

- [Quickstart for GitHub Actions](https://docs.github.com/en/actions/quickstart)
- [GitHub Actions documentation](https://docs.github.com/en/actions)
- [Using the API to manage Projects](https://docs.github.com/en/issues/planning-and-tracking-with-projects/automating-your-project/using-the-api-to-manage-projects)
- [actions/add-to-project](https://github.com/actions/add-to-project) - GitHub-maintained workflow for simplified automation
