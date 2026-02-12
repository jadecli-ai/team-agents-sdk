# Filtering and Searching Issues and Pull Requests

> Source: https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/filtering-and-searching-issues-and-pull-requests

## Overview

This guide explains how to organize and locate issues and pull requests in GitHub repositories through filtering, searching, and sorting techniques.

## Basic Filtering

### Default Filters Available

GitHub provides built-in filters to help locate:
- All open issues and pull requests
- Items you've created
- Items assigned to you
- Items where you're mentioned

### How to Apply Basic Filters

1. Navigate to your repository's main page
2. Click the **Issues** or **Pull Requests** tab
3. Select the **Filters** dropdown menu
4. Choose your desired filter type

## Advanced Filtering with Boolean Logic

### Using AND/OR Operators

**AND operator**: Returns results where both conditions are true

Example: `label:"question" AND assignee:octocat` displays issues with the "question" label assigned to @octocat.

**OR operator**: Returns results where either condition is true

Example: `assignee:octocat OR assignee:hubot` shows issues assigned to either user.

**Default behavior**: Spaces between statements default to AND operations.

### Nested Filters with Parentheses

Combine multiple conditions using parentheses (up to 5 levels deep):

```
(type:"Bug" AND assignee:octocat) OR (type:"Feature" AND assignee:hubot)
```

This finds bugs assigned to @octocat or features assigned to @hubot.

## Filtering by Assignees

1. Navigate to repository main page
2. Click **Issues** or **Pull Requests**
3. Select the **Assignee** dropdown
4. Click a person's name or select **Assigned to nobody**

**Tip**: Clear filters by clicking "Clear current search query, filters, and sorts"

## Filtering by Labels

1. Go to repository main page
2. Click **Issues** or **Pull Requests**
3. Click the **Labels** button
4. Select your desired label

## Filtering by Issue Type

For organizations using issue types:

1. Navigate to repository main page
2. Click **Issues**
3. Select **Types** dropdown menu
4. Click an issue type

You can also use the `type:` qualifier directly in search queries.

## Pull Request Review Status Filters

Access filters to find PRs by:
- Review status (unreviewed, approved, changes requested)
- Reviewer involvement
- Review requirements

Use the **Reviews** dropdown in the upper-right corner above the PR list to select specific review statuses.

### Filterable PR Review States

- Haven't been reviewed yet
- Require review before merging
- Approved by reviewers
- Changes requested by reviewers
- Reviewed by you
- Requested directly for your review
- Team review requested

## Search-Based Filtering

### Using the Search Bar

The issues/pull requests search bar supports custom filters and multiple sort options.

### General Search Terms

| Filter | Example |
|--------|---------|
| Author | `state:open is:issue author:octocat` |
| Involvement | `state:open is:issue involves:octocat` |
| Assignee | `state:open is:issue assignee:octocat` |
| Label | `state:open is:issue label:"bug"` |
| Negation | `state:open is:issue -author:octocat` |

### Label Filtering Logic

- **Logical OR** (either label): `label:"bug","wip"`
- **Logical AND** (both labels): `label:"bug" label:"wip"`

### Copilot Integration

Search for items assigned to or authored by Copilot using `@copilot`:
- `assignee:@copilot`
- `author:@copilot`

### Issue-Specific Search Terms

| Filter | Example |
|--------|---------|
| Linked to PR | `linked:pr` |
| Closure reason | `is:closed reason:completed` or `is:closed reason:"not planned"` |
| Issue type | `is:open type:"Bug"` |
| Has metadata | `has:label` |
| Missing metadata | `no:project` |
| Repository ownership | `state:open is:issue org:github OR user:octocat` (up to 16 user/org qualifiers) |

### Pull Request-Specific Search Terms

| Filter | Example |
|--------|---------|
| Draft PRs | `is:draft` |
| Unreviewed | `state:open is:pr review:none` |
| Review required | `state:open is:pr review:required` |
| Approved | `state:open is:pr review:approved` |
| Changes requested | `state:open is:pr review:changes_requested` |
| By specific reviewer | `state:open is:pr reviewed-by:octocat` |
| Requested from user | `state:open is:pr review-requested:octocat` |
| Requested from you | `state:open is:pr user-review-requested:@me` |
| Team review requested | `state:open is:pr team-review-requested:github/docs` |
| Linked to issue | `linked:issue` |
| Merge status | `is:merged` or `is:unmerged` |

## GitHub CLI Search

### Basic CLI Search

Using `gh issue list` or `gh pr list` with `--search` argument:

```shell
gh issue list --search 'no:assignee label:"help wanted",bug sort:created-asc'
```

This lists unassigned issues with "help wanted" or "bug" labels, sorted by creation date.

```shell
gh pr list --search "team:octo-org/octo-team"
```

This lists all PRs mentioning the specified team.

## Sorting Issues and Pull Requests

Available sort options:
- Newest created
- Oldest created
- Most commented
- Least commented
- Newest updated
- Oldest updated
- Most reactions added

### How to Sort

1. Navigate to repository main page
2. Click **Issues** or **Pull Requests**
3. Select **Sort** dropdown
4. Choose your sort method

**Reset**: Click **Sort** > **Newest** to clear sort selection

## Sharing Filters

When you apply filters or sorting, your browser URL updates automatically to reflect the view. You can share this URL with others who will see the identical filtered results.

Example filtered URL:
```
/issues?q=state:open+is:issue+assignee:hubot+sort:created-asc
```

## Key Tips

- Use keyboard shortcuts to focus the search bar
- Combine multiple filter criteria for precise results
- Share filter URLs for consistent team views
- Clear all filters easily with the "Clear current search query" button
