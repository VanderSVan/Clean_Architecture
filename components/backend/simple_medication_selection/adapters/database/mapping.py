from sqlalchemy.orm import registry

from simple_medication_selection.application import entities

from . import tables

mapper = registry()

mapper.map_imperatively(entities.Symptom, tables.symptoms)
