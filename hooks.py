app_name = "woven_app"
app_title = "Woven App"
app_publisher = "hitc technologies"
app_description = "A app for woven industry"
app_email = "hitctechnologies@gmail.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "woven_app",
# 		"logo": "/assets/woven_app/logo.png",
# 		"title": "Woven App",
# 		"route": "/woven_app",
# 		"has_permission": "woven_app.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/woven_app/css/woven_app.css"
# app_include_js = "/assets/woven_app/js/woven_app.js"
# include js in doctype views
doctype_js = {
    "Quotation": "public/js/quotation.js",
    "Sales Order": "public/js/customer_credit.js",
    "Blanket Order":  "public/js/valuation_rate.js",
    "Sales Invoice": "public/js/item_price.js",
    "Work Order":"public/js/work_order.js",
     "Item" : "public/js/construction_child_table.js", 
     "BOM": "public/js/bom.js",
     "Purchase Order" : "public/js/purchase_order.js",
     "Job Card" : "public/js/job_card.js" ,
     "Job Offer" : "public/js/offer_letter.js" ,
    "Customer" : "public/js/customer_ceo_approval.js",
}
doc_events = {
    "Item": {
        "validate": "woven_app.api.item_master.create_matrix_requirement"
    },
    # "Sales Order": {
    #     # Trigger when Sales Order is updated — refresh manufacturing progress HTML
    #     "on_submit": "woven_app.api.job_card.update_sales_order_progress"
    # },
    "Job Card": {
        # Trigger when Job Card is created, updated, submitted, or cancelled — update Sales Order progress
        "after_insert":"woven_app.api.job_card.update_sales_order_progress",
        "on_update": "woven_app.api.job_card.update_sales_order_progress",
        "on_submit": "woven_app.api.job_card.update_sales_order_progress",
        "validate": "woven_app.api.job_card.update_sales_order_progress",
        "after_cancel": "woven_app.api.job_card.update_sales_order_progress",
         "before_save": "woven_app.api.job_card.add_scrap_items",
    },
    # "Work Order": {
    #     "on_submit": "woven_app.api.job_card.add_scrap_items"
    # },

    "Batch": {
        "validate": "woven_app.api.batch.generate_batch_barcode"
    }
}    
# doc_events = {
#     "Quotation": {
#         "before_save": "woven_app.woven_app.events.quotation.before_save"
#     }

# }
fixtures=[
    "Workflow",
    "Workflow State",
    "Workflow Action Master",
    # "Notification",
    "Print Format",
    "Item" ,

]

# include js, css files in header of web template
# web_include_css = "/assets/woven_app/css/woven_app.css"
# web_include_js = "/assets/woven_app/js/woven_app.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "woven_app/public/scss/website"

# include js, css files in header of web form
# webform_include_js = {"doctype": "public/js/doctype.js"}
# webform_include_css = {"doctype": "public/css/doctype.css"}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "woven_app/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "woven_app.utils.jinja_methods",
# 	"filters": "woven_app.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "woven_app.install.before_install"
# after_install = "woven_app.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "woven_app.uninstall.before_uninstall"
# after_uninstall = "woven_app.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "woven_app.utils.before_app_install"
# after_app_install = "woven_app.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "woven_app.utils.before_app_uninstall"
# after_app_uninstall = "woven_app.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "woven_app.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
#     "Item": {
#         "on_submit": "woven_app.api.item_master_on_submit"
#     }
# }


# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"woven_app.tasks.all"
# 	],
# 	"daily": [
# 		"woven_app.tasks.daily"
# 	],
# 	"hourly": [
# 		"woven_app.tasks.hourly"
# 	],
# 	"weekly": [
# 		"woven_app.tasks.weekly"
# 	],
# 	"monthly": [
# 		"woven_app.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "woven_app.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "woven_app.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "woven_app.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Request Events
# ----------------
# before_request = ["woven_app.utils.before_request"]
# after_request = ["woven_app.utils.after_request"]

# Job Events
# ----------
# before_job = ["woven_app.utils.before_job"]
# after_job = ["woven_app.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"woven_app.auth.validate"
# ]

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

