import json

# Define the 10 Real Product Prompts
PRODUCT_PROMPTS = [
    {
        "id": "prod-1",
        "name": "CRM System",
        "prompt": "Build a CRM with login, contacts, dashboard, role-based access, and premium plan with payments. Admins can see analytics."
    },
    {
        "id": "prod-2",
        "name": "E-Commerce Platform",
        "prompt": "Build an e-commerce app with product listings, search, shopping cart, checkout, payments, and order history. Sellers can manage products, admins can see sales metrics."
    },
    {
        "id": "prod-3",
        "name": "Task Management Board",
        "prompt": "Build a project board like Trello with columns, tasks, assignees, comments, drag-and-drop simulation, and premium tier for unlimited boards."
    },
    {
        "id": "prod-4",
        "name": "Customer Support Ticket Desk",
        "prompt": "Build a support ticketing system with customer portal, agent view, ticket assignment, status tracking, SLA logic, and admin reporting."
    },
    {
        "id": "prod-5",
        "name": "Hotel Room Booking App",
        "prompt": "Build a hotel booking platform with search, room availability check, booking creation, payments, and admin room management."
    },
    {
        "id": "prod-6",
        "name": "Developer API Analytics Dashboard",
        "prompt": "Build an API analytics tracker with request logger, dashboard showing response times, usage limits gating for free tier, and alert setup."
    },
    {
        "id": "prod-7",
        "name": "Fitness Workout Planner",
        "prompt": "Build a workout app with exercise log, routine planner, progress charts, premium personal trainer chat feature, and user profile."
    },
    {
        "id": "prod-8",
        "name": "Library Catalog Manager",
        "prompt": "Build a library book management app with borrow/return tracking, fine payments, search by author/genre, and librarian dashboard."
    },
    {
        "id": "prod-9",
        "name": "Social Media Scheduler",
        "prompt": "Build a social media post scheduler with draft creation, queue preview, premium automatic posting simulation, and content category analytics."
    },
    {
        "id": "prod-10",
        "name": "Inventory Tracking System",
        "prompt": "Build an inventory management system with stock level tracking, low stock alerts, supplier information, purchase order approvals, and role access."
    }
]

# Define the 10 Edge Cases
EDGE_PROMPTS = [
    {
        "id": "edge-1",
        "name": "Vague: Store website",
        "prompt": "Make a website for a store where people do things."
    },
    {
        "id": "edge-2",
        "name": "Conflicting: Public but private database",
        "prompt": "Build a public database where anyone can read all messages, but make sure only the sender and admin can see them."
    },
    {
        "id": "edge-3",
        "name": "Incomplete: Bare roles & payments",
        "prompt": "Make an app with payment integration and user roles."
    },
    {
        "id": "edge-4",
        "name": "Conflicting: Premium only, but free/guest",
        "prompt": "Create a dashboard for premium subscribers only, but it should be free and accessible to guests without signing in."
    },
    {
        "id": "edge-5",
        "name": "Vague: Items & Analytics",
        "prompt": "An app for managing items with some analytics."
    },
    {
        "id": "edge-6",
        "name": "Incomplete: Dashboard only",
        "prompt": "Build a dashboard."
    },
    {
        "id": "edge-7",
        "name": "Conflicting: Encrypted but editable by Admin",
        "prompt": "A secure messaging app where messages are fully encrypted and stored in DB, but admins can edit any user's messages directly in the dashboard."
    },
    {
        "id": "edge-8",
        "name": "Incomplete: Booking system",
        "prompt": "Make a booking system."
    },
    {
        "id": "edge-9",
        "name": "Vague: Tracks stuff",
        "prompt": "Build a system that tracks stuff for a company."
    },
    {
        "id": "edge-10",
        "name": "Conflicting: Free buy with payment checkout",
        "prompt": "Build an e-commerce cart where users can buy items for free, but it must process payments for each checkout."
    }
]

ALL_PROMPTS = PRODUCT_PROMPTS + EDGE_PROMPTS

def get_prebuilt_mock_schema(prompt_id: str) -> dict:
    """
    Returns a comprehensive, high-quality, valid app configuration JSON representation 
    for the standard dataset prompts. This is used for out-of-the-box demo mode.
    """
    # Standard CRM schema (prod-1)
    if prompt_id == "prod-1":
        return {
            "app_name": "SleekCRM",
            "db_schema": {
                "tables": [
                    {
                        "name": "users",
                        "columns": [
                            {"name": "id", "type": "INTEGER", "is_primary_key": True, "is_nullable": False, "is_unique": True},
                            {"name": "email", "type": "TEXT", "is_primary_key": False, "is_nullable": False, "is_unique": True},
                            {"name": "password_hash", "type": "TEXT", "is_primary_key": False, "is_nullable": False, "is_unique": False},
                            {"name": "role", "type": "TEXT", "is_primary_key": False, "is_nullable": False, "is_unique": False, "default_value": "Member"},
                            {"name": "subscription", "type": "TEXT", "is_primary_key": False, "is_nullable": False, "is_unique": False, "default_value": "free"}
                        ],
                        "indexes": ["email"],
                        "foreign_keys": []
                    },
                    {
                        "name": "contacts",
                        "columns": [
                            {"name": "id", "type": "INTEGER", "is_primary_key": True, "is_nullable": False, "is_unique": True},
                            {"name": "name", "type": "TEXT", "is_primary_key": False, "is_nullable": False, "is_unique": False},
                            {"name": "email", "type": "TEXT", "is_primary_key": False, "is_nullable": False, "is_unique": False},
                            {"name": "phone", "type": "TEXT", "is_primary_key": False, "is_nullable": True, "is_unique": False},
                            {"name": "company", "type": "TEXT", "is_primary_key": False, "is_nullable": True, "is_unique": False},
                            {"name": "owner_id", "type": "INTEGER", "is_primary_key": False, "is_nullable": False, "is_unique": False}
                        ],
                        "indexes": ["owner_id"],
                        "foreign_keys": [
                            {"column": "owner_id", "reference_table": "users", "reference_column": "id"}
                        ]
                    },
                    {
                        "name": "deals",
                        "columns": [
                            {"name": "id", "type": "INTEGER", "is_primary_key": True, "is_nullable": False, "is_unique": True},
                            {"name": "title", "type": "TEXT", "is_primary_key": False, "is_nullable": False, "is_unique": False},
                            {"name": "amount", "type": "REAL", "is_primary_key": False, "is_nullable": False, "is_unique": False},
                            {"name": "stage", "type": "TEXT", "is_primary_key": False, "is_nullable": False, "is_unique": False, "default_value": "Lead"},
                            {"name": "contact_id", "type": "INTEGER", "is_primary_key": False, "is_nullable": False, "is_unique": False}
                        ],
                        "indexes": ["contact_id"],
                        "foreign_keys": [
                            {"column": "contact_id", "reference_table": "contacts", "reference_column": "id"}
                        ]
                    }
                ]
            },
            "api_schema": {
                "endpoints": [
                    {
                        "path": "/api/auth/register",
                        "method": "POST",
                        "description": "Registers a new user",
                        "auth_required": False,
                        "allowed_roles": [],
                        "request_body": [
                            {"name": "email", "type": "string", "required": True},
                            {"name": "password", "type": "string", "required": True}
                        ],
                        "response_schema": [
                            {"name": "id", "type": "integer"},
                            {"name": "email", "type": "string"},
                            {"name": "role", "type": "string"}
                        ],
                        "db_operations": [
                            {"table": "users", "action": "INSERT"}
                        ]
                    },
                    {
                        "path": "/api/auth/login",
                        "method": "POST",
                        "description": "Authenticates user and returns session",
                        "auth_required": False,
                        "allowed_roles": [],
                        "request_body": [
                            {"name": "email", "type": "string", "required": True},
                            {"name": "password", "type": "string", "required": True}
                        ],
                        "response_schema": [
                            {"name": "token", "type": "string"},
                            {"name": "role", "type": "string"},
                            {"name": "subscription", "type": "string"}
                        ],
                        "db_operations": [
                            {"table": "users", "action": "SELECT"}
                        ]
                    },
                    {
                        "path": "/api/contacts",
                        "method": "GET",
                        "description": "Gets all contacts for the user",
                        "auth_required": True,
                        "allowed_roles": ["Admin", "Member"],
                        "db_operations": [
                            {"table": "contacts", "action": "SELECT", "conditions": "owner_id = user.id"}
                        ]
                    },
                    {
                        "path": "/api/contacts",
                        "method": "POST",
                        "description": "Creates a contact",
                        "auth_required": True,
                        "allowed_roles": ["Admin", "Member"],
                        "request_body": [
                            {"name": "name", "type": "string", "required": True},
                            {"name": "email", "type": "string", "required": True},
                            {"name": "phone", "type": "string", "required": False},
                            {"name": "company", "type": "string", "required": False}
                        ],
                        "db_operations": [
                            {"table": "contacts", "action": "INSERT"}
                        ]
                    },
                    {
                        "path": "/api/analytics/sales",
                        "method": "GET",
                        "description": "Calculates sales analytics pipeline metrics",
                        "auth_required": True,
                        "allowed_roles": ["Admin"],
                        "db_operations": [
                            {"table": "deals", "action": "SELECT"}
                        ]
                    },
                    {
                        "path": "/api/subscription/upgrade",
                        "method": "POST",
                        "description": "Upgrades user to premium plan",
                        "auth_required": True,
                        "allowed_roles": ["Admin", "Member"],
                        "db_operations": [
                            {"table": "users", "action": "UPDATE", "conditions": "id = user.id"}
                        ]
                    }
                ]
            },
            "ui_schema": {
                "pages": [
                    {
                        "name": "Dashboard",
                        "route": "/dashboard",
                        "auth_required": True,
                        "allowed_roles": ["Admin", "Member"],
                        "layout": "sidebar",
                        "components": [
                            {
                                "id": "welcome_card",
                                "type": "StatCard",
                                "title": "CRM Summary",
                                "props": {"text": "Manage contacts, view sales dashboard, upgrade to premium."}
                            },
                            {
                                "id": "analytics_link",
                                "type": "Button",
                                "title": "Go to Admin Analytics Panel",
                                "props": {"variant": "primary"},
                                "actions": [{"trigger": "click", "action_type": "navigate", "target": "/analytics"}]
                            }
                        ]
                    },
                    {
                        "name": "Contacts",
                        "route": "/contacts",
                        "auth_required": True,
                        "allowed_roles": ["Admin", "Member"],
                        "layout": "sidebar",
                        "components": [
                            {
                                "id": "contact_form",
                                "type": "Form",
                                "title": "Add Contact",
                                "props": {
                                    "fields": [
                                        {"name": "name", "label": "Full Name", "type": "text"},
                                        {"name": "email", "label": "Email Address", "type": "email"},
                                        {"name": "phone", "label": "Phone Number", "type": "text"},
                                        {"name": "company", "label": "Company", "type": "text"}
                                    ]
                                },
                                "actions": [
                                    {"trigger": "submit", "action_type": "api_call", "target": "/api/contacts", "payload": {"method": "POST"}}
                                ]
                            },
                            {
                                "id": "contact_table",
                                "type": "Table",
                                "title": "My Contacts",
                                "props": {
                                    "columns": ["id", "name", "email", "phone", "company"]
                                },
                                "api_binding": {
                                    "path": "/api/contacts",
                                    "method": "GET",
                                    "bind_to": "table_data"
                                }
                            }
                        ]
                    },
                    {
                        "name": "Analytics",
                        "route": "/analytics",
                        "auth_required": True,
                        "allowed_roles": ["Admin"],
                        "layout": "sidebar",
                        "components": [
                            {
                                "id": "sales_chart",
                                "type": "Chart",
                                "title": "Admin Sales Pipeline Metrics",
                                "props": {"chart_type": "bar", "metric": "amount"},
                                "api_binding": {
                                    "path": "/api/analytics/sales",
                                    "method": "GET",
                                    "bind_to": "chart_data"
                                }
                            }
                        ]
                    },
                    {
                        "name": "Billing",
                        "route": "/billing",
                        "auth_required": True,
                        "allowed_roles": ["Admin", "Member"],
                        "layout": "sidebar",
                        "components": [
                            {
                                "id": "premium_status",
                                "type": "StatCard",
                                "title": "Subscription Mode",
                                "props": {"text": "Upgrade to Premium to get access to advanced contact triggers."}
                            },
                            {
                                "id": "upgrade_button",
                                "type": "Button",
                                "title": "Upgrade to Premium ($19/mo)",
                                "props": {"variant": "success"},
                                "actions": [
                                    {"trigger": "click", "action_type": "api_call", "target": "/api/subscription/upgrade", "payload": {"plan": "premium"}}
                                ]
                            }
                        ]
                    }
                ]
            },
            "auth_schema": {
                "roles": ["Admin", "Member", "Anonymous"],
                "permissions": {
                    "Admin": ["contacts:read", "contacts:write", "analytics:read", "billing:upgrade"],
                    "Member": ["contacts:read", "contacts:write", "billing:upgrade"],
                    "Anonymous": []
                },
                "gated_features": [
                    {"feature_name": "Sales Analytics Panel", "required_role": "Admin"},
                    {"feature_name": "Premium Auto-Responder Trigger", "required_subscription": "premium"}
                ]
            },
            "logic_schema": {
                "rules": [
                    {
                        "id": "gate_analytics_api",
                        "trigger_event": "api:before_call:/api/analytics/sales",
                        "conditions": ["user.role != 'Admin'"],
                        "action": "DENY",
                        "error_message": "Access Denied: Only Admins can view analytics data."
                    },
                    {
                        "id": "premium_contact_gate",
                        "trigger_event": "api:before_call:/api/contacts:POST",
                        "conditions": ["user.subscription != 'premium'", "count(contacts) >= 3"],
                        "action": "DENY",
                        "error_message": "Upgrade Required: Free plan is limited to 3 contacts. Upgrade to premium to add more."
                    }
                ]
            }
        }
    
    # Generic fallback dynamic mock response builder for any other prompt
    # Ensure it's valid JSON matching the AppConfig schema
    name_clean = "App" + prompt_id.replace("-", "").capitalize()
    return {
        "app_name": name_clean,
        "db_schema": {
            "tables": [
                {
                    "name": "users",
                    "columns": [
                        {"name": "id", "type": "INTEGER", "is_primary_key": True, "is_nullable": False, "is_unique": True},
                        {"name": "email", "type": "TEXT", "is_primary_key": False, "is_nullable": False, "is_unique": True},
                        {"name": "role", "type": "TEXT", "is_primary_key": False, "is_nullable": False, "is_unique": False, "default_value": "Member"}
                    ],
                    "indexes": [],
                    "foreign_keys": []
                },
                {
                    "name": "items",
                    "columns": [
                        {"name": "id", "type": "INTEGER", "is_primary_key": True, "is_nullable": False, "is_unique": True},
                        {"name": "name", "type": "TEXT", "is_primary_key": False, "is_nullable": False, "is_unique": False},
                        {"name": "details", "type": "TEXT", "is_primary_key": False, "is_nullable": True, "is_unique": False}
                    ],
                    "indexes": [],
                    "foreign_keys": []
                }
            ]
        },
        "api_schema": {
            "endpoints": [
                {
                    "path": "/api/items",
                    "method": "GET",
                    "description": "Fetch items list",
                    "auth_required": True,
                    "allowed_roles": ["Admin", "Member"],
                    "db_operations": [{"table": "items", "action": "SELECT"}]
                },
                {
                    "path": "/api/items",
                    "method": "POST",
                    "description": "Add new item",
                    "auth_required": True,
                    "allowed_roles": ["Admin"],
                    "request_body": [{"name": "name", "type": "string", "required": True}],
                    "db_operations": [{"table": "items", "action": "INSERT"}]
                }
            ]
        },
        "ui_schema": {
            "pages": [
                {
                    "name": "Dashboard",
                    "route": "/dashboard",
                    "auth_required": True,
                    "allowed_roles": ["Admin", "Member"],
                    "layout": "sidebar",
                    "components": [
                        {
                            "id": "welcome_banner",
                            "type": "Heading",
                            "title": "Welcome to " + name_clean,
                            "props": {"text": "Simple workspace app"}
                        },
                        {
                            "id": "items_grid",
                            "type": "Table",
                            "title": "Available Items",
                            "props": {"columns": ["id", "name", "details"]},
                            "api_binding": {"path": "/api/items", "method": "GET", "bind_to": "table_data"}
                        }
                    ]
                }
            ]
        },
        "auth_schema": {
            "roles": ["Admin", "Member", "Anonymous"],
            "permissions": {"Admin": ["items:read", "items:write"], "Member": ["items:read"], "Anonymous": []},
            "gated_features": []
        },
        "logic_schema": {
            "rules": [
                {
                    "id": "write_gate",
                    "trigger_event": "api:before_call:/api/items:POST",
                    "conditions": ["user.role != 'Admin'"],
                    "action": "DENY",
                    "error_message": "Access Denied: Only admins can add items."
                }
            ]
        }
    }
