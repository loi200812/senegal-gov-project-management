# Senegal Government Project Management

A comprehensive Odoo module for managing government projects in Senegal, integrating with National Vision, Strategic Axes, Government Decisions, and Finance Laws.

## Features

- **Government Project Management**: Complete project lifecycle management tailored for government needs
- **National Vision Integration**: Link projects to Senegal's National Vision and Strategic Axes
- **Government Decision Tracking**: Connect projects to official government decisions
- **Finance Law Integration**: Align projects with finance laws and budget allocations
- **QR Code Generation**: Generate QR codes for all records for easy tracking and reference
- **Comprehensive Reporting**: Detailed reports on project progress, budgets, and outcomes
- **Task Management**: Government-specific task management with timesheet capabilities
- **Ministry Integration**: Organize projects by government ministries

## Module Structure

```
senegal_gov_project_management/
├── __init__.py
├── __manifest__.py
├── controllers/          # Web controllers for custom routes
├── data/                 # Initial data and demo data
├── models/               # Core business logic models
├── reports/              # Report templates and configurations
├── security/             # Access control and security rules
├── static/               # CSS, JavaScript, and image assets
├── views/                # XML view definitions
└── wizards/              # Wizard dialogs for user interactions
```

## Installation

1. Copy this module to your Odoo addons directory
2. Update the app list in Odoo
3. Install the "Senegal Government Project Management" module

## Dependencies

- base
- project
- web
- mail
- account
- hr

## Configuration

After installation, configure:
1. Government ministries
2. National vision and strategic axes
3. User access rights and security groups
4. Report templates (if needed)

## Usage

### Creating Projects
1. Navigate to Government Projects → Projects
2. Create a new project with government-specific information
3. Link to relevant ministries, strategic axes, and decisions
4. Set up tasks and assign team members

### Generating Reports
1. Use the Project Report Wizard to generate comprehensive reports
2. QR codes can be generated for any record using the QR Code Wizard
3. Export reports in various formats (PDF, Excel, etc.)

### Managing Tasks
1. Create tasks within projects
2. Track time using the Task Timesheet Wizard
3. Monitor progress through various views and reports

## Technical Details

- **Version**: 18.0.1.0.0
- **Category**: Project Management
- **License**: LGPL-3
- **Author**: Senegal Government
- **Website**: https://www.gouv.sn

## Support

For support and contributions, please contact the Senegal Government IT Department.

## License

This module is licensed under LGPL-3. See LICENSE file for full copyright and licensing details.
