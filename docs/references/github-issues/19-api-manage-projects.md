# Using the API to Manage Projects

> Source: https://docs.github.com/en/issues/planning-and-tracking-with-projects/automating-your-project/using-the-api-to-manage-projects

## Overview

The GraphQL API enables automation of GitHub Projects. This guide demonstrates project management through the API, with examples for queries and mutations.

## Authentication

### For curl Commands

Replace `TOKEN` with a token having:
- `read:project` scope for queries only
- `project` scope for queries and mutations

Token options:
- Personal access token (classic) for users
- Installation access token for GitHub Apps

**Note:** When using an installation access token for a GitHub App, some GraphQL mutations require additional permissions such as the `Contents` permission when linking projects to repositories.

### For GitHub CLI

Authenticate with: `gh auth login --scopes "project"`

Use `read:project` scope if only reading projects.

## Using Variables

Simplify scripts using variables:
- Use `-F` for numbers, booleans, or null values
- Use `-f` for other variable types

Example:
```shell
my_org="octo-org"
my_num=5
gh api graphql -f query='
  query($organization: String! $number: Int!){
    organization(login: $organization){
      projectV2(number: $number) {
        id
      }
    }
  }' -f organization=$my_org -F number=$my_num
```

## Finding Project Information

### Organization Project Node ID

```shell
gh api graphql -f query='
  query{
    organization(login: "ORGANIZATION"){
      projectV2(number: NUMBER) {
        id
      }
    }
  }'
```

### All Organization Projects

Retrieve node IDs and titles for the first 20 projects:

```shell
gh api graphql -f query='
  query{
    organization(login: "ORGANIZATION") {
      projectsV2(first: 20) {
        nodes {
          id
          title
        }
      }
    }
  }'
```

### User Project Node ID

```shell
gh api graphql -f query='
  query{
    user(login: "USER"){
      projectV2(number: NUMBER) {
        id
      }
    }
  }'
```

### All User Projects

```shell
gh api graphql -f query='
  query{
    user(login: "USER") {
      projectsV2(first: 20) {
        nodes {
          id
          title
        }
      }
    }
  }'
```

### Field Node IDs

Obtain field information including ID, name, options (for single select), and iterations:

```shell
gh api graphql -f query='
  query{
  node(id: "PROJECT_ID") {
    ... on ProjectV2 {
      fields(first: 20) {
        nodes {
          ... on ProjectV2Field {
            id
            name
          }
          ... on ProjectV2IterationField {
            id
            name
            configuration {
              iterations {
                startDate
                id
              }
            }
          }
          ... on ProjectV2SingleSelectField {
            id
            name
            options {
              id
              name
            }
          }
        }
      }
    }
  }
}'
```

**Sample Response:**
- Single select fields contain an `options` field with selectable option IDs
- Iteration fields include `configuration` with iteration IDs and start dates

### Simplified Field Query (ProjectV2FieldCommon)

```shell
gh api graphql -f query='
  query{
  node(id: "PROJECT_ID") {
    ... on ProjectV2 {
      fields(first: 20) {
        nodes {
          ... on ProjectV2FieldCommon {
            id
            name
          }
        }
      }
    }
  }
}'
```

### Project Items

Query issues, pull requests, and draft issues with field values:

```shell
gh api graphql -f query='
  query{
    node(id: "PROJECT_ID") {
        ... on ProjectV2 {
          items(first: 20) {
            nodes{
              id
              fieldValues(first: 8) {
                nodes{
                  ... on ProjectV2ItemFieldTextValue {
                    text
                    field {
                      ... on ProjectV2FieldCommon {
                        name
                      }
                    }
                  }
                  ... on ProjectV2ItemFieldDateValue {
                    date
                    field {
                      ... on ProjectV2FieldCommon {
                        name
                      }
                    }
                  }
                  ... on ProjectV2ItemFieldSingleSelectValue {
                    name
                    field {
                      ... on ProjectV2FieldCommon {
                        name
                      }
                    }
                  }
                }
              }
              content{
                ... on DraftIssue {
                  title
                  body
                }
                ...on Issue {
                  title
                  assignees(first: 10) {
                    nodes{
                      login
                    }
                  }
                }
                ...on PullRequest {
                  title
                  assignees(first: 10) {
                    nodes{
                      login
                    }
                  }
                }
              }
            }
          }
        }
      }
    }'
```

**Note:** A project may contain items that a user does not have permission to view. In this case, the item type will be returned as `REDACTED`.

## Updating Projects

**Important:** You cannot add and update an item in the same call. You must use `addProjectV2ItemById` to add the item and then use `updateProjectV2ItemFieldValue` to update the item.

### Adding Issues or Pull Requests

```shell
gh api graphql -f query='
  mutation {
    addProjectV2ItemById(input: {projectId: "PROJECT_ID" contentId: "CONTENT_ID"}) {
      item {
        id
      }
    }
  }'
```

Response contains the new item's node ID. If the item already exists, the existing ID returns.

### Adding Draft Issues

```shell
gh api graphql -f query='
  mutation {
    addProjectV2DraftIssue(input: {projectId: "PROJECT_ID" title: "TITLE" body: "BODY"}) {
      projectItem {
        id
      }
    }
  }'
```

### Updating Project Settings

Modify title, visibility, readme, and description:

```shell
gh api graphql -f query='
  mutation {
    updateProjectV2(
      input: {
        projectId: "PROJECT_ID",
        title: "Project title",
        public: false,
        readme: "# Project README\n\nA long description",
        shortDescription: "A short description"
      }
    ) {
      projectV2 {
        id
        title
        readme
        shortDescription
      }
    }
  }'
```

### Updating Text, Number, or Date Fields

```shell
gh api graphql -f query='
  mutation {
    updateProjectV2ItemFieldValue(
      input: {
        projectId: "PROJECT_ID"
        itemId: "ITEM_ID"
        fieldId: "FIELD_ID"
        value: {
          text: "Updated text"
        }
      }
    ) {
      projectV2Item {
        id
      }
    }
  }'
```

**Limitation:** You cannot use `updateProjectV2ItemFieldValue` to change `Assignees`, `Labels`, `Milestone`, or `Repository` as these are pull request/issue properties. Use dedicated mutations instead:
- `addAssigneesToAssignable`
- `removeAssigneesFromAssignable`
- `addLabelsToLabelable`
- `removeLabelsFromLabelable`
- `updateIssue`
- `updatePullRequest`
- `transferIssue`

### Updating Single Select Fields

```shell
gh api graphql -f query='
  mutation {
    updateProjectV2ItemFieldValue(
      input: {
        projectId: "PROJECT_ID"
        itemId: "ITEM_ID"
        fieldId: "FIELD_ID"
        value: {
          singleSelectOptionId: "OPTION_ID"
        }
      }
    ) {
      projectV2Item {
        id
      }
    }
  }'
```

### Updating Iteration Fields

```shell
gh api graphql -f query='
  mutation {
    updateProjectV2ItemFieldValue(
      input: {
        projectId: "PROJECT_ID"
        itemId: "ITEM_ID"
        fieldId: "FIELD_ID"
        value: {
          iterationId: "ITERATION_ID"
        }
      }
    ) {
      projectV2Item {
        id
      }
    }
  }'
```

### Deleting Items

```shell
gh api graphql -f query='
  mutation {
    deleteProjectV2Item(
      input: {
        projectId: "PROJECT_ID"
        itemId: "ITEM_ID"
      }
    ) {
      deletedItemId
    }
  }'
```

## Managing Projects

### Creating Projects

Get the owner's node ID via REST API:

```shell
gh api -H "Accept: application/vnd.github+json" /users/GITHUB_OWNER
```

Then create the project:

```shell
gh api graphql -f query='
  mutation{
    createProjectV2(
      input: {
        ownerId: "OWNER_ID",
        title: "PROJECT_NAME"
      }
    ){
      projectV2 {
        id
      }
     }
  }'
```

## Using Webhooks

Subscribe to project events via webhooks. When configured, GitHub sends HTTP POST payloads to trigger server-side automation. The `projects_v2_item` webhook event fires when items are edited.
