from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from pydantic import BaseModel

router = APIRouter(prefix="/students", tags=["students"])

class StudentCreate(BaseModel):
    name: str
    email: str

@router.post("/")
def create_student(s: StudentCreate, db: Session = Depends(get_db)):
    student = models.Student(**s.dict())
    db.add(student)
    db.commit()
    db.refresh(student)
    return student

@router.get("/email/{email}")
def get_student_by_email(email: str, db: Session = Depends(get_db)):
    student = db.query(models.Student).filter(models.Student.email == email).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student

@router.get("/{student_id}")
def get_student(student_id: int, db: Session = Depends(get_db)):
    return db.query(models.Student).filter(models.Student.id == student_id).first()

@router.delete("/{student_id}")
def delete_student(student_id: int, db: Session = Depends(get_db)):
    # Delete all attempts first
    db.query(models.Attempt).filter(models.Attempt.student_id == student_id).delete()
    student = db.query(models.Student).filter(models.Student.id == student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    db.delete(student)
    db.commit()
    return {"message": "Student deleted successfully"}