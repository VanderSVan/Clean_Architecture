import pytest
from sqlalchemy import select, func

from simple_medication_selection.adapters.database import repositories
from simple_medication_selection.application import entities, schemas
from .. import test_data


# ---------------------------------------------------------------------------------------
# SETUP
# ---------------------------------------------------------------------------------------
@pytest.fixture(scope='function', autouse=True)
def fill_db(session) -> dict[str, list[int]]:
    patient_ids: list[int] = test_data.insert_patients(session)
    diagnosis_ids: list[int] = test_data.insert_diagnoses(session)
    med_book_ids: list[int] = test_data.insert_medical_books(patient_ids, diagnosis_ids,
                                                             session)
    return {'patient_ids': patient_ids,
            'diagnosis_ids': diagnosis_ids,
            'med_book_ids': med_book_ids}


@pytest.fixture(scope='function')
def repo(transaction_context):
    return repositories.PatientsRepo(context=transaction_context)


# ---------------------------------------------------------------------------------------
# TESTS
# ---------------------------------------------------------------------------------------
class TestFetchById:
    def test__fetch_by_id(self, repo, session):
        # Setup
        patient = session.query(entities.Patient).first()

        # Call
        result = repo.fetch_by_id(patient.id)

        # Assert
        assert isinstance(result, entities.Patient)
        assert result.id == patient.id


class TestFetchByNickname:
    def test__fetch_by_nickname(self, repo, session):
        # Setup
        patient = session.query(entities.Patient).first()

        # Call
        result = repo.fetch_by_nickname(patient.nickname)

        # Assert
        assert isinstance(result, entities.Patient)
        assert result.nickname == patient.nickname


class TestFetchAll:
    def test__fetch_all(self, repo, session, fill_db):
        # Setup
        filter_params = schemas.FindPatients()

        # Call
        result = repo.fetch_all(filter_params)

        # Assert
        assert len(result) > 0
        assert len(result) == len(test_data.PATIENTS_DATA)
        assert all(isinstance(patient, entities.Patient) for patient in result)


class TestFetchByGender:
    def test__fetch_by_gender(self, repo, session, fill_db):
        # Setup
        patient_id: int = fill_db['patient_ids'][0]
        expected_patient: entities.Patient = session.execute(
            select(entities.Patient).where(entities.Patient.id == patient_id)
        ).scalar()
        filter_params = schemas.FindPatients(gender=expected_patient.gender)

        # Call
        result = repo.fetch_by_gender(filter_params)

        # Assert
        assert len(result) > 0
        for patient in result:
            assert isinstance(patient, entities.Patient)
            assert patient.gender == expected_patient.gender


class TestFetchByAge:
    @pytest.mark.parametrize('age_from, age_to', [(1, 100), (None, 100), (1, None)])
    def test__fetch_by_age(self, age_from, age_to, repo, session, fill_db):
        # Setup
        filter_params = schemas.FindPatients(age_from=age_from, age_to=age_to)

        # Call
        result = repo.fetch_by_age(filter_params)

        # Assert
        assert len(result) > 0
        for patient in result:
            assert isinstance(patient, entities.Patient)
            assert (patient.age >= age_from if age_from is not None else True)
            assert (patient.age <= age_to if age_to is not None else True)


class TestFetchBySkinType:
    def test__fetch_by_skin_type(self, repo, session, fill_db):
        # Setup
        patient_id: int = fill_db['patient_ids'][0]
        expected_patient: entities.Patient = session.execute(
            select(entities.Patient).where(entities.Patient.id == patient_id)
        ).scalar()
        filter_params = schemas.FindPatients(skin_type=expected_patient.skin_type)

        # Call
        result = repo.fetch_by_skin_type(filter_params)

        # Assert
        assert len(result) > 0
        for patient in result:
            assert isinstance(patient, entities.Patient)
            assert patient.skin_type == expected_patient.skin_type


class TestFetchByGenderAndAge:

    @pytest.mark.parametrize('age_from, age_to', [(1, 100), (None, 100), (1, None)])
    def test__fetch_by_gender_and_age(self, age_from, age_to, repo, session, fill_db):
        # Setup
        patient_id: int = fill_db['patient_ids'][0]
        expected_patient: entities.Patient = session.execute(
            select(entities.Patient).where(entities.Patient.id == patient_id)
        ).scalar()
        filter_params = schemas.FindPatients(gender=expected_patient.gender,
                                             age_from=age_from,
                                             age_to=age_to)

        # Call
        result = repo.fetch_by_gender_and_age(filter_params)

        # Assert
        assert len(result) > 0
        for patient in result:
            assert isinstance(patient, entities.Patient)
            assert patient.gender == expected_patient.gender
            assert (patient.age >= age_from if age_from is not None else True)
            assert (patient.age <= age_to if age_to is not None else True)


class TestFetchByGenderAndSkinType:
    def test__fetch_by_gender_and_skin_type(self, repo, session, fill_db):
        # Setup
        patient_id: int = fill_db['patient_ids'][0]
        expected_patient: entities.Patient = session.execute(
            select(entities.Patient).where(entities.Patient.id == patient_id)
        ).scalar()
        filter_params = schemas.FindPatients(gender=expected_patient.gender,
                                             skin_type=expected_patient.skin_type)

        # Call
        result = repo.fetch_by_gender_and_skin_type(filter_params)

        # Assert
        assert len(result) > 0
        for patient in result:
            assert isinstance(patient, entities.Patient)
            assert patient.gender == expected_patient.gender
            assert patient.skin_type == expected_patient.skin_type


class TestFetchByAgeAndSkinType:

    @pytest.mark.parametrize('age_from, age_to', [(1, 100), (None, 100), (1, None)])
    def test__fetch_by_age_and_skin_type(self, age_from, age_to, repo, session, fill_db):
        # Setup
        patient_id: int = fill_db['patient_ids'][0]
        expected_patient: entities.Patient = session.execute(
            select(entities.Patient).where(entities.Patient.id == patient_id)
        ).scalar()
        filter_params = schemas.FindPatients(age_from=age_from,
                                             age_to=age_to,
                                             skin_type=expected_patient.skin_type)

        # Call
        result = repo.fetch_by_age_and_skin_type(filter_params)

        # Assert
        assert len(result) > 0
        for patient in result:
            assert isinstance(patient, entities.Patient)
            assert patient.skin_type == expected_patient.skin_type
            assert (patient.age >= age_from if age_from is not None else True)
            assert (patient.age <= age_to if age_to is not None else True)


class TestFetchByGenderAgeAndSkinType:

    @pytest.mark.parametrize('age_from, age_to', [(1, 100), (None, 100), (1, None)])
    def test__fetch_by_gender_age_and_skin_type(self, age_from, age_to, repo, session,
                                                fill_db):
        # Setup
        patient_id: int = fill_db['patient_ids'][0]
        expected_patient: entities.Patient = session.execute(
            select(entities.Patient).where(entities.Patient.id == patient_id)
        ).scalar()
        filter_params = schemas.FindPatients(gender=expected_patient.gender,
                                             age_from=age_from,
                                             age_to=age_to,
                                             skin_type=expected_patient.skin_type)

        # Call
        result = repo.fetch_by_gender_age_and_skin_type(filter_params)

        # Assert
        assert len(result) > 0
        for patient in result:
            assert isinstance(patient, entities.Patient)
            assert patient.gender == expected_patient.gender
            assert patient.skin_type == expected_patient.skin_type
            assert (patient.age >= age_from if age_from is not None else True)
            assert (patient.age <= age_to if age_to is not None else True)


class TestAdd:
    def test__add(self, repo, session):
        # Setup
        before_count = session.execute(
            select(func.count(entities.Patient.id.distinct()))
        ).scalar()

        # Call
        result = repo.add(entities.Patient(nickname='SomeAmazingNickname',
                                           gender='female',
                                           age=20,
                                           skin_type='сухая'))

        # Setup
        after_count = session.execute(
            select(func.count(entities.Patient.id.distinct()))
        ).scalar()

        # Assert
        assert before_count + 1 == after_count
        assert isinstance(result, entities.Patient)


class TestRemove:
    def test__remove(self, repo, session, fill_db):
        # Setup
        before_count = session.execute(
            select(func.count(entities.Patient.id.distinct()))
        ).scalar()
        patient_to_remove: entities.Patient = session.query(entities.Patient).first()

        # Call
        result = repo.remove(patient_to_remove)

        # Setup
        after_count = session.execute(
            select(func.count(entities.Patient.id.distinct()))
        ).scalar()

        # Assert
        assert before_count - 1 == after_count
        assert isinstance(result, entities.Patient)

    def test__cascade_remove_orphaned_medical_books(self, repo, session, fill_db):
        # Setup
        patient_to_remove: entities.Patient = (
            session.execute(
                select(entities.Patient)
                .join(entities.MedicalBook,
                      entities.Patient.id == entities.MedicalBook.patient_id)
            ).scalar()
        )
        print(patient_to_remove)
        orphaned_medical_book_ids: list[entities.MedicalBook] = (
            session.execute(
                select(entities.MedicalBook.id)
                .where(entities.MedicalBook.patient_id == patient_to_remove.id)
            ).scalars().all()
        )
        print(orphaned_medical_book_ids)
        # Assert
        assert len(orphaned_medical_book_ids) > 0

        # Call
        result = repo.remove(patient_to_remove)

        # Setup
        medical_books_after_remove: list[entities.MedicalBook] = (
            session.execute(select(entities.MedicalBook.id)).scalars().all()
        )
        print(medical_books_after_remove)

        # Assert
        assert len(medical_books_after_remove) > 0
        for medical_book_id in orphaned_medical_book_ids:
            assert medical_book_id not in medical_books_after_remove


class TestPatientQueryPagination:

    @pytest.mark.parametrize('sort_field', [
        'id', 'nickname', 'gender', 'age', 'skin_type'
    ])
    def test__order_is_asc(self, sort_field, repo, session, fill_db):
        # Setup
        filter_params = schemas.FindPatients(sort_field=sort_field,
                                             sort_direction='asc')

        # Call
        result = repo.fetch_all(filter_params)

        # Assert
        assert len(result) > 0
        assert result == sorted(
            result,
            key=lambda patient: (
                float('inf') if getattr(patient, sort_field) is None
                else getattr(patient, sort_field)
            ),
            reverse=False
        )

    @pytest.mark.parametrize('sort_field', [
        'id', 'nickname', 'gender', 'age', 'skin_type'
    ])
    def test__order_is_desc(self, sort_field, repo, session, fill_db):
        # Setup
        filter_params = schemas.FindPatients(sort_field=sort_field,
                                             sort_direction='desc')

        # Call
        result = repo.fetch_all(filter_params)

        # Assert
        assert len(result) > 0
        assert result == sorted(
            result,
            key=lambda patient: (
                float('-inf') if getattr(patient, sort_field) is None
                else getattr(patient, sort_field)
            ),
            reverse=True
        )

    def test__with_limit(self, repo, session, fill_db):
        # Setup
        filter_params = schemas.FindPatients(limit=1)

        # Call
        result = repo.fetch_all(filter_params)

        # Assert
        assert len(result) == 1

    def test__with_offset(self, repo, session, fill_db):
        # Setup
        filter_params = schemas.FindPatients(offset=1)

        # Call
        result = repo.fetch_all(filter_params)

        # Assert
        assert len(result) == len(test_data.PATIENTS_DATA) - filter_params.offset
