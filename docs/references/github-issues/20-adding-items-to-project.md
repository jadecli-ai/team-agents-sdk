# Adding Items to Your Project

> Source: https://docs.github.com/en/issues/planning-and-tracking-with-projects/managing-items-in-your-project/adding-items-to-your-project

## Overview

This guide covers how to add pull requests, issues, and draft issues to GitHub Projects individually or in bulk.

## Key Limitation

A project can contain a maximum of **50,000 items** across both active views and the archive page.

## Adding Issues and Pull Requests

### Timeline Events Notice

When you add an issue or pull request to a project, timeline events are created. These events are only visible to users with at least read access to the project. Automated workflow changes are attributed to `@github-project-automation`.

### Automatic Addition

Configure built-in workflows to automatically add items when they meet specific filter criteria.

### Pasting URLs

1. Position cursor in the bottom row of the project table
2. Paste the issue or pull request URL
3. Press Return to add the item

### Searching Within Your Project

1. Place cursor in the bottom row next to the plus icon
2. Type `#` to open the repository list
3. Select the repository containing your item
4. Search and select the specific issue or pull request by title or number

### Bulk Adding Items

1. Click the plus button in the bottom row
2. Select **Add item from repository**
3. Choose a repository from the dropdown (optional)
4. Use filters like `label:bug` to narrow results
5. Select multiple items
6. Click **Add selected items**

### Adding from Repository Lists

1. Navigate to a repository's Issues or Pull Requests section
2. Use checkboxes to select individual items or "select all" at the top
3. Click the **Projects** button above the list
4. Choose which projects to add the selected items to

### Adding from Within an Issue or PR

1. Navigate to the specific issue or pull request
2. Click **Projects** in the sidebar
3. Select your target project
4. Optionally populate custom fields

### Using Command Palette

1. Press Command+K (Mac) or Ctrl+K (Windows/Linux)
2. Type "Add items" and press Return
3. Select repository and search for items
4. Choose desired issues/pull requests
5. Click **Add selected items**

## Creating New Issues

When creating issues in grouped views, the new item automatically inherits the group's field value.

1. Click the plus button at the bottom of a table, item group, or board column
2. Select **Create new issue**
3. Choose the repository for the new issue
4. Enter an issue title
5. Optionally set assignees, labels, milestones, and add to other projects
6. Optionally add a description
7. Select **Create more** to create additional issues in succession
8. Click **Create**

## Creating Draft Issues

Draft issues exist only within your project and are useful for capturing quick ideas without creating full repository issues.

1. Place cursor in the bottom project row
2. Type your idea and press Enter
3. Click the draft issue title to add body text
4. Enter markdown text in the input box
5. Click **Save**

### Draft Issue Limitations

Draft issues support titles, text bodies, assignees, and custom fields. However, repository, labels, and milestones require first converting the draft to a full issue. Users won't receive notifications for draft issues unless they're converted to standard issues.

## Related Resources

- Converting draft issues to issues
- Editing items in your project
- Archiving items automatically
- Using built-in automations
