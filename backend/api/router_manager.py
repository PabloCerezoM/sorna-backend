from fastapi import APIRouter

class RouterManager:
    __routes: dict[str, APIRouter] = {}

    @classmethod
    def add_router(cls, router: APIRouter) -> APIRouter:
        if router.prefix in cls.__routes:
            raise ValueError(f"Router with prefix {router.prefix} already exists")
        
        cls.__routes[router.prefix] = router

        return router

    @classmethod
    def all(cls) -> dict[str, APIRouter]:
        return cls.__routes