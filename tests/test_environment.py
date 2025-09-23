import pytest
# import unittest.mock as mock
# from unittest.mock import MagicMock, patch
import sys
import os

# Add the project root to the path to import the configs module
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from configs.project import Environment, UnityCatalog, InputModel, VectorSearchModel


class TestEnvironment:
    """Test cases for the Environment class."""

    def test_environment_creation_with_required_fields(self):
        """Test that Environment can be created with all required fields."""
        env_data = {
            'uc_catalog': 'test_catalog',
            'uc_schema': 'test_schema',
            'raw_data_volume': 'test_volume',
            'vector_search_endpoint_name': 'test_vs_endpoint',
            'embedding_model_endpoint_name': 'test_embedding_endpoint',
            'secret_scope': 'test_scope',
            'genie_space_id': 'test_genie_id',
            'llm_endpoint_names': ['test_llm_endpoint'],
            'mlflow_experiment_name': 'test_experiment'
        }
        
        env = Environment(**env_data)
        
        assert env.uc_catalog == 'test_catalog'
        assert env.uc_schema == 'test_schema'
        assert env.raw_data_volume == 'test_volume'
        assert env.vector_search_endpoint_name == 'test_vs_endpoint'
        assert env.embedding_model_endpoint_name == 'test_embedding_endpoint'
        assert env.secret_scope == 'test_scope'
        assert env.genie_space_id == 'test_genie_id'
        assert env.llm_endpoint_names == ['test_llm_endpoint']
        assert env.mlflow_experiment_name == 'test_experiment'

    # def test_environment_inherits_from_input_model_and_vector_search_model(self):
    #     """Test that Environment properly inherits from InputModel and VectorSearchModel."""
    #     env_data = {
    #         'uc_catalog': 'test_catalog',
    #         'uc_schema': 'test_schema',
    #         'raw_data_volume': 'test_volume',
    #         'vector_search_endpoint_name': 'test_vs_endpoint',
    #         'embedding_model_endpoint_name': 'test_embedding_endpoint',
    #         'secret_scope': 'test_scope',
    #         'genie_space_id': 'test_genie_id',
    #         'llm_endpoint_names': ['test_llm_endpoint'],
    #         'mlflow_experiment_name': 'test_experiment'
    #     }
        
    #     env = Environment(**env_data)
        
    #     # Check that it's an instance of the parent classes
    #     assert isinstance(env, InputModel)
    #     assert isinstance(env, VectorSearchModel)
    #     assert isinstance(env, UnityCatalog)

    # def test_environment_missing_required_fields(self):
    #     """Test that Environment raises validation error when required fields are missing."""
    #     incomplete_data = {
    #         'uc_catalog': 'test_catalog',
    #         'uc_schema': 'test_schema',
    #         # Missing other required fields
    #     }
        
    #     with pytest.raises(Exception):  # Pydantic will raise ValidationError
    #         Environment(**incomplete_data)

    # def test_llm_endpoint_names_as_list(self):
    #     """Test that llm_endpoint_names accepts a list of strings."""
    #     env_data = {
    #         'uc_catalog': 'test_catalog',
    #         'uc_schema': 'test_schema',
    #         'raw_data_volume': 'test_volume',
    #         'vector_search_endpoint_name': 'test_vs_endpoint',
    #         'embedding_model_endpoint_name': 'test_embedding_endpoint',
    #         'secret_scope': 'test_scope',
    #         'genie_space_id': 'test_genie_id',
    #         'llm_endpoint_names': ['endpoint1', 'endpoint2', 'endpoint3'],
    #         'mlflow_experiment_name': 'test_experiment'
    #     }
        
    #     env = Environment(**env_data)
    #     assert len(env.llm_endpoint_names) == 3
    #     assert 'endpoint1' in env.llm_endpoint_names
    #     assert 'endpoint2' in env.llm_endpoint_names
    #     assert 'endpoint3' in env.llm_endpoint_names

    # @patch('databricks.sdk.WorkspaceClient')
    # def test_mlflow_experiment_base_path_auto_imputation(self, mock_workspace_client):
    #     """Test that mlflow_experiment_base_path is automatically imputed when None."""
    #     # Mock the workspace client and current user
    #     mock_user = MagicMock()
    #     mock_user.user_name = 'test.user@example.com'
    #     mock_current_user = MagicMock()
    #     mock_current_user.me.return_value = mock_user
    #     mock_workspace_client.return_value.current_user = mock_current_user
        
    #     env_data = {
    #         'uc_catalog': 'test_catalog',
    #         'uc_schema': 'test_schema',
    #         'raw_data_volume': 'test_volume',
    #         'vector_search_endpoint_name': 'test_vs_endpoint',
    #         'embedding_model_endpoint_name': 'test_embedding_endpoint',
    #         'secret_scope': 'test_scope',
    #         'genie_space_id': 'test_genie_id',
    #         'llm_endpoint_names': ['test_llm_endpoint'],
    #         'mlflow_experiment_name': 'test_experiment'
    #         # mlflow_experiment_base_path is None (default)
    #     }
        
    #     env = Environment(**env_data)
        
    #     # Check that the base path was automatically imputed
    #     expected_path = '/Users/test.user@example.com/mlflow_experiments'
    #     assert env.mlflow_experiment_base_path == expected_path

    # def test_mlflow_experiment_base_path_explicit_value(self):
    #     """Test that explicit mlflow_experiment_base_path is preserved."""
    #     explicit_path = '/custom/experiment/path'
    #     env_data = {
    #         'uc_catalog': 'test_catalog',
    #         'uc_schema': 'test_schema',
    #         'raw_data_volume': 'test_volume',
    #         'vector_search_endpoint_name': 'test_vs_endpoint',
    #         'embedding_model_endpoint_name': 'test_embedding_endpoint',
    #         'secret_scope': 'test_scope',
    #         'genie_space_id': 'test_genie_id',
    #         'llm_endpoint_names': ['test_llm_endpoint'],
    #         'mlflow_experiment_name': 'test_experiment',
    #         'mlflow_experiment_base_path': explicit_path
    #     }
        
    #     env = Environment(**env_data)
    #     assert env.mlflow_experiment_base_path == explicit_path

    # def test_environment_model_validation(self):
    #     """Test that the model validator is called correctly."""
    #     env_data = {
    #         'uc_catalog': 'test_catalog',
    #         'uc_schema': 'test_schema',
    #         'raw_data_volume': 'test_volume',
    #         'vector_search_endpoint_name': 'test_vs_endpoint',
    #         'embedding_model_endpoint_name': 'test_embedding_endpoint',
    #         'secret_scope': 'test_scope',
    #         'genie_space_id': 'test_genie_id',
    #         'llm_endpoint_names': ['test_llm_endpoint'],
    #         'mlflow_experiment_name': 'test_experiment'
    #     }
        
    #     # This should not raise any exceptions
    #     env = Environment(**env_data)
    #     assert env is not None

    # def test_environment_field_types(self):
    #     """Test that all fields have the correct types."""
    #     env_data = {
    #         'uc_catalog': 'test_catalog',
    #         'uc_schema': 'test_schema',
    #         'raw_data_volume': 'test_volume',
    #         'vector_search_endpoint_name': 'test_vs_endpoint',
    #         'embedding_model_endpoint_name': 'test_embedding_endpoint',
    #         'secret_scope': 'test_scope',
    #         'genie_space_id': 'test_genie_id',
    #         'llm_endpoint_names': ['test_llm_endpoint'],
    #         'mlflow_experiment_name': 'test_experiment',
    #         'mlflow_experiment_base_path': '/test/path'
    #     }
        
    #     env = Environment(**env_data)
        
    #     assert isinstance(env.uc_catalog, str)
    #     assert isinstance(env.uc_schema, str)
    #     assert isinstance(env.raw_data_volume, str)
    #     assert isinstance(env.vector_search_endpoint_name, str)
    #     assert isinstance(env.embedding_model_endpoint_name, str)
    #     assert isinstance(env.secret_scope, str)
    #     assert isinstance(env.genie_space_id, str)
    #     assert isinstance(env.llm_endpoint_names, list)
    #     assert isinstance(env.mlflow_experiment_name, str)
    #     assert isinstance(env.mlflow_experiment_base_path, str)

    # def test_environment_empty_llm_endpoint_names_list(self):
    #     """Test that empty llm_endpoint_names list is accepted."""
    #     env_data = {
    #         'uc_catalog': 'test_catalog',
    #         'uc_schema': 'test_schema',
    #         'raw_data_volume': 'test_volume',
    #         'vector_search_endpoint_name': 'test_vs_endpoint',
    #         'embedding_model_endpoint_name': 'test_embedding_endpoint',
    #         'secret_scope': 'test_scope',
    #         'genie_space_id': 'test_genie_id',
    #         'llm_endpoint_names': [],  # Empty list
    #         'mlflow_experiment_name': 'test_experiment'
    #     }
        
    #     env = Environment(**env_data)
    #     assert env.llm_endpoint_names == []

    # def test_environment_serialization(self):
    #     """Test that Environment can be serialized to dict."""
    #     env_data = {
    #         'uc_catalog': 'test_catalog',
    #         'uc_schema': 'test_schema',
    #         'raw_data_volume': 'test_volume',
    #         'vector_search_endpoint_name': 'test_vs_endpoint',
    #         'embedding_model_endpoint_name': 'test_embedding_endpoint',
    #         'secret_scope': 'test_scope',
    #         'genie_space_id': 'test_genie_id',
    #         'llm_endpoint_names': ['test_llm_endpoint'],
    #         'mlflow_experiment_name': 'test_experiment',
    #         'mlflow_experiment_base_path': '/test/path'
    #     }
        
    #     env = Environment(**env_data)
    #     serialized = env.model_dump()
        
    #     assert isinstance(serialized, dict)
    #     assert serialized['uc_catalog'] == 'test_catalog'
    #     assert serialized['llm_endpoint_names'] == ['test_llm_endpoint']

    # @patch('databricks.sdk.WorkspaceClient')
    # def test_environment_validator_error_handling(self, mock_workspace_client):
    #     """Test error handling in the model validator."""
    #     # Test what happens if WorkspaceClient fails
    #     mock_workspace_client.side_effect = Exception("Connection failed")
        
    #     env_data = {
    #         'uc_catalog': 'test_catalog',
    #         'uc_schema': 'test_schema',
    #         'raw_data_volume': 'test_volume',
    #         'vector_search_endpoint_name': 'test_vs_endpoint',
    #         'embedding_model_endpoint_name': 'test_embedding_endpoint',
    #         'secret_scope': 'test_scope',
    #         'genie_space_id': 'test_genie_id',
    #         'llm_endpoint_names': ['test_llm_endpoint'],
    #         'mlflow_experiment_name': 'test_experiment'
    #     }
        
    #     # This should raise an exception when trying to create WorkspaceClient
    #     with pytest.raises(Exception):
    #         Environment(**env_data)


if __name__ == "__main__":
    pytest.main([__file__])