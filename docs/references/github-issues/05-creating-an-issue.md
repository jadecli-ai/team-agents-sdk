# Creating an Issue

> Source: https://docs.github.com/en/issues/tracking-your-work-with-issues/using-issues/creating-an-issue

## Overview

Issues can be created in a variety of ways, so you can choose the most convenient method for your workflow.

## Permissions

People with read access can create an issue in a repository where issues are enabled. Repository administrators can disable this feature if needed.

## Methods for Creating Issues

### 1. Creating an Issue from a Repository

This is the standard web interface method:

1. Navigate to your repository's main page on GitHub
2. Click the **Issues** tab in the horizontal navigation bar
3. Select **New issue**
4. If templates exist, choose your issue type or click **Open a blank issue**
5. Enter a title in the "Title" field
6. Provide a description in the comment body field
7. Optionally assign the issue, add it to a project, associate a milestone, set the issue type, or apply labels
8. Click **Submit new issue**

### 2. Creating an Issue with GitHub CLI

GitHub CLI enables command-line issue creation. Basic syntax:

```shell
gh issue create --title "My new issue" --body "Here are more details."
```

Advanced usage with additional fields:

```shell
gh issue create --title "My new issue" --body "Here are more details." \
  --assignee @me,monalisa --label "bug,help wanted" \
  --project onboarding --milestone "learning codebase"
```

### 3. Creating an Issue from a Comment

Convert existing comments into issues:

1. Navigate to the relevant comment on an issue or pull request
2. Click the kebab menu (three dots) on that comment
3. Select **Reference in new issue**
4. Use the repository dropdown to choose your target repository
5. Add a descriptive title and body
6. Click **Create issue**
7. Configure optional fields as needed
8. Click **Submit new issue**

### 4. Creating an Issue from Code

Reference specific code lines or ranges:

1. Navigate to the repository main page
2. Locate the code: either directly in a file or in a pull request's "Files changed" section
3. Select code by clicking line numbers (single line) or Shift+clicking for ranges
4. Click the kebab menu to the left of the code
5. Choose **Reference in new issue**
6. Add title and description
7. Configure optional fields
8. Click **Submit new issue**

### 5. Creating an Issue from Discussion

For users with triage permissions:

1. Go to the **Discussions** tab
2. Select the discussion to convert
3. In the right sidebar, click **Create issue from discussion**
4. The discussion content auto-populates in the issue body
5. Add or modify the title as needed
6. Configure optional fields
7. Click **Submit new issue**

Note: Creating an issue from a discussion does not convert the discussion to an issue or delete the existing discussion.

### 6. Creating an Issue from a Project

Streamlined creation without leaving your project:

1. Navigate to your project
2. At the bottom of a table, group of items, or board column, click the plus icon
3. Select **Create new issue**
4. Choose the target repository from the dropdown
5. Enter the issue title below the repository selector
6. Optionally configure assignees, labels, milestones, and projects
7. Add an optional description
8. Check **Create more** if you want to create additional issues
9. Click **Create**

When using grouped views, creating an issue in that group will automatically set the new issue's field to the group's value.

### 7. Creating an Issue from a Task List Item

Within existing issues, convert task list items to full issues by hovering over the task and clicking the issue icon in the upper-right corner.

### 8. Creating an Issue from a URL Query

Use query parameters to pre-populate issue fields:

| Parameter | Purpose |
|-----------|---------|
| `title` | Sets the issue title |
| `body` | Pre-fills the issue description |
| `labels` | Applies comma-separated labels |
| `milestone` | Associates a specific milestone |
| `assignees` | Assigns the issue to users |
| `projects` | Adds the issue to specified projects |
| `template` | Loads a template from the ISSUE_TEMPLATE directory |

Example:
```
https://github.com/octo-org/octo-repo/issues/new?labels=bug&title=New+bug+report
```

Requirements: You must have the proper permissions for any action to use the equivalent query parameter.

### 9. Creating an Issue with Copilot Chat on GitHub

This feature is in public preview. Creating issues manually can be repetitive and time-consuming. With Copilot, you can create issues faster by prompting in natural language, or even by uploading a screenshot.

### 10. Creating an Issue from Copilot Chat in VS Code

Users can create issues directly through Copilot Chat in Visual Studio Code using the Model Context Protocol (MCP).

## Key Features Available After Creation

For project maintainers, these options are available:

- Assign the issue to team members
- Add to projects
- Associate with milestones
- Set the issue type
- Apply relevant labels

## Error Handling

- Invalid URLs or insufficient permissions return `404 Not Found` errors
- URLs exceeding server limits return `414 URI Too Long` errors

## Related Resources

- About Issues documentation
- Writing on GitHub guide
- Template best practices for encouraging useful issues and pull requests
