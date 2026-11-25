from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.product import Product
from app.schemas.product import ProductCreate, ProductUpdate


def create_product(
    db: Session,
    product_data: ProductCreate,
) -> Product:
    existing_product = db.scalar(select(Product).where(Product.sku == product_data.sku))

    if existing_product:
        raise ValueError("A product with this SKU already exists")

    product = Product(**product_data.model_dump())

    db.add(product)
    db.commit()
    db.refresh(product)

    return product


def get_product(
    db: Session,
    product_id: int,
) -> Product | None:
    return db.get(Product, product_id)


def get_products(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[Product]:
    statement = select(Product).order_by(Product.id).offset(skip).limit(limit)

    return list(db.scalars(statement).all())


def update_product(
    db: Session,
    product_id: int,
    product_data: ProductUpdate,
) -> Product | None:
    product = db.get(Product, product_id)

    if product is None:
        return None

    update_data = product_data.model_dump(exclude_unset=True)

    for field, value in update_data.items():
        setattr(product, field, value)

    db.commit()
    db.refresh(product)

    return product


def delete_product(
    db: Session,
    product_id: int,
) -> bool:
    product = db.get(Product, product_id)

    if product is None:
        return False

    db.delete(product)
    db.commit()

    return True
