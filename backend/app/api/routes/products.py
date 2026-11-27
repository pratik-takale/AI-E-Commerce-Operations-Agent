from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.api.deps import require_admin
from app.database import get_db
from app.schemas.product import ProductCreate, ProductListOut, ProductOut, ProductUpdate
from app.services import product_service

router = APIRouter()


@router.get("", response_model=ProductListOut, summary="Get all products")
def get_products(
    category: str | None = Query(None, description="Example: Smartphones"),
    q: str | None = Query(None, min_length=2, description="Search in name and description"),
    min_price: float | None = Query(None, ge=0),
    max_price: float | None = Query(None, ge=0),
    in_stock: bool = Query(False, description="If true, return only products in stock"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return product_service.list_products(
        db, category, q, min_price, max_price, in_stock, page, page_size
    )


@router.get("/{product_id}", response_model=ProductOut, summary="Product details")
def get_product(product_id: int, db: Session = Depends(get_db)):
    return product_service.get_product(db, product_id)


# The endpoints below change data, so they are admin only.

@router.post(
    "",
    response_model=ProductOut,
    status_code=status.HTTP_201_CREATED,
    summary="Add product (admin)",
    dependencies=[Depends(require_admin)],
)
def create_product(body: ProductCreate, db: Session = Depends(get_db)):
    return product_service.create_product(db, body)


@router.put(
    "/{product_id}",
    response_model=ProductOut,
    summary="Update product (admin)",
    dependencies=[Depends(require_admin)],
)
def update_product(product_id: int, body: ProductUpdate, db: Session = Depends(get_db)):
    return product_service.update_product(db, product_id, body)


@router.delete(
    "/{product_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete product, soft delete (admin)",
    dependencies=[Depends(require_admin)],
)
def delete_product(product_id: int, db: Session = Depends(get_db)):
    product_service.delete_product(db, product_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)