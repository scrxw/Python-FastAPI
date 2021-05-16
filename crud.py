from sqlalchemy.orm import Session

import models, schemas


def get_shippers(db: Session):
    return db.query(models.Shipper).all()


def get_shipper(db: Session, shipper_id: int):
    return (
        db.query(models.Shipper).filter(models.Shipper.ShipperID == shipper_id).first()
    )

def get_suppliers(db:Session):
	return (
		db.query(models.Supplier).order_by(models.Supplier.SupplierID.asc()).all()
		)
def get_supplier_id(db:Session, supplier_id: int):
	return(
		db.query(models.Supplier).filter(models.Supplier.SupplierID == supplier_id).order_by(models.Supplier.SupplierID).first()
		)