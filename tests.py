import unittest
import json
from pipeline.models import AppConfig, DbSchema, ApiSchema, UiSchema, AuthSchema, LogicSchema, DbTable, DbColumn, ApiEndpoint, DbOperation, UiPage, UiComponent, LogicRule
from pipeline.validator import validate_app_config
from pipeline.repair_engine import programmatic_repair
from runtime.mock_db import MockDatabase
from runtime.mock_api import MockApiRouter
from runtime.simulator import AppSimulator

class TestAppForgeCompiler(unittest.TestCase):
    """Unit test suite for the AppForge Compiler modules (Validators, Repair, SQLite DB, API, Simulator)."""
    
    def setUp(self):
        # Create a simple valid AppConfig mock object
        self.valid_config = AppConfig(
            app_name="TestApp",
            db_schema=DbSchema(tables=[
                DbTable(
                    name="users",
                    columns=[
                        DbColumn(name="id", type="INTEGER", is_primary_key=True, is_nullable=False, is_unique=True),
                        DbColumn(name="email", type="TEXT", is_primary_key=False, is_nullable=False, is_unique=True),
                        DbColumn(name="role", type="TEXT", is_primary_key=False, is_nullable=False, is_unique=False, default_value="Member")
                    ],
                    indexes=["email"],
                    foreign_keys=[]
                ),
                DbTable(
                    name="contacts",
                    columns=[
                        DbColumn(name="id", type="INTEGER", is_primary_key=True, is_nullable=False, is_unique=True),
                        DbColumn(name="name", type="TEXT", is_primary_key=False, is_nullable=False, is_unique=False),
                        DbColumn(name="owner_id", type="INTEGER", is_primary_key=False, is_nullable=False, is_unique=False)
                    ],
                    indexes=[],
                    foreign_keys=[]
                )
            ]),
            api_schema=ApiSchema(endpoints=[
                ApiEndpoint(
                    path="/api/contacts",
                    method="GET",
                    description="Get contacts",
                    auth_required=True,
                    allowed_roles=["Admin", "Member"],
                    db_operations=[DbOperation(table="contacts", action="SELECT", conditions="owner_id = user.id")]
                ),
                ApiEndpoint(
                    path="/api/contacts",
                    method="POST",
                    description="Create contact",
                    auth_required=True,
                    allowed_roles=["Admin", "Member"],
                    db_operations=[DbOperation(table="contacts", action="INSERT")]
                )
            ]),
            ui_schema=UiSchema(pages=[
                UiPage(
                    name="Dashboard",
                    route="/dashboard",
                    auth_required=True,
                    allowed_roles=["Admin", "Member"],
                    components=[
                        UiComponent(
                            id="header",
                            type="Heading",
                            title="Dashboard",
                            props={"text": "Welcome to contacts CRM"}
                        )
                    ]
                )
            ]),
            auth_schema=AuthSchema(
                roles=["Admin", "Member", "Anonymous"],
                permissions={"Admin": ["contacts:read", "contacts:write"], "Member": ["contacts:read"], "Anonymous": []},
                gated_features=[]
            ),
            logic_schema=LogicSchema(rules=[
                LogicRule(
                    id="member_gate",
                    trigger_event="api:before_call:/api/contacts:POST",
                    conditions=["user.role != 'Admin'"],
                    action="DENY",
                    error_message="Only admins can add contacts directly."
                )
            ])
        )

    def test_semantic_validator_valid_config(self):
        """Checks that the validator returns no errors for a fully consistent AppConfig."""
        errors = validate_app_config(self.valid_config)
        self.assertEqual(len(errors), 0, f"Expected 0 errors, got: {errors}")

    def test_semantic_validator_catches_invalid_table_ref(self):
        """Checks that the validator flags an API endpoint performing operations on a non-existent DB table."""
        # Intentionally break the API endpoint to reference non-existent table "clients"
        config = self.valid_config.model_dump()
        config["api_schema"]["endpoints"][0]["db_operations"][0]["table"] = "clients"
        
        broken_config = AppConfig(**config)
        errors = validate_app_config(broken_config)
        
        self.assertGreater(len(errors), 0, "Validator should have flagged the missing database table reference.")
        self.assertEqual(errors[0]["category"], "CROSS_LAYER")
        self.assertIn("non-existent table 'clients'", errors[0]["message"])

    def test_semantic_validator_catches_undefined_roles(self):
        """Checks that the validator flags page/endpoint roles not matching defined Auth roles."""
        config = self.valid_config.model_dump()
        config["ui_schema"]["pages"][0]["allowed_roles"].append("Moderator")
        
        broken_config = AppConfig(**config)
        errors = validate_app_config(broken_config)
        
        self.assertGreater(len(errors), 0, "Validator should have flagged the missing user role Moderator.")
        self.assertEqual(errors[0]["category"], "AUTH")
        self.assertIn("Moderator", errors[0]["message"])

    def test_programmatic_repair_patches_missing_role(self):
        """Checks that the repair engine can automatically restore undefined roles in Auth schemas."""
        config = self.valid_config.model_dump()
        config["ui_schema"]["pages"][0]["allowed_roles"].append("SuperUser")
        
        broken_config = AppConfig(**config)
        errors = validate_app_config(broken_config)
        self.assertEqual(len(errors), 1)
        
        repaired_config = programmatic_repair(broken_config, errors)
        new_errors = validate_app_config(repaired_config)
        
        self.assertEqual(len(new_errors), 0, f"Expected errors to be repaired, but got: {new_errors}")
        self.assertIn("SuperUser", repaired_config.auth_schema.roles)

    def test_sqlite_mock_db_crud(self):
        """Checks table creation, data inserting, and fetching in in-memory SQLite."""
        db = MockDatabase(self.valid_config.db_schema)
        
        # Test insert
        last_id, count = db.execute(
            "INSERT INTO contacts (name, owner_id) VALUES (?, ?);", 
            ("Dave Davies", 2)
        )
        self.assertEqual(count, 1)
        self.assertGreater(last_id, 0)
        
        # Test query SELECT
        rows = db.query("SELECT * FROM contacts WHERE id = ?;", (last_id,))
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["name"], "Dave Davies")
        
        db.close()

    def test_api_router_logic_rules_denial(self):
        """Checks that logic rules correctly gate database actions via HTTP requests."""
        db = MockDatabase(self.valid_config.db_schema)
        router = MockApiRouter(self.valid_config.api_schema, self.valid_config.logic_schema, db)
        
        # Request body
        payload = {"id": 10, "name": "New lead"}
        
        # Member role (which is gated by logic rule member_gate saying role != Admin)
        user_member = {"id": 2, "email": "member@appforge.com", "role": "Member", "subscription": "free"}
        res = router.handle_request("/api/contacts", "POST", payload, user_member)
        
        self.assertEqual(res["status"], 400)
        self.assertIn("Only admins can add contacts", res["body"]["error"])
        
        # Admin role (which should bypass the gate)
        user_admin = {"id": 1, "email": "admin@appforge.com", "role": "Admin", "subscription": "premium"}
        res_admin = router.handle_request("/api/contacts", "POST", payload, user_admin)
        self.assertEqual(res_admin["status"], 200)
        
        db.close()

    def test_simulator_view_and_binding(self):
        """Checks that the simulator mounts component bindings and returns rendered views."""
        simulator = AppSimulator(self.valid_config)
        
        # Dashboard page has no bindings, returns status 200
        view = simulator.get_rendered_page("/dashboard")
        self.assertEqual(view["status"], 200)
        self.assertEqual(view["page_name"], "Dashboard")
        self.assertEqual(len(view["components"]), 1)
        
        # Check non-existent page route returns 404
        view_err = simulator.get_rendered_page("/unknown")
        self.assertEqual(view_err["status"], 404)
        
        simulator.close()

if __name__ == "__main__":
    unittest.main()
