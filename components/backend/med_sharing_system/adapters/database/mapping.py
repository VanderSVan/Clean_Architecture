from sqlalchemy.orm import registry, relationship

from med_sharing_system.application import entities
from . import tables

mapper = registry()

mapper.map_imperatively(entities.Patient, tables.patients)
mapper.map_imperatively(entities.Symptom, tables.symptoms)
mapper.map_imperatively(entities.Diagnosis, tables.diagnoses)
mapper.map_imperatively(entities.ItemCategory, tables.item_categories)
mapper.map_imperatively(entities.ItemType, tables.item_types)
mapper.map_imperatively(
    entities.TreatmentItem,
    tables.treatment_items,
    properties={
        'reviews': relationship(
            entities.ItemReview,
            lazy='select',
            cascade='all, delete-orphan',
            order_by=tables.item_reviews.c.item_rating.desc()
        )
    }
)
mapper.map_imperatively(entities.ItemReview, tables.item_reviews)
mapper.map_imperatively(
    entities.MedicalBook,
    tables.medical_books,
    properties={
        'symptoms': relationship(
            entities.Symptom,
            secondary=tables.medical_books_symptoms,
            lazy='select',
            cascade='save-update, merge',
            order_by=tables.symptoms.c.name.asc()
        ),
        'item_reviews': relationship(
            entities.ItemReview,
            secondary=tables.medical_books_item_reviews,
            lazy='select',
            cascade='save-update, merge',
            order_by=tables.item_reviews.c.item_rating.desc()
        ),
        'diagnosis': relationship(
            entities.Diagnosis,
            uselist=False,
            lazy='select',
            backref='medical_books',
            order_by=tables.diagnoses.c.name.asc()
        ),
        'patient': relationship(
            entities.Patient,
            uselist=False,
            lazy='select',
            cascade='save-update, merge',
            order_by=tables.patients.c.nickname.asc()
        ),
    }
)
