from pydantic import BaseModel

class Token(BaseModel):
    """Модель токена, представляющая данные токена."""
    
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None