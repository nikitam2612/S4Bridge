from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.customer import Customer
from app.schemas.customer import CustomerCreate, CustomerUpdate


def create_customer(
    db: Session,
    customer_data: CustomerCreate,
) -> Customer:
    existing_customer = db.scalar(
        select(Customer).where(Customer.email == customer_data.email)
    )

    if existing_customer:
        raise ValueError("A customer with this email already exists")

    customer = Customer(**customer_data.model_dump())

    db.add(customer)
    db.commit()
    db.refresh(customer)

    return customer


def get_customer(
    db: Session,
    customer_id: int,
) -> Customer | None:
    return db.get(Customer, customer_id)


def get_customers(
    db: Session,
    skip: int = 0,
    limit: int = 100,
) -> list[Customer]:
    statement = select(Customer).order_by(Customer.id).offset(skip).limit(limit)

    return list(db.scalars(statement).all())


def update_customer(
    db: Session,
    customer_id: int,
    customer_data: CustomerUpdate,
) -> Customer | None:
    customer = db.get(Customer, customer_id)

    if customer is None:
        return None

    update_data = customer_data.model_dump(exclude_unset=True)

    if "email" in update_data:
        existing_customer = db.scalar(
            select(Customer).where(
                Customer.email == update_data["email"],
                Customer.id != customer_id,
            )
        )

        if existing_customer:
            raise ValueError("Another customer already uses this email")

    for field, value in update_data.items():
        setattr(customer, field, value)

    db.commit()
    db.refresh(customer)

    return customer


def delete_customer(
    db: Session,
    customer_id: int,
) -> bool:
    customer = db.get(Customer, customer_id)

    if customer is None:
        return False

    db.delete(customer)
    db.commit()

    return True
