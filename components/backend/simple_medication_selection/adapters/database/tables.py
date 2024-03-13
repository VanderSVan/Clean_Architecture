from sqlalchemy import (
    Boolean,
    Column,
    DECIMAL,
    Float,
    ForeignKey,
    Integer,
    MetaData,
    String,
    Table,
    Text,
)

naming_convention = {
    'ix': 'ix_%(column_0_label)s',
    'uq': 'uq_%(table_name)s_%(column_0_name)s',
    'ck': 'ck_%(table_name)s_%(constraint_name)s',
    'fk': 'fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s',
    'pk': 'pk_%(table_name)s'
}

metadata = MetaData(naming_convention=naming_convention)

patients = Table(
    'patients',
    metadata,
    Column('id', Integer, primary_key=True),
    Column('nickname', String, nullable=False, unique=True),
    Column('gender', String, nullable=False),
    Column('age', Integer, nullable=False),
    Column('skin_type', String, nullable=False),
    Column('about', Text, nullable=True),
    Column('phone', String(15), nullable=True),
)

symptoms = Table(
    'symptoms',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', String, nullable=False, unique=True),
)

diagnoses = Table(
    'diagnoses',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', String, nullable=False, unique=True),
)

item_types = Table(
    'item_types',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', String, nullable=False, unique=True),
)

item_categories = Table(
    'item_categories',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', String, nullable=False, unique=True),
)

treatment_items = Table(
    'treatment_items',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('title', String, nullable=False),
    Column('price', Float, nullable=True),
    Column('description', String, nullable=True),
    Column('type_id', Integer,
           ForeignKey('item_types.id', ondelete='CASCADE', onupdate='CASCADE'),
           nullable=False),
    Column('category_id', Integer,
           ForeignKey('item_categories.id', ondelete='CASCADE', onupdate='CASCADE'),
           nullable=False),
    Column('avg_rating', DECIMAL(precision=3, scale=2), nullable=True),
)

item_reviews = Table(
    'item_reviews',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('item_id', Integer,
           ForeignKey('treatment_items.id', ondelete='CASCADE', onupdate='CASCADE'),
           nullable=False),
    Column('is_helped', Boolean, nullable=False),
    Column('item_rating', DECIMAL(precision=2, scale=1), nullable=False),
    Column('item_count', Integer, nullable=False),
    Column('usage_period', Integer, nullable=True),
)

medical_books_symptoms = Table(
    'medical_books_symptoms',
    metadata,
    Column('medical_book_id',
           ForeignKey('medical_books.id', ondelete='CASCADE', onupdate='CASCADE'),
           primary_key=True,
           nullable=False),
    Column('symptom_id',
           ForeignKey('symptoms.id', ondelete='CASCADE', onupdate='CASCADE'),
           primary_key=True,
           nullable=False)
)

medical_books_item_reviews = Table(
    'medical_books_item_reviews',
    metadata,
    Column('medical_book_id',
           ForeignKey('medical_books.id', ondelete='CASCADE', onupdate='CASCADE'),
           primary_key=True,
           nullable=False),
    Column('item_review_id',
           ForeignKey('item_reviews.id', ondelete='CASCADE', onupdate='CASCADE'),
           primary_key=True,
           nullable=False)
)

medical_books = Table(
    'medical_books',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('title_history', String(255), nullable=False),
    Column('history', Text, nullable=True),
    Column('patient_id', Integer,
           ForeignKey('patients.id', ondelete='CASCADE', onupdate='CASCADE')),
    Column('diagnosis_id', Integer,
           ForeignKey('diagnoses.id',  ondelete='CASCADE', onupdate='CASCADE')),
)
