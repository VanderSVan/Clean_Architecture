from sqlalchemy import create_engine, Column, Integer, String, ForeignKey, Table
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

# Many-to-Many association table
symptom_association = Table('symptom_association', Base.metadata,
                            Column('patient_id', Integer, ForeignKey('patients.id')),
                            Column('symptom_id', Integer, ForeignKey('symptoms.id'))
                            )

diagnosis_association = Table('diagnosis_association', Base.metadata,
                              Column('patient_id', Integer, ForeignKey('patients.id')),
                              Column('diagnosis_id', Integer, ForeignKey('diagnoses.id'))
                              )

effect_association = Table('effect_association', Base.metadata,
                           Column('product_id', Integer, ForeignKey('products.id')),
                           Column('effect_id', Integer, ForeignKey('effects.id'))
                           )


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    role = Column(String)
    email = Column(String, unique=True)
    password = Column(String)
    nickname = Column(String)


class Patient(User):
    __tablename__ = 'patients'
    id = Column(Integer, ForeignKey('users.id'), primary_key=True)
    age = Column(Integer)
    skin_type = Column(String)
    history = Column(String)
    symptoms = relationship('Symptom', secondary=symptom_association, backref='patients')
    diagnoses = relationship('Diagnosis', secondary=diagnosis_association, backref='patients')


class Symptom(Base):
    __tablename__ = 'symptoms'
    id = Column(Integer, primary_key=True)
    name = Column(String)


class Diagnosis(Base):
    __tablename__ = 'diagnoses'
    id = Column(Integer, primary_key=True)
    name = Column(String)


class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    category = Column(String)
    type = Column(String)
    effects = relationship('Effect', secondary=effect_association, backref='products')


class Procedure(Base):
    __tablename__ = 'procedures'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    category = Column(String)
    type = Column(String)
    effects = relationship('Effect', secondary=effect_association, backref='procedures')


class Effect(Base):
    __tablename__ = 'effects'
    id = Column(Integer, primary_key=True)
    name = Column(String)


class TreatmentResult(Base):
    __tablename__ = 'treatment_results'
    id = Column(Integer, primary_key=True)
    name = Column(String)


class CompletedTreatmentProtocol(Base):
    __tablename__ = 'treatment_protocols'
    id = Column(Integer, primary_key=True)
    duration = Column(Integer)
    diagnosis_id = Column(Integer, ForeignKey('diagnoses.id'))
    product_id = Column(Integer, ForeignKey('products.id'))
    procedure_id = Column(Integer, ForeignKey('procedures.id'))
    result_id = Column(Integer, ForeignKey('treatment_results.id'))


engine = create_engine('sqlite:///:memory:')
Base.metadata.create_all(engine)
