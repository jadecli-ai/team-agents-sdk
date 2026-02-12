# Best Practices for Projects

> Source: https://docs.github.com/en/issues/planning-and-tracking-with-projects/learning-about-projects/best-practices-for-projects

## Overview

Use Projects to manage your work on GitHub, where your issues and pull requests live. This guide provides strategies for efficiently managing projects.

## Communicate Across Issues and Pull Requests

Leverage built-in communication features within GitHub:
- Use **@mentions** to alert individuals or teams about comments
- **Assign collaborators** to issues to clarify responsibility
- **Link related items** to show connections between issues and pull requests

## Break Down Large Issues Into Smaller Issues

Breaking a large issue into smaller issues makes the work more manageable and enables team members to work in parallel.

### Key Approaches

**Sub-Issues**: You can add sub-issues to an issue to quickly break down larger pieces of work into smaller issues. This creates hierarchical relationships and supports multiple nesting levels.

**Issue Types**: Classify work across repositories using issue type management alongside sub-issues.

**Dependencies**: Clearly define which issues are blocked by, or blocking, other issues using issue dependency features.

**Tracking Progress**: Use milestones or labels to show how smaller tasks connect to broader goals.

## Share Project Information

### Description and README

Use project descriptions and READMEs to communicate:
- Project purpose and objectives
- How to navigate and use different views
- Relevant links and contact information

Project READMEs support Markdown which allows you to use images and advanced formatting such as links, lists, and headers.

### Status Updates

Status updates allow you to mark the project with a status, such as "On track" or "At risk", set start and target dates, and share written updates with your team.

## Create Customized Views

Projects support multiple layout options for different perspectives:

### Table Layout
- View and manage backlog items
- Customize columns and sorting

### Board Layout
- Organize items by status or category
- Manage iterations and workflows
- Set column limits to maintain focus

### Roadmap Layout
- Visualize timelines
- Plan feature releases
- Track delivery schedules

### View Customization Options
- Filter by status to view unstated items
- Group by custom priority fields
- Sort by date fields
- Slice by assignee to assess capacity
- Show field sums for complexity estimates
- Apply column limits for focus

## Use Field Types for Metadata

Take advantage of the various field types to meet your needs and add metadata to your issues, pull requests, and draft issues for richer views.

### Available Field Types

**Date Fields**: Track target ship dates and deadlines

**Number Fields**: Measure task complexity or effort estimates

**Single Select Fields**:
- Track priority levels (Low, Medium, High)
- Classify project phases
- Since the values are selected from a preset list, you can easily group or filter to focus on items with a specific value

**Text Fields**: Add quick notes or descriptions

**Iteration Fields**:
- Use an iteration field to schedule work or create a timeline
- View completed work from past iterations
- Support breaks for time away
- Enable velocity planning and team reflection

## Use Automation

You can automate tasks to spend less time on busy work and more time on the project itself.

### Built-In Workflows
- Automatically set status to "Done" when issues close
- Archive items meeting specified criteria
- Add items from repositories matching filters

### Advanced Automation
- **GitHub Actions**: Create workflows for routine tasks
- **GraphQL API**: Automate project management programmatically
- Example: Auto-add pull requests marked "ready for review" with "needs review" status

## Create Charts and Insights

You can use insights for Projects to view, create, and customize charts that use the items added to your project as their source data.

### Capabilities
- View default charts with applied filters
- Create custom charts
- Set filters, chart type, and displayed information
- Share charts with all project viewers
- Visualize progress and team performance

## Create Project Templates

You can create project templates for your organization, or set a project as a template, to share a pre-configured project with other people in your organization.

### Template Contents
- Configured views
- Custom fields
- Draft issues and associated fields
- Pre-configured workflows (excludes auto-add workflows)
- Insights and charts

Benefits: Standardize workflows and reduce setup time for new projects.

## Link Projects to Teams and Repositories

### Team Integration
When you add a project to a team, that project is listed on the team's projects page, making it easier for members to identify which projects a particular team uses.

### Repository Integration
Add projects to repositories owned by the same user or organization, improving discoverability.

## Maintain a Single Source of Truth

To prevent information from getting out of sync, maintain a single source of truth. For example, track a target ship date in a single location instead of spread across multiple fields.

### Automatic Synchronization
Projects automatically stay up to date with GitHub data, such as assignees, milestones, and labels. When one of these fields changes in an issue or pull request, the change is automatically reflected in your project.

This reduces manual updates and prevents data inconsistency.

## Further Reading

- About Projects
- Quickstart for Projects
