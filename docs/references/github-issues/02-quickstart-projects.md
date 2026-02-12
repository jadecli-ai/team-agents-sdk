# Quickstart for GitHub Projects

> Source: https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/quickstart-for-projects

## Introduction

This interactive guide demonstrates how to use GitHub Projects for planning and tracking work. You'll create a new project, customize multiple views, add custom fields, set up built-in workflows, and configure charts to visualize project data. The guide covers managing team backlogs, iteration planning, and roadmaps for communicating priorities with collaborators.

## Prerequisites

You can create either an organization project or a user project. Organization projects require a GitHub organization (see organizational setup documentation for creation steps).

For this guide, you'll add issues from repositories you own or your organization owns. Familiarity with creating issues in GitHub is helpful. All items added will become part of your project.

## Creating a Project

### Organization Project Steps

1. Click your profile picture in the upper-right corner, then select **Organizations**
2. Click your organization name
3. Under your organization name, click **Projects**
4. Click **New project**
5. Choose your project type:
   - **Blank project**: Select Table, Roadmap, or Board under "Start from scratch"
   - **Template**: Choose from built-in GitHub templates, your organization's templates, or recommended templates
6. If using a template, review the pre-configured fields, views, workflows, and insights
7. Enter your project name in the text box
8. Optionally select **Import items from repository** to automatically populate your project (this designates the repository as your default)
9. Click **Create project**

### User Project Steps

1. Click your profile picture in the top right, then select **Your profile**
2. Click **Projects**
3. Click **New project**
4. Select your project type (same options as organization projects)
5. Review template details if applicable
6. Enter your project name
7. Click **Create project**

## Project Description and README

You can add a project description and README to communicate purpose, usage instructions, and relevant links.

1. Navigate to your project
2. Click the menu icon in the top-right corner
3. Select **Settings**
4. Under "Add a description," type your description and click **Save**
5. Under "README," type your content using Markdown formatting
6. Use the eye icon to preview or pencil icon to edit
7. Click **Save** to finalize your README

Quick edits to description and README are available by clicking the sidebar icon in the top right of your project.

## Adding Items to Your Project

### Adding Existing Issues or Pull Requests

1. Click in the bottom row next to the plus icon
2. Paste the URL of the issue or pull request
3. Press Return to add the item

Repeat these steps to add multiple items. See the full Adding items documentation for alternative methods and additional item types.

### Adding Draft Issues

Draft issues are internal project items not yet converted to repository issues:

1. Click in the bottom row next to the plus icon
2. Type your idea and press Enter
3. Click the draft issue title to open it
4. In the markdown input box, enter the body text
5. Click **Save**

## Adding Custom Fields

### Iteration Field

Iteration fields enable planning and tracking work across repeating time blocks with customizable durations and break insertion:

1. In table view, click the plus icon in the rightmost field header
2. Click **New field**
3. Type your field name
4. Select **Iteration**
5. Adjust iteration duration (enter number, select days or weeks)
6. Click **Save**
7. Assign iterations to all project items

### Priority Field

Create a single-select field for prioritization:

1. In table view, click the plus icon in the rightmost field header
2. Click **New field**
3. Type "Priority"
4. Select **Single select**
5. Under "Options," type "High"
6. Click **Add option** for "Medium"
7. Click **Add option** for "Low"
8. Click **Save**
9. Assign priority levels to all items

### Estimate Field

Create a number field for tracking task complexity:

1. In table view, click the plus icon in the rightmost field header
2. Click **New field**
3. Type "Estimate"
4. Select **Number**
5. Click **Save**
6. Enter estimates for all project items

## Creating Views

Views allow visualization of project items in different formats. For detailed customization information, see the Customizing views documentation.

### Team Backlog (Table View)

Display your backlog as a spreadsheet to view multiple fields and make quick edits:

1. In table view, click the plus icon in the rightmost field header
2. Under "Hidden fields," click to unhide: Type, Status, Sub-issues progress, Assignees, Linked pull requests, Priority, and Estimate

**Grouping by Priority:**

1. Click the dropdown arrow next to the current view name
2. Click **Group**
3. Select **Priority**
4. Drag items between priority groups to change their priority

**Adding Field Sums:**

1. Click the dropdown arrow next to the current view name
2. Click **Field sum**
3. Select **Estimate**

**Saving the View:**

1. Click the dropdown arrow next to the current view name
2. Click **Save changes**

**Renaming the View:**

1. Click the dropdown arrow next to the current view name
2. Click **Rename view**
3. Enter the new name
4. Press Return

### Weekly Iteration Board View

Use Kanban board layout for viewing progress across status columns:

1. Click **New view** to the right of existing views
2. Click the dropdown arrow next to the current view name
3. Under "Layout," select **Board**
4. Rename the view (same process as above)
5. Add a filter for `iteration:@current` to show only current iteration items
6. Add field sum for **Estimate** (same steps as backlog view)
7. Save the view

### Team Roadmap

Display project items on a timeline using date and iteration fields:

1. Click **New view**
2. Click the dropdown arrow next to the current view name
3. Under "Layout," select **Roadmap**
4. Click **Markers** in the top right
5. Select which markers to display on your roadmap
6. Save the view
7. Rename the view as needed

For detailed roadmap customization, see the roadmap layout documentation.

## Configuring Built-in Automation

### Auto-add Workflow

Automatically add issues with specific labels to your project:

1. Navigate to your project
2. Click the menu icon in the top-right corner
3. Select **Workflows**
4. Under "Default workflows," click **Auto-add to project**
5. Click **Edit** in the top right
6. Under "Filters," select your repository
7. Enter filter criteria (example: `is:issue,pr label:question`)
8. Click **Save and turn on workflow**

### Item Status Automation

Set status to Todo when items are added:

1. Click the menu icon in the top-right corner
2. Select **Workflows**
3. Under "Default workflows," click **Item added to project**
4. Verify both `issues` and `pull requests` are selected next to **When**
5. Next to **Set**, select **Status:Todo**
6. Click the **Disabled** toggle to enable the workflow

Additional automation options and configurations are available in the Automating your project documentation.

## Viewing Charts and Insights

Create and customize charts using project items as data sources:

1. Navigate to your project
2. Click the insights button in the top-right corner
3. In the left menu, click **New chart**
4. Optionally click the chart name to rename it
5. Enter filters above the chart to modify the displayed data
6. Configure grouping, layout, and axis settings as needed
7. Click **Save changes**

See the About insights for Projects documentation for advanced charting options.

## Further Reading

- Best practices for Projects
- Managing items in your project
- Understanding fields
- Customizing views in your project
- Automating your project
- About insights for Projects
