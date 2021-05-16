from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import PositiveInt
from typing import List
from sqlalchemy.orm import Session

import crud, schemas, models
from database import get_db


router = APIRouter()

@router.get("/suppliers", response_model=List[schemas.SupplierLittle])
async def get_suppliers(response: Response, db: Session = Depends(get_db)):
	response.status_code = 200
	return crud.get_suppliers(db)


@router.get("/suppliers/{supplier_id}", response_model=schemas.Supplier)
async def get_supplier(supplier_id: int, response: Response, db: Session = Depends(get_db)):
	supplier = crud.get_supplier_by_id(db, supplier_id)
	if supplier is None:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
	else:
		response.status_code = 200
		return supplier
