from uuid import UUID
from typing import Annotated
from fastapi.security import APIKeyCookie
from fastapi import Security, HTTPException
from jose import jwt
from jose.exceptions import JWTError, JWTClaimsError
from backend.settings.web import WebSettings

session_cookie_scheme = APIKeyCookie(name="session", auto_error=False)
profile_coockie_scheme = APIKeyCookie(name="profile", auto_error=False)

web_settings: WebSettings = WebSettings() # type: ignore

class AuthenticatedUser:
    id: UUID
    session_id: str
    username: str
    email: str

    async def __init__(
        self,
        session: Annotated[str, Security(session_cookie_scheme)],
        profile: Annotated[str, Security(profile_coockie_scheme)],
    ):
        self.__decode_cookies(session, profile)
        
        pass
    
    def __decode_cookies(self, session: str, profile: str):
        """
        Decodes the JWT tokens from the cookies.
        """
        try:
            session_data = jwt.decode(session, web_settings.WEB_SESSION_SECRET, algorithms=["HS256"])
            profile_data = jwt.decode(profile, web_settings.WEB_SESSION_SECRET, algorithms=["HS256"])
            self.id = UUID(session_data["sub"])
            self.username = profile_data["username"]
            self.email = profile_data["email"]
        except (JWTError, JWTClaimsError):
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        
    async def __validate_session(self):
        # Validate the session ID against the database
        # consultar el session id que tengo en el self para el user id que tengo en el self
        # if not session_id:
        #     raise HTTPException(status_code=401, detail="Invalid session ID")
        # if ok nada mas
        pass