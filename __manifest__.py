# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.
{
    'name': 'Senegal Government Project Management',
    'version': '18.0.1.0.0',
    'summary': 'Government Project Management for Senegal',
    'description': """
        This module provides a comprehensive system for managing government projects in Senegal.
        It integrates projects with National Vision, Strategic Axes, Government Decisions, and Finance Laws.
        Includes QR code functionality for all records and comprehensive reporting features.
    """,
    'category': 'Project',
    'author': 'Senegal Government',
    'website': 'https://www.gouv.sn',
    'license': 'LGPL-3',
    'depends': [
        'base',
        'project',
        'web',
        'mail',
        'account',
        'hr',
    ],
    'data': [
        # Security
        'security/security.xml',
        'security/ir.model.access.csv',
        
        # Data
        'data/government_vision_data.xml',
        
        # Views
        'views/government_ministry_views.xml',
        'views/government_strategic_axis_views.xml',
        'views/government_national_vision_views.xml',
        'views/government_decision_views.xml',
        'views/government_finance_law_views.xml',
        'views/project_government_project_views.xml',
        'views/project_government_task_views.xml',
        'views/project_government_report_views.xml',
        'views/menu_views.xml',
        
        # Reports
        'reports/project_report_templates.xml',
        'reports/project_reports.xml',
        
        # Wizards
        'wizards/qr_code_wizard_view.xml',
        'wizards/project_report_wizard_view.xml',
        'wizards/task_timesheet_wizard_view.xml',
    ],
    'demo': [
        'data/demo_data.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'senegal_gov_project_management/static/src/js/qr_code_generator.js',
            'senegal_gov_project_management/static/src/scss/government_project_styles.scss',
            'senegal_gov_project_management/static/src/xml/qr_code_widget.xml',
        ],
        'web.report_assets_common': [
            'senegal_gov_project_management/static/src/scss/report_styles.scss',
        ],
    },

    'installable': True,
    'application': True,
    'auto_install': False,
    'images': ['static/description/banner.png'],
}