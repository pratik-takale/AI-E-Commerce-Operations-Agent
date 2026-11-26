from fastapi import APIRouter

router = APIRouter()


@router.get("/ping")
def ping():
    return {"message": "orders router is ready"}