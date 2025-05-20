import secrets
from uuid import UUID
from typing import Annotated, Any, TypedDict, Literal
from base64 import urlsafe_b64encode

import bcrypt

from fastapi import Security, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from fastapi.security import APIKeyCookie
from jose import jwt
from jose.exceptions import JWTError
from dataclasses import dataclass
from sqlalchemy import select
from fastapi import Request, Response
from datetime import datetime, timedelta, UTC

from backend.database.functions import get_db_session
from backend.database.tables import SessionsTable
from backend.database.tables import UsersTable
from backend.settings.web import WebSettings

session_cookie_scheme = APIKeyCookie(name="session", auto_error=False)
profile_cookie_scheme = APIKeyCookie(name="profile", auto_error=False)
web_settings: WebSettings = WebSettings()  # type: ignore


@dataclass
class SessionData:
    user_id: UUID
    session: str


@dataclass
class ProfileData:
    user_id: UUID
    username: str
    email: str


@dataclass
class AuthenticatedUser:
    id: UUID
    username: str
    email: str
    session: str

class SetCookieTypedDict(TypedDict):
    key: str
    value: str
    expires: int
    httponly: bool
    secure: bool
    samesite: Literal["lax", "strict"]
    domain: str

async def get_authenticated_user(
    session: Annotated[str | None, Security(session_cookie_scheme)],
    profile: Annotated[str | None, Security(profile_cookie_scheme)],
) -> AuthenticatedUser:
    if session is None or profile is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )

    return await SessionMiddleware.validate(session, profile)


class SessionMiddleware(BaseHTTPMiddleware):

    async def dispatch(self, request: Request, call_next):
        cookies: list[SetCookieTypedDict] = []
        
        # Retrieving Cookies
        session_cookie_encoded = request.cookies.get(session_cookie_scheme.scheme_name)
        profile_cookie_encoded = request.cookies.get(profile_cookie_scheme.scheme_name)

        if any([session_cookie_encoded, profile_cookie_encoded]) and not all(
            [session_cookie_encoded, profile_cookie_encoded]
        ):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            )

        if session_cookie_encoded and profile_cookie_encoded:
            session_decoded = jwt.decode(
                session_cookie_encoded,
                web_settings.WEB_COOKIE_SECRET,
                algorithms=["HS256"],
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "require": ["exp", "session", "user_id"],
                },
            )
            
            session_cookie_extended = self.extend_cookie(session_decoded)
            if session_cookie_extended is not None:
                session_cookie = self.create_session_cookie(session_cookie_extended)
                cookies.append(session_cookie)
            
            profile_decoded = jwt.decode(
                profile_cookie_encoded,
                web_settings.WEB_COOKIE_SECRET,
                algorithms=["HS256"],
                options={
                    "verify_signature": True,
                    "verify_exp": True,
                    "require": ["exp", "user_id", "username", "email"],
                },
            )
            
            profile_cookie_extended = self.extend_cookie(profile_decoded)
            if profile_cookie_extended:
                profile_cookie = self.create_profile_cookie(profile_cookie_extended)
                cookies.append(profile_cookie)
            
        response: Response = await call_next(request)
        for cookie in cookies:
            response.set_cookie(**cookie)

        return response

    @staticmethod
    def extend_cookie(claims: dict[str, Any]) -> dict[str, Any] | None:
        now = datetime.now(UTC)

        exp: int = claims["exp"]
        extend_trigger = web_settings.WEB_COOKIE_EXTEND_TRIGGER_SECONDS
        exp_diff = exp - int(now.timestamp())

        if exp_diff <= extend_trigger:
            claims["exp"] = int((now + timedelta(seconds=web_settings.WEB_COOKIE_EXPIRATION_SECONDS)).timestamp())
            claims["nonce"] = secrets.token_urlsafe(16)
            return claims

        return None

    @staticmethod
    def create_session_cookie(values: dict[str, Any]) -> SetCookieTypedDict:
        values.update(nonce=secrets.token_urlsafe(16))
        
        return {
            "key": session_cookie_scheme.model.name,
            "value": jwt.encode(
                values,
                web_settings.WEB_COOKIE_SECRET,
                algorithm="HS256",
            ),
            "expires": values["exp"],
            "httponly": True,
            "secure": True,
            "samesite": "strict",
            "domain": web_settings.WEB_FQDN,
        }
    
    @staticmethod
    def create_profile_cookie(values: dict[str, Any]) -> SetCookieTypedDict:
        values.update(nonce=secrets.token_urlsafe(16))
        
        return {
            "key": profile_cookie_scheme.model.name,
            "value": jwt.encode(
                values,
                web_settings.WEB_COOKIE_SECRET,
                algorithm="HS256",
            ),
            "expires": values["exp"],
            "httponly": False,
            "secure": True,
            "samesite": "strict",
            "domain": web_settings.WEB_FQDN,
        }
    
    @staticmethod
    async def logout(current_user: AuthenticatedUser) -> Response:
        try:
            
            async with get_db_session() as db_session:
                result = await db_session.execute(
                    select(SessionsTable).where(
                        SessionsTable.user_id == current_user.id,
                        SessionsTable.session == current_user.session,
                    )
                )
                
                session = result.scalar_one_or_none()
                if session is not None:
                    await db_session.delete(session)
                    await db_session.commit()
                    
        except Exception as e:
            pass # Handle exception if needed. For example, log it.
        
        finally:
            response = Response(status_code=status.HTTP_204_NO_CONTENT, content='')
            response.delete_cookie(session_cookie_scheme.scheme_name)
            response.delete_cookie(profile_cookie_scheme.scheme_name)
            return response
    
    @staticmethod
    async def login(
        request: Request,
        username: str,
        password: str,
    ) -> Response:
        now = datetime.now(UTC)
        expires = now + timedelta(seconds=web_settings.WEB_COOKIE_EXPIRATION_SECONDS)
        
        async with get_db_session() as db_session:
            result = await db_session.execute(
                select(UsersTable).where(UsersTable.username == username)
            )
            
            user = result.scalar_one_or_none()
            
            if user is None or not bcrypt.checkpw(password.encode("utf-8"), user.password):
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid credentials",
                )

            session = urlsafe_b64encode(secrets.token_bytes(32)).decode("utf-8")
            
            user_agent = request.headers.get("User-Agent")
            ip_address = request.client.host if request.client else None
            
            session_record = SessionsTable(
                session=session,
                user_id=user.id,
                user_agent=user_agent,
                ip_address=ip_address,
                expires=expires,
            )
            
            db_session.add(session_record)
            
        
            session = {
                "user_id": str(user.id),
                "session": session,
                "exp": int(expires.timestamp()),
            }
            
            profile = {
                "user_id": str(user.id),
                "username": str(user.username),
                "email": str(user.email),
                "exp": int(expires.timestamp()),
            }

            await db_session.commit()
            
        create_session_cookie = SessionMiddleware.create_session_cookie(session)
        create_profile_cookie = SessionMiddleware.create_profile_cookie(profile)
        
        response = Response(status_code=status.HTTP_204_NO_CONTENT, content='')
        response.set_cookie(**create_session_cookie)
        response.set_cookie(**create_profile_cookie)
        
        return response
        
    @staticmethod
    async def validate(
        session: str,
        profile: str,
    ) -> AuthenticatedUser:

        try:
            session_raw = jwt.get_unverified_claims(session)
            profile_raw = jwt.get_unverified_claims(profile)

            session_data = SessionData(
                user_id=UUID(session_raw["user_id"]),
                session=session_raw["session"],
            )

            profile_data = ProfileData(
                user_id=UUID(profile_raw["user_id"]),
                username=profile_raw["username"],
                email=profile_raw["email"],
            )

            async with get_db_session() as db_session:
                result = await db_session.execute(
                    select(SessionsTable).where(
                        SessionsTable.user_id == session_data.user_id,
                        SessionsTable.session == session_data.session,
                    )
                )
                
                if result.one_or_none() is None:
                    raise HTTPException(
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        detail="Invalid credentials",
                    )

            return AuthenticatedUser(
                id=session_data.user_id,
                username=profile_data.username,
                email=profile_data.email,
                session=session_data.session,
            )

        except JWTError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid credentials",
            ) from e
