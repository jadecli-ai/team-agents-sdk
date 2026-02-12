# Planning and Tracking Work for Your Team or Project

> Source: https://docs.github.com/en/issues/tracking-your-work-with-issues/learning-about-issues/planning-and-tracking-work-for-your-team-or-project

## Introduction

GitHub repositories, issues, projects, and other tools enable work planning and tracking for individual projects or cross-functional teams. This guide covers creating and setting up repositories for collaboration, establishing issue templates and forms, opening issues with task breakdowns, and organizing work through projects.

## Creating a Repository

When launching a new project, initiative, or feature, creating a repository is the first step. Repositories house project files and provide collaboration and work management spaces.

### Repository Use Cases

**Product repositories:** Organizations tracking work around specific products maintain repositories containing code, documentation, product health reports, and future plans.

**Project repositories:** Individual or collaborative projects use dedicated repositories. Organizations tracking short-lived initiatives (such as consulting firms) need repositories for project health reporting and resource allocation across different projects.

**Team repositories:** Organizations grouping people into teams with scattered code across multiple repositories benefit from team-specific repositories as centralized work tracking hubs.

**Personal repositories:** Individual repositories track personal work, plan future tasks, save notes, and enable collaboration when adding team members.

Create multiple repositories when requiring different access permissions for source code versus issue tracking.

## Communicating Repository Information

**README.md** files introduce teams or projects and communicate essential information. As visitors' first encounter with repositories, READMEs should include project details, getting started information, and team contact methods.

**CONTRIBUTING.md** files contain guidelines for user and contributor engagement, including bug fix issue procedures and improvement requests.

## Creating Issue Templates

Issues track different work types across cross-functional teams and projects while gathering external information. Common use cases include:

- **Release tracking:** Monitor release progress and launch-day completion steps
- **Large initiatives:** Track progress on major initiatives linked to smaller issues
- **Feature requests:** Team members and users request product or project improvements
- **Bugs:** Team members and users report bugs

Issue templates and forms create standardized template selections for repository issue creation.

## Opening Issues and Breaking Down Work

Issues organize and track work.

### Sub-Issues

Sub-issues break larger work pieces into smaller issues, creating hierarchical issue relationships. Multiple sub-issue levels accurately represent projects with required detail levels.

Issue types classify work across organizational repositories (tasks, bugs, features).

### Task Lists

Task lists break larger issues into smaller tasks and track issues toward larger goals. Task lists in issue bodies display task completion counts and automatically mark checkboxes when linked issues close.

### Labels

Labels categorize issues, pull requests, and discussions. GitHub provides default labels for new repositories that can be edited or deleted. Labels track project goals, bugs, work types, and issue status.

After creating labels, apply them to any repository issue, pull request, or discussion. Filter issues and pull requests by label to find associated work (for example, filtering for both `front-end` and `bug` labels finds front-end bugs).

## Showing Which Issues Block Other Work

Issue dependencies clearly display and communicate which issues are blocked by or blocking other issues, streamlining coordination, preventing bottlenecks, and increasing team transparency.

## Understanding New Issues (Copilot)

GitHub Copilot helps quickly understand unfamiliar or complex issue context, history, and key information for faster, more confident startup.

### Reviewing Issues

1. Navigate to a GitHub issue
2. Click the Copilot icon next to the search bar in the top right
3. The GitHub Copilot Chat panel opens
4. For new conversations, click the plus sign icon
5. In the "Ask Copilot" box, type questions and press Enter

Example questions:
- "Summarize the main points of this issue"
- "What's the goal of this issue?"

### Understanding History and Comments

Issues contain discussion and decision histories providing important context. Use Copilot to summarize conversations, identify key points (proposed solutions, unanswered questions), or highlight made decisions.

### Clarifying Technical Terms

Issues mention technical terms, code, or files requiring clarification. Ask Copilot about file or function purposes, or specific term meanings.

### Getting Next Step Suggestions

After understanding issue context, Copilot suggests how to proceed. Ask for approach suggestions for bug fixes or feature implementation.

## Making Decisions as a Team

Issues and discussions enable team communication and decision-making regarding planned improvements or project priorities. Issues suit specific detail discussions (bug or performance reports, quarterly planning, new initiative design). Discussions suit open-ended brainstorming or feedback outside codebases and across repositories.

## Using Labels to Highlight Project Goals and Status

Labels categorize issues, pull requests, and discussions for a repository. GitHub provides default labels for every new repository that can be edited or deleted. Labels track project goals, bugs, work types, and issue status.

## Adding Issues to a Project

GitHub projects plan and track team work. Projects are customizable spreadsheets integrating with issues and pull requests on GitHub, automatically updating with GitHub information. Customize layouts by filtering, sorting, and grouping issues and pull requests.

Projects support multiple view layouts:
- **Table views**: Displaying Title, Assignees, Status, Labels, and Notes columns
- **Board views**: Organizing issues into columns like "No Status," "Todo," "In Progress," and "Done"

## Next Steps

- About repositories
- Learning about Projects
- Changing the layout of a view
- Tracking your work with issues
- About issue and pull request templates
- Managing issue types in an organization
- Managing labels
- Adding sub-issues
- About tasklists
