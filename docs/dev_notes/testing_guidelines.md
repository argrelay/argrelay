
| Method                     | Client test | Server test | REST | `EnvMock`                             | Comments |
|----------------------------|-------------|-------------|------|---------------------------------------|----------|
| `LocalServer`              | Yes         | Yes         | No   | `set_client_config_with_local_server` |          |
| `ServerOnlyEnvMockBuilder` | No          | Yes         | ?    |                                       |          |
| `LiveServerEnvMockBuilder` | Yes         | Yes         | Yes  |                                       |          |


These are used together:
*   set_client_config_with_local_server
*   set_mock_server_config_file_read    4
*   set_mock_client_config_file_read
*   set_mock_client_input

Used together by set_client_config_with_local_server x ||||:
.set_mock_client_config_file_read(False)
.set_client_config_with_local_server(False)