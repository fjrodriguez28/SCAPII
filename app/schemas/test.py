from pydantic import BaseModel

class DatabaseTestRequest(BaseModel):
    server: str
    database: str
    username: str
    password: str
    port: int = 1433
    test_query: str = "SELECT 1"