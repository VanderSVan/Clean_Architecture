import pytest

from simple_medication_selection.adapters.database import tables, repositories
from simple_medication_selection.application import entities, dtos
from .. import test_data


# ---------------------------------------------------------------------------------------
# SETUP
# ---------------------------------------------------------------------------------------
@pytest.fixture(scope='function', autouse=True)
def fill_db(session) -> dict[str, list[int]]:
    patient_ids: list[int] = test_data.insert_patients(session)
    diagnosis_ids: list[int] = test_data.insert_diagnoses(session)
    symptom_ids: list[int] = test_data.insert_symptoms(session)
    category_ids: list[int] = test_data.insert_categories(session)
    type_ids: list[int] = test_data.insert_types(session)
    item_ids: list[int] = test_data.insert_items(type_ids, category_ids, session)
    review_ids: list[int] = test_data.insert_reviews(item_ids, session)
    med_book_ids: list[int] = test_data.insert_medical_books(patient_ids, diagnosis_ids, session)
    test_data.insert_avg_rating(session)
    test_data.insert_medical_book_reviews(med_book_ids, review_ids, session)
    test_data.insert_medical_book_symptoms(med_book_ids, symptom_ids, session)
    return {
        'patient_ids': patient_ids,
        'diagnosis_ids': diagnosis_ids,
        'symptom_ids': symptom_ids,
        'category_ids': category_ids,
        'type_ids': type_ids,
        'item_ids': item_ids,
        'review_ids': review_ids,
        'med_book_ids': med_book_ids
    }


@pytest.fixture(scope='function')
def repo(transaction_context):
    return repositories.MedicalBooksRepo(context=transaction_context)


# ---------------------------------------------------------------------------------------
# TESTS
# ---------------------------------------------------------------------------------------
class TestFetchById:
    def test__fetch_by_id(self, repo, session):
        # Setup
        med_book = session.query(entities.MedicalBook).first()

        # Call
        result = repo.fetch_by_id(med_book.id)

        # Assert
        assert isinstance(result, entities.MedicalBook)

    def test__not_found(self, repo):
        # Call
        result = repo.fetch_by_id(100)

        # Assert
        assert result is None


class TestFetchByPatientId:
    def test__fetch_by_patient_id(self, repo, session):
        # Setup
        med_book = session.query(entities.MedicalBook).first()

        # Call
        result = repo.fetch_by_patient(patient_id=med_book.patient_id,
                                       limit=None,
                                       offset=None)

        # Assert
        assert result is not None
        for fetched_med_book in result:
            assert isinstance(fetched_med_book, entities.MedicalBook)
            assert fetched_med_book.patient_id == med_book.patient_id

    def test__with_limit(self, repo, session):
        # Setup
        med_book = session.query(entities.MedicalBook).first()

        # Call
        result = repo.fetch_by_patient(patient_id=med_book.patient_id,
                                       limit=1,
                                       offset=None)

        # Assert
        assert len(result) == 1

    def test__with_offset(self, repo, session):
        # Setup
        patient = session.query(entities.Patient).first()
        med_books_by_patient = (
            session.query(entities.MedicalBook).filter_by(patient_id=patient.id).all()
        )

        # Call
        result = (
            repo.fetch_by_patient(patient_id=med_books_by_patient[0].patient_id,
                                  limit=None,
                                  offset=1)
        )

        # Assert
        assert len(result) == len(med_books_by_patient) - 1
        assert med_books_by_patient[1:] == result


class TestFetchBySymptomsAndHelpedStatus:
    @pytest.mark.parametrize('helped_status', [
        'True', 'False',
    ])
    def test__fetch_by_symptoms_and_helped_status(self, helped_status, repo, session,
                                                  fill_db):
        # Setup
        symptom_ids: list[int] = fill_db['symptom_ids'][:2]

        # Call
        result = repo.fetch_by_symptoms_and_helped_status(symptom_ids=symptom_ids,
                                                          is_helped=helped_status,
                                                          limit=None,
                                                          offset=None)

        # Assert
        assert result is not None
        for med_book in result:
            assert isinstance(med_book, dtos.MedicalBookGetSchema)

    def test__with_limit(self, repo, session, fill_db):
        # Setup
        symptom_ids: list[int] = fill_db['symptom_ids'][:2]
        limit = 1

        # Call
        result = repo.fetch_by_symptoms_and_helped_status(symptom_ids=symptom_ids,
                                                          is_helped=True,
                                                          limit=limit,
                                                          offset=None)

        # Assert
        assert len(result) == limit

    def test__with_offset(self, repo, session, fill_db):
        # Setup
        helped_status = True
        offset = 1
        symptom_ids: list[int] = fill_db['symptom_ids'][:2]
        med_books_by_symptoms_count: int = (
            session.query(entities.MedicalBook)
            .join(entities.MedicalBook.item_reviews)
            .join(entities.MedicalBook.symptoms)
            .filter(
                entities.MedicalBook.symptoms.any(entities.Symptom.id.in_(symptom_ids)),
                entities.ItemReview.is_helped == helped_status
            )
            .distinct(entities.MedicalBook.id)
            .count()
        )

        # Call
        result = repo.fetch_by_symptoms_and_helped_status(symptom_ids=symptom_ids,
                                                          is_helped=helped_status,
                                                          limit=None,
                                                          offset=offset)

        # Assert
        assert len(result) == med_books_by_symptoms_count - offset


class TestFetchByDiagnosisAndHelpedStatus:
    @pytest.mark.parametrize('helped_status', [
        'True', 'False',
    ])
    def test__fetch_by_diagnosis_and_helped_status(self, helped_status, repo, session, fill_db):
        # Setup
        diagnosis_id: int = fill_db['diagnosis_ids'][0]

        # Call
        result = repo.fetch_by_diagnosis_and_helped_status(diagnosis_id=diagnosis_id,
                                                           is_helped=True,
                                                           limit=None,
                                                           offset=None)

        # Assert
        assert result is not None
        for med_book in result:
            assert isinstance(med_book, dtos.MedicalBookGetSchema)
            assert med_book.diagnosis_id == diagnosis_id

    def test__with_limit(self, repo, session, fill_db):
        # Setup
        diagnosis_id: int = fill_db['diagnosis_ids'][0]
        limit = 1

        # Call
        result = repo.fetch_by_diagnosis_and_helped_status(diagnosis_id=diagnosis_id,
                                                           is_helped=True,
                                                           limit=limit,
                                                           offset=None)

        # Assert
        assert len(result) == limit

    def test__with_offset(self, repo, session, fill_db):
        # Setup
        helped_status = True
        diagnosis_id: int = fill_db['diagnosis_ids'][0]
        offset = 1
        med_books_by_symptoms__count: int = (
            session.query(entities.MedicalBook)
            .join(entities.MedicalBook.item_reviews)
            .join(entities.MedicalBook.symptoms)
            .filter(
                entities.MedicalBook.diagnosis_id == diagnosis_id,
                entities.ItemReview.is_helped == helped_status
            )
            .distinct(entities.MedicalBook.id)
            .count()
        )

        # Call
        result = repo.fetch_by_diagnosis_and_helped_status(diagnosis_id=diagnosis_id,
                                                           is_helped=helped_status,
                                                           limit=None,
                                                           offset=offset)

        # Assert
        assert len(result) == med_books_by_symptoms__count - 1


class TestAdd:
    def test__add(self, repo, session, fill_db):
        # Setup
        before_count = len(session.execute(tables.medical_books.select()).all())
        symptoms_to_add: list[entities.Symptom] = (
            session.query(entities.Symptom)
            .filter(
                entities.Symptom.id.in_(
                    [fill_db['symptom_ids'][0], fill_db['symptom_ids'][1]]
                )
            )
            .all()
        )
        reviews_to_add: list[entities.ItemReview] = (
            session.query(entities.ItemReview)
            .filter(
                entities.ItemReview.id.in_(
                    [fill_db['review_ids'][0], fill_db['review_ids'][1]]
                )
            )
            .all()
        )

        # Call
        result = repo.add(
            entities.MedicalBook(
                title_history='История 1',
                patient_id=fill_db['patient_ids'][0],
                diagnosis_id=fill_db['diagnosis_ids'][0],
                symptoms=symptoms_to_add,
                item_reviews=reviews_to_add,
            )
        )
        after_count = len(session.execute(tables.medical_books.select()).all())

        # Assert
        assert before_count + 1 == after_count
        assert isinstance(result, entities.MedicalBook)

    def test__add__with_no_symptoms(self, repo, session, fill_db):
        # Setup
        before_count = len(session.execute(tables.medical_books.select()).all())

        # Call
        result = repo.add(
            entities.MedicalBook(
                title_history='История 1',
                patient_id=fill_db['patient_ids'][0],
                diagnosis_id=fill_db['diagnosis_ids'][0],
            )
        )
        after_count = len(session.execute(tables.medical_books.select()).all())

        # Assert
        assert before_count + 1 == after_count
        assert isinstance(result, entities.MedicalBook)

    def test__add__with_no_reviews(self, repo, session, fill_db):
        # Setup
        before_count = len(session.execute(tables.medical_books.select()).all())

        # Call
        result = repo.add(
            entities.MedicalBook(
                title_history='История 1',
                patient_id=fill_db['patient_ids'][0],
                diagnosis_id=fill_db['diagnosis_ids'][0],
            )
        )
        after_count = len(session.execute(tables.medical_books.select()).all())

        # Assert
        assert before_count + 1 == after_count
        assert isinstance(result, entities.MedicalBook)


class TestRemove:
    def test__remove(self, repo, session, fill_db):
        # Setup
        before_count = len(session.execute(tables.medical_books.select()).all())
        med_book: entities.MedicalBook = session.query(entities.MedicalBook).first()

        # Call
        result = repo.remove(med_book)
        after_count = len(session.execute(tables.medical_books.select()).all())

        # Assert
        assert before_count - 1 == after_count
        assert isinstance(result, entities.MedicalBook)
