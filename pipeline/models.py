from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

# Common Sub-Models
class FieldDef(BaseModel):
    name: str
    type: str  # string, integer, float, boolean, datetime
    required: bool = True
    description: Optional[str] = None

# DB Schema Models
class DbColumn(BaseModel):
    name: str
    type: str  # INTEGER, TEXT, REAL, BOOLEAN, DATETIME
    is_primary_key: bool = False
    is_nullable: bool = True
    is_unique: bool = False
    default_value: Optional[Any] = None

class DbForeignKey(BaseModel):
    column: str
    reference_table: str
    reference_column: str

class DbTable(BaseModel):
    name: str
    columns: List[DbColumn]
    indexes: List[str] = []
    foreign_keys: List[DbForeignKey] = []

class DbSchema(BaseModel):
    tables: List[DbTable]

# API Schema Models
class DbOperation(BaseModel):
    table: str
    action: str  # SELECT, INSERT, UPDATE, DELETE
    conditions: Optional[str] = None  # e.g., "id = request.body.id" or "owner_id = user.id"

class ApiEndpoint(BaseModel):
    path: str
    method: str  # GET, POST, PUT, DELETE
    description: str
    auth_required: bool = True
    allowed_roles: List[str] = []
    request_body: Optional[List[FieldDef]] = None
    response_schema: Optional[List[FieldDef]] = None
    db_operations: List[DbOperation] = []

class ApiSchema(BaseModel):
    endpoints: List[ApiEndpoint]

# UI Schema Models
class ApiBinding(BaseModel):
    path: str
    method: str
    params: Optional[Dict[str, str]] = None
    bind_to: str  # e.g. "table_data" or "form_fields"

class UiAction(BaseModel):
    trigger: str  # click, submit, change
    action_type: str  # navigate, api_call, open_modal, close_modal
    target: str  # e.g. page path, API endpoint path, component ID
    payload: Optional[Dict[str, Any]] = None

class UiComponent(BaseModel):
    id: str
    type: str  # Table, Form, StatCard, Chart, Button, Text, Heading
    title: str
    props: Dict[str, Any] = {}
    api_binding: Optional[ApiBinding] = None
    actions: List[UiAction] = []

class UiPage(BaseModel):
    name: str
    route: str
    auth_required: bool = True
    allowed_roles: List[str] = []
    layout: str = "sidebar"  # sidebar, full-width, clean
    components: List[UiComponent]

class UiSchema(BaseModel):
    pages: List[UiPage]

# Auth Schema Models
class GatedFeature(BaseModel):
    feature_name: str
    required_role: Optional[str] = None
    required_subscription: Optional[str] = None

class AuthSchema(BaseModel):
    roles: List[str]
    permissions: Dict[str, List[str]]  # e.g. {"Admin": ["contacts:read", "contacts:write"]}
    gated_features: List[GatedFeature] = []

# Logic Schema Models
class LogicRule(BaseModel):
    id: str
    trigger_event: str  # e.g. "api:before_create:contacts", "ui:click:upgrade_btn"
    conditions: List[str]  # e.g. ["user.subscription != 'premium'", "request.body.amount > 1000"]
    action: str  # ALLOW, DENY, ERROR, MOCK_PAYMENT
    error_message: Optional[str] = None

class LogicSchema(BaseModel):
    rules: List[LogicRule]

# Master Application Schema Configuration
class AppConfig(BaseModel):
    app_name: str
    db_schema: DbSchema
    api_schema: ApiSchema
    ui_schema: UiSchema
    auth_schema: AuthSchema
    logic_schema: LogicSchema

# Intent Extraction Models (Stage 1 Intermediate Representation)
class EntityIntent(BaseModel):
    name: str
    fields: List[FieldDef]
    relationships: List[str] = []  # e.g., "belongs_to users", "has_many contacts"

class UserRoleIntent(BaseModel):
    role_name: str
    permissions: List[str]
    is_premium_restricted: bool = False

class FeatureIntent(BaseModel):
    name: str
    description: str
    requires_auth: bool = True
    gated_by_role: Optional[str] = None
    gated_by_subscription: Optional[str] = None

class AppIntent(BaseModel):
    app_name: str
    description: str
    entities: List[EntityIntent]
    roles: List[UserRoleIntent]
    features: List[FeatureIntent]
    business_logic_rules: List[str] = []

# System Design Layer Models (Stage 2 Intermediate Representation)
class DesignEntity(BaseModel):
    name: str
    description: str
    fields: List[FieldDef]
    relationships: List[str] = []
    allowed_operations: Dict[str, List[str]] = {} # e.g. {"read": ["Admin"], "write": ["Admin"]}

class DesignFlow(BaseModel):
    name: str
    trigger: str
    steps: List[str]
    affected_entities: List[str] = []

class SystemDesign(BaseModel):
    app_name: str
    entities: List[DesignEntity]
    flows: List[DesignFlow]
    roles: List[UserRoleIntent]

