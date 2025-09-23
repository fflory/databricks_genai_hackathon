# import unittest
# # import unittest.mock as mock
# # from unittest.mock import MagicMock, patch
# import sys
# import os

# # Add the project root to the path to import the configs module
# sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# from configs.project import Environment


# class TestEnvironment(unittest.TestCase):
#     """Test cases for the Environment class using unittest."""

#     def setUp(self):
#         """Set up test data for each test."""
#         self.valid_env_data = {
#             'uc_catalog': 'test_catalog',
#             'uc_schema': 'test_schema',
#             'raw_data_volume': 'test_volume',
#             'vector_search_endpoint_name': 'test_vs_endpoint',
#             'embedding_model_endpoint_name': 'test_embedding_endpoint',
#             'secret_scope': 'test_scope',
#             'genie_space_id': 'test_genie_id',
#             'llm_endpoint_names': ['test_llm_endpoint'],
#             'mlflow_experiment_name': 'test_experiment'
#         }
        
#         # Set up environment to use sdlc profile for all tests
#         os.environ['DATABRICKS_CONFIG_PROFILE'] = 'sdlc'

#     def tearDown(self):
#         """Clean up after each test."""
#         # Remove the environment variable after each test
#         if 'DATABRICKS_CONFIG_PROFILE' in os.environ:
#             del os.environ['DATABRICKS_CONFIG_PROFILE']

#     def test_environment_creation_with_required_fields(self):
#         """Test that Environment can be created with all required fields."""
#         env = Environment(**self.valid_env_data)
        
#         self.assertEqual(env.uc_catalog, 'test_catalog')
#         self.assertEqual(env.uc_schema, 'test_schema')
#         self.assertEqual(env.raw_data_volume, 'test_volume')
#         self.assertEqual(env.vector_search_endpoint_name, 'test_vs_endpoint')
#         self.assertEqual(env.embedding_model_endpoint_name, 'test_embedding_endpoint')
#         self.assertEqual(env.secret_scope, 'test_scope')
#         self.assertEqual(env.genie_space_id, 'test_genie_id')
#         self.assertEqual(env.llm_endpoint_names, ['test_llm_endpoint'])
#         self.assertEqual(env.mlflow_experiment_name, 'test_experiment')

#     def test_environment_missing_required_fields(self):
#         """Test that Environment raises validation error when required fields are missing."""
#         incomplete_data = {
#             'uc_catalog': 'test_catalog',
#             'uc_schema': 'test_schema',
#             # Missing other required fields
#         }
        
#         with self.assertRaises(Exception):  # Pydantic will raise ValidationError
#             Environment(**incomplete_data)

#     def test_llm_endpoint_names_as_list(self):
#         """Test that llm_endpoint_names accepts a list of strings."""
#         data = self.valid_env_data.copy()
#         data['llm_endpoint_names'] = ['endpoint1', 'endpoint2', 'endpoint3']
        
#         env = Environment(**data)
#         self.assertEqual(len(env.llm_endpoint_names), 3)
#         self.assertIn('endpoint1', env.llm_endpoint_names)
#         self.assertIn('endpoint2', env.llm_endpoint_names)
#         self.assertIn('endpoint3', env.llm_endpoint_names)

#     def test_mlflow_experiment_base_path_auto_imputation(self):
#         """Test that mlflow_experiment_base_path is automatically imputed when None."""
#         # Don't include mlflow_experiment_base_path (will be None by default)
#         env = Environment(**self.valid_env_data)
        
#         # Check that the base path was automatically imputed (should contain /Users/)
#         self.assertIsNotNone(env.mlflow_experiment_base_path)
#         self.assertIn('/Users/', env.mlflow_experiment_base_path)
#         self.assertIn('/mlflow_experiments', env.mlflow_experiment_base_path)

#     def test_mlflow_experiment_base_path_explicit_value(self):
#         """Test that explicit mlflow_experiment_base_path is preserved."""
#         explicit_path = '/custom/experiment/path'
#         data = self.valid_env_data.copy()
#         data['mlflow_experiment_base_path'] = explicit_path
        
#         env = Environment(**data)
#         self.assertEqual(env.mlflow_experiment_base_path, explicit_path)

#     def test_environment_field_types(self):
#         """Test that all fields have the correct types."""
#         data = self.valid_env_data.copy()
#         data['mlflow_experiment_base_path'] = '/test/path'
        
#         env = Environment(**data)
        
#         self.assertIsInstance(env.uc_catalog, str)
#         self.assertIsInstance(env.uc_schema, str)
#         self.assertIsInstance(env.raw_data_volume, str)
#         self.assertIsInstance(env.vector_search_endpoint_name, str)
#         self.assertIsInstance(env.embedding_model_endpoint_name, str)
#         self.assertIsInstance(env.secret_scope, str)
#         self.assertIsInstance(env.genie_space_id, str)
#         self.assertIsInstance(env.llm_endpoint_names, list)
#         self.assertIsInstance(env.mlflow_experiment_name, str)
#         self.assertIsInstance(env.mlflow_experiment_base_path, str)

#     def test_environment_empty_llm_endpoint_names_list(self):
#         """Test that empty llm_endpoint_names list is accepted."""
#         data = self.valid_env_data.copy()
#         data['llm_endpoint_names'] = []  # Empty list
        
#         env = Environment(**data)
#         self.assertEqual(env.llm_endpoint_names, [])

#     def test_environment_serialization(self):
#         """Test that Environment can be serialized to dict."""
#         data = self.valid_env_data.copy()
#         data['mlflow_experiment_base_path'] = '/test/path'
        
#         env = Environment(**data)
#         serialized = env.model_dump()
        
#         self.assertIsInstance(serialized, dict)
#         self.assertEqual(serialized['uc_catalog'], 'test_catalog')
#         self.assertEqual(serialized['llm_endpoint_names'], ['test_llm_endpoint'])

#     @patch('configs.project.WorkspaceClient')
#     def test_environment_validator_error_handling(self, mock_workspace_client):
#         """Test error handling in the model validator."""
#         # Remove the profile to test error handling
#         if 'DATABRICKS_CONFIG_PROFILE' in os.environ:
#             del os.environ['DATABRICKS_CONFIG_PROFILE']
        
#         # Test what happens if WorkspaceClient fails
#         mock_workspace_client.side_effect = Exception("Connection failed")
        
#         # This should raise an exception when trying to create WorkspaceClient
#         with self.assertRaises(Exception):
#             Environment(**self.valid_env_data)

#     @patch('databricks.sdk.WorkspaceClient')
#     def test_environment_with_real_yaml_structure(self, mock_workspace_client):
#         """Test Environment with data structure similar to project.yml."""
#         # Mock the workspace client and current user
#         mock_user = MagicMock()
#         mock_user.user_name = 'test.user@example.com'
#         mock_current_user = MagicMock()
#         mock_current_user.me.return_value = mock_user
#         mock_workspace_client.return_value.current_user = mock_current_user
        
#         # Based on the actual project.yml structure
#         yaml_like_data = {
#             'uc_catalog': 'ds_treaties_model_catalog',
#             'uc_schema': 'databricks_genai_hackathon',
#             'raw_data_volume': 'raw_data',
#             'vector_search_endpoint_name': 'one-env-shared-endpoint-1',
#             'embedding_model_endpoint_name': 'databricks-bge-large-en',
#             'secret_scope': 'felix-flory',
#             'genie_space_id': '01f00c360aa7147aa93f081d65b4c8e5',
#             'llm_endpoint_names': ['ASK-BEFORE-USE-fflory-gpt-4o'],
#             'mlflow_experiment_name': 'databricks_genai_hackathon'
#         }
        
#         env = Environment(**yaml_like_data)
        
#         self.assertEqual(env.uc_catalog, 'ds_treaties_model_catalog')
#         self.assertEqual(env.uc_schema, 'databricks_genai_hackathon')
#         self.assertEqual(env.genie_space_id, '01f00c360aa7147aa93f081d65b4c8e5')
#         self.assertEqual(len(env.llm_endpoint_names), 1)
#         self.assertEqual(env.llm_endpoint_names[0], 'ASK-BEFORE-USE-fflory-gpt-4o')


if __name__ == "__main__":
    # Run the tests
    unittest.main(verbosity=2)