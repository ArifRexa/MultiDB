class DatabaseInfoError(Exception):
    def __init__(self,message: str = "Database/Table Does Not Found with Given Information"):
        super().__init__(message)
    
    def __str__(self) -> str:
        return "Database not found"
