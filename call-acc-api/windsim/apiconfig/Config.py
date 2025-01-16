from pydantic_settings import BaseSettings

class Config(BaseSettings):
    API_BASE_URL_TEST: str = "https://coreapi-accelerator-test.windsim.com"
    API_BASE_URL_PROD: str = "https://coreapi-accelerator-prod.windsim.com"
    ADD_PROJECT_POSTFIX: str = "/api/Project/Add"

    MAP_FUNCTION_URL_TEST: str = "https://func-mapapi-test-westeurope.azurewebsites.net/api/Terrain/GenerateGwsFile?code="
    MAP_FUNCTION_URL_PROD: str = "https://func-mapapi-prod-westeurope.azurewebsites.net/api/Terrain/GenerateGwsFile?code="
    ENV: str = "test"

    addProject: str = API_BASE_URL_TEST + ADD_PROJECT_POSTFIX

    ADD_PROJECT_TEST: str = API_BASE_URL_TEST + ADD_PROJECT_POSTFIX
    LOGIN_TEST: str = API_BASE_URL_TEST + "/api/Authentication/Login"

    ADD_PROJECT_PROD: str = API_BASE_URL_PROD + ADD_PROJECT_POSTFIX

    LOGIN_PROD: str = API_BASE_URL_PROD + "/api/Authentication/Login"
