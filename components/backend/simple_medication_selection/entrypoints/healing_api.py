from sqlalchemy import create_engine

from simple_medication_selection.adapters import database, log
from simple_medication_selection.adapters.database import TransactionContext
from simple_medication_selection.application import services, dtos


class Settings:
    db = database.Settings()


class Logger:
    log.configure(
        Settings.db.LOGGING_CONFIG,
    )


class DB:
    engine = create_engine(Settings.db.DATABASE_URL)

    context = TransactionContext(bind=engine)

    symptoms_repo = database.repositories.SymptomsRepo(context=context)
    triggers_repo = database.repositories.TriggersRepo(context=context)


class Services:
    Symptom = services.Symptom(symptoms_repo=DB.symptoms_repo)
    Trigger = services.Trigger(triggers_repo=DB.triggers_repo)


class Aspects:
    services.symptom_decorated_function_registry.apply_decorators(DB.context)
    services.trigger_decorated_function_registry.apply_decorators(DB.context)


if __name__ == '__main__':

    services.Symptom(symptoms_repo=DB.symptoms_repo).create(dtos.SymptomCreateSchema(name="Test symptom2121"))
    # services.Symptom(symptoms_repo=DB.symptoms_repo).update(dtos.SymptomUpdateSchema(id=2, name="Test symptom2024"))
    # services.Symptom(symptoms_repo=DB.symptoms_repo).delete(dtos.SymptomDeleteSchema(id=2))
