import pytest

from sqlalchemy import select, func
from sqlalchemy.orm import joinedload

from simple_medication_selection.adapters.database import repositories
from simple_medication_selection.application import entities
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
    med_book_ids: list[int] = test_data.insert_medical_books(patient_ids, diagnosis_ids,
                                                             session)
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
    return repositories.ItemReviewsRepo(context=transaction_context)


# ---------------------------------------------------------------------------------------
# TESTS
# ---------------------------------------------------------------------------------------
class TestFetchById:

    def test__fetch_by_id(self, repo, session):
        # Setup
        review = session.query(entities.ItemReview).first()

        # Call
        result = repo.fetch_by_id(review.id)

        # Assert
        assert isinstance(result, entities.ItemReview)
        assert result.id == review.id


class TestFetchAll:

    def test__fetch_all(self, repo, session, fill_db):
        # Call
        result = repo.fetch_all(order_field='item_rating',
                                order_direction='desc',
                                limit=None,
                                offset=None)

        # Assert
        assert len(result) == len(test_data.REVIEWS_DATA)
        for review in result:
            assert isinstance(review, entities.ItemReview)

    def test__nulls_last(self, repo, session, fill_db):
        # Call
        result = repo.fetch_all(order_field='usage_period',
                                order_direction='asc',
                                limit=None,
                                offset=None)

        # Assert
        assert result[0].usage_period is not None
        assert result[-1].usage_period is None

    @pytest.mark.parametrize('order_field', [
        'id', 'item_id', 'is_helped', 'item_rating', 'item_count', 'usage_period',
    ])
    def test__order_is_asc(self, order_field, repo, session, fill_db):
        # Call
        result = repo.fetch_all(order_field=order_field,
                                order_direction='asc',
                                limit=None,
                                offset=None)

        # Assert
        assert result == sorted(
            result,
            key=lambda review: (
                float('inf') if getattr(review, order_field) is None
                else getattr(review, order_field)
            ),
            reverse=False
        )

    @pytest.mark.parametrize('order_field', [
        'id', 'item_id', 'is_helped', 'item_rating', 'item_count', 'usage_period',
    ])
    def test__order_is_desc(self, order_field, repo, session, fill_db):
        # Call
        result = repo.fetch_all(order_field=order_field,
                                order_direction='desc',
                                limit=None,
                                offset=None)

        # Assert
        assert result == sorted(
            result,
            key=lambda review: (
                float('-inf') if getattr(review, order_field) is None
                else getattr(review, order_field)
            ),
            reverse=True
        )

    def test__with_limit(self, repo, session, fill_db):
        # Setup
        limit = 1

        # Call
        result = repo.fetch_all(order_field='item_rating',
                                order_direction='desc',
                                limit=limit,
                                offset=None)

        # Assert
        assert len(result) == limit

    def test__with_offset(self, repo, session, fill_db):
        # Setup
        offset = 1

        # Call
        result = repo.fetch_all(order_field='item_rating',
                                order_direction='desc',
                                limit=None,
                                offset=offset)

        # Assert
        assert len(result) == len(test_data.REVIEWS_DATA) - offset


class TestFetchAllByItemId:

    def test__fetch_all_by_item(self, repo, session, fill_db):
        # Setup
        item_id: int = (
            session.query(entities.TreatmentItem)
            .filter_by(title=test_data.ITEMS_DATA[0]['title'])
            .first()
            .id
        )
        review_count_by_item: int = session.execute(
            select(func.count(entities.ItemReview.id.distinct()))
            .where(entities.ItemReview.item_id == item_id)
        ).scalar()

        # Call
        result = repo.fetch_all_by_item(item_id=item_id,
                                        order_field='item_rating',
                                        order_direction='desc',
                                        limit=None,
                                        offset=None)

        # Assert
        assert len(result) == review_count_by_item

    def test__nulls_last(self, repo, session, fill_db):
        # Setup
        item_id: int = (
            session.query(entities.TreatmentItem)
            .filter_by(title=test_data.ITEMS_DATA[2]['title'])
            .first()
            .id
        )

        # Call
        result = repo.fetch_all_by_item(item_id=item_id,
                                        order_field='usage_period',
                                        order_direction='asc',
                                        limit=None,
                                        offset=None)

        # Assert
        assert result[0].usage_period is not None
        assert result[-1].usage_period is None

    @pytest.mark.parametrize('order_field', [
        'id', 'item_id', 'is_helped', 'item_rating', 'item_count', 'usage_period',
    ])
    def test__order_is_asc(self, order_field, repo, session, fill_db):
        # Setup
        item_id: int = (
            session.query(entities.TreatmentItem)
            .filter_by(title=test_data.ITEMS_DATA[0]['title'])
            .first()
            .id
        )

        # Call
        result = repo.fetch_all_by_item(item_id=item_id,
                                        order_field=order_field,
                                        order_direction='asc',
                                        limit=None,
                                        offset=None)

        # Assert
        assert result == sorted(
            result,
            key=lambda review: (
                float('-inf') if getattr(review, order_field) is None
                else getattr(review, order_field)
            ),
            reverse=False
        )

    @pytest.mark.parametrize('order_field', [
        'id', 'item_id', 'is_helped', 'item_rating', 'item_count', 'usage_period',
    ])
    def test__order_is_desc(self, order_field, repo, session, fill_db):
        # Setup
        item_id: int = (
            session.query(entities.TreatmentItem)
            .filter_by(title=test_data.ITEMS_DATA[0]['title'])
            .first()
            .id
        )

        # Call
        result = repo.fetch_all_by_item(item_id=item_id,
                                        order_field=order_field,
                                        order_direction='desc',
                                        limit=None,
                                        offset=None)

        # Assert
        assert result == sorted(
            result,
            key=lambda review: (
                float('-inf') if getattr(review, order_field) is None
                else getattr(review, order_field)
            ),
            reverse=True
        )

    def test__with_limit(self, repo, session, fill_db):
        # Setup
        item_id: int = (
            session.query(entities.TreatmentItem)
            .filter_by(title=test_data.ITEMS_DATA[0]['title'])
            .first()
            .id
        )
        limit = 1

        # Call
        result = repo.fetch_all_by_item(item_id=item_id,
                                        order_field='item_rating',
                                        order_direction='desc',
                                        limit=limit,
                                        offset=None)

        # Assert
        assert len(result) == limit

    def test__with_offset(self, repo, session, fill_db):
        # Setup
        offset = 1
        item_id: int = (
            session.query(entities.TreatmentItem)
            .filter_by(title=test_data.ITEMS_DATA[0]['title'])
            .first()
            .id
        )
        review_count_by_item: int = session.execute(
            select(func.count(entities.ItemReview.id.distinct()))
            .where(entities.ItemReview.item_id == item_id)
        ).scalar()

        # Call
        result = repo.fetch_all_by_item(item_id=item_id,
                                        order_field='item_rating',
                                        order_direction='desc',
                                        limit=None,
                                        offset=offset)

        # Assert
        assert len(result) == review_count_by_item - offset


class TestFetchReviewsByPatient:
    def test__fetch_reviews_by_patient(self, repo, session, fill_db):
        # Setup
        patient_id: int = (
            session.query(entities.Patient)
            .filter_by(nickname=test_data.PATIENTS_DATA[0]['nickname'])
            .first()
            .id
        )
        review_count_by_patient: int = session.execute(
            select(func.count(entities.ItemReview.id.distinct()))
            .join(entities.MedicalBook.item_reviews)
            .where(entities.MedicalBook.patient_id == patient_id)
        ).scalar()

        # Call
        result = repo.fetch_reviews_by_patient(patient_id=patient_id,
                                               order_field='item_rating',
                                               order_direction='desc',
                                               limit=None,
                                               offset=None)

        # Assert
        assert len(result) == review_count_by_patient
        for review in result:
            assert isinstance(review, entities.ItemReview)

    def test__nulls_last(self, repo, session, fill_db):
        # Setup
        patient_id: int = (
            session.query(entities.Patient)
            .filter_by(nickname=test_data.PATIENTS_DATA[0]['nickname'])
            .first()
            .id
        )

        # Call
        result = repo.fetch_reviews_by_patient(patient_id=patient_id,
                                               order_field='usage_period',
                                               order_direction='asc',
                                               limit=None,
                                               offset=None)

        # Assert
        assert result[0].usage_period is not None
        assert result[-1].usage_period is None

    @pytest.mark.parametrize('order_field', [
        'id', 'item_id', 'is_helped', 'item_rating', 'item_count', 'usage_period',
    ])
    def test__order_is_asc(self, order_field, repo, session, fill_db):
        # Setup
        patient_id: int = (
            session.query(entities.Patient)
            .filter_by(nickname=test_data.PATIENTS_DATA[0]['nickname'])
            .first()
            .id
        )

        # Call
        result = repo.fetch_reviews_by_patient(patient_id=patient_id,
                                               order_field=order_field,
                                               order_direction='asc',
                                               limit=None,
                                               offset=None)

        # Assert
        assert result == sorted(
            result,
            key=lambda review: (
                float('inf') if getattr(review, order_field) is None
                else getattr(review, order_field)
            ),
            reverse=False
        )

    @pytest.mark.parametrize('order_field', [
        'id', 'item_id', 'is_helped', 'item_rating', 'item_count', 'usage_period',
    ])
    def test__order_is_desc(self, order_field, repo, session, fill_db):
        # Setup
        patient_id: int = (
            session.query(entities.Patient)
            .filter_by(nickname=test_data.PATIENTS_DATA[0]['nickname'])
            .first()
            .id
        )

        # Call
        result = repo.fetch_reviews_by_patient(patient_id=patient_id,
                                               order_field=order_field,
                                               order_direction='desc',
                                               limit=None,
                                               offset=None)

        # Assert
        assert result == sorted(
            result,
            key=lambda review: (
                float('-inf') if getattr(review, order_field) is None
                else getattr(review, order_field)
            ),
            reverse=True
        )

    def test__with_limit(self, repo, session, fill_db):
        # Setup
        patient_id: int = (
            session.query(entities.Patient)
            .filter_by(nickname=test_data.PATIENTS_DATA[0]['nickname'])
            .first()
            .id
        )
        limit = 1

        # Call
        result = repo.fetch_reviews_by_patient(patient_id=patient_id,
                                               order_field='item_rating',
                                               order_direction='desc',
                                               limit=limit,
                                               offset=None)

        # Assert
        assert len(result) == limit

    def test__with_offset(self, repo, session, fill_db):
        # Setup
        offset = 1
        patient_id: int = (
            session.query(entities.Patient)
            .filter_by(nickname=test_data.PATIENTS_DATA[0]['nickname'])
            .first()
            .id
        )
        review_count_by_patient: int = session.execute(
            select(func.count(entities.ItemReview.id.distinct()))
            .join(entities.MedicalBook.item_reviews)
            .where(entities.MedicalBook.patient_id == patient_id)
        ).scalar()

        # Call
        result = repo.fetch_reviews_by_patient(patient_id=patient_id,
                                               order_field='item_rating',
                                               order_direction='desc',
                                               limit=None,
                                               offset=offset)

        # Assert
        assert len(result) == review_count_by_patient - offset


class TestFetchPatientReviewsByItem:
    def test__fetch_patient_reviews_by_item(self, repo, session, fill_db):
        # Setup
        item_id: int = (
            session.query(entities.TreatmentItem)
            .filter_by(title=test_data.ITEMS_DATA[0]['title'])
            .first()
            .id
        )
        patient_id: int = (
            session.query(entities.Patient)
            .filter_by(nickname=test_data.PATIENTS_DATA[0]['nickname'])
            .first()
            .id
        )
        review_count_by_patient_and_item: int = session.execute(
            select(func.count(entities.ItemReview.id.distinct()))
            .join(entities.MedicalBook.item_reviews)
            .where(entities.MedicalBook.patient_id == patient_id,
                   entities.ItemReview.item_id == item_id)
        ).scalar()

        # Call
        result = repo.fetch_patient_reviews_by_item(patient_id=patient_id,
                                                    item_id=item_id,
                                                    order_field='item_rating',
                                                    order_direction='desc',
                                                    limit=None,
                                                    offset=None)

        # Assert
        assert len(result) == review_count_by_patient_and_item
        for review in result:
            assert isinstance(review, entities.ItemReview)

    def test__nulls_last(self, repo, session, fill_db):
        # Setup
        item_id: int = (
            session.query(entities.TreatmentItem)
            .filter_by(title=test_data.ITEMS_DATA[2]['title'])
            .first()
            .id
        )
        patient_id: int = (
            session.query(entities.Patient)
            .filter_by(nickname=test_data.PATIENTS_DATA[0]['nickname'])
            .first()
            .id
        )

        # Call
        result = repo.fetch_patient_reviews_by_item(patient_id=patient_id,
                                                    item_id=item_id,
                                                    order_field='usage_period',
                                                    order_direction='asc',
                                                    limit=None,
                                                    offset=None)

        # Assert
        assert result[-1].usage_period is None

    @pytest.mark.parametrize('order_field', [
        'id', 'item_id', 'is_helped', 'item_rating', 'item_count', 'usage_period',
    ])
    def test__order_is_asc(self, order_field, repo, session, fill_db):
        # Setup
        item_id: int = (
            session.query(entities.TreatmentItem)
            .filter_by(title=test_data.ITEMS_DATA[0]['title'])
            .first()
            .id
        )
        patient_id: int = (
            session.query(entities.Patient)
            .filter_by(nickname=test_data.PATIENTS_DATA[0]['nickname'])
            .first()
            .id
        )

        # Call
        result = repo.fetch_patient_reviews_by_item(patient_id=patient_id,
                                                    item_id=item_id,
                                                    order_field=order_field,
                                                    order_direction='asc',
                                                    limit=None,
                                                    offset=None)

        # Assert
        assert result == sorted(
            result,
            key=lambda review: (
                float('inf') if getattr(review, order_field) is None
                else getattr(review, order_field)
            ),
        )

    @pytest.mark.parametrize('order_field', [
        'id', 'item_id', 'is_helped', 'item_rating', 'item_count', 'usage_period',
    ])
    def test__order_is_desc(self, order_field, repo, session, fill_db):
        # Setup
        item_id: int = (
            session.query(entities.TreatmentItem)
            .filter_by(title=test_data.ITEMS_DATA[0]['title'])
            .first()
            .id
        )
        patient_id: int = (
            session.query(entities.Patient)
            .filter_by(nickname=test_data.PATIENTS_DATA[0]['nickname'])
            .first()
            .id
        )

        # Call
        result = repo.fetch_patient_reviews_by_item(patient_id=patient_id,
                                                    item_id=item_id,
                                                    order_field=order_field,
                                                    order_direction='desc',
                                                    limit=None,
                                                    offset=None)

        # Assert
        assert result == sorted(
            result,
            key=lambda review: (
                float('-inf') if getattr(review, order_field) is None
                else getattr(review, order_field)
            ),
            reverse=True
        )

    def test__with_limit(self, repo, session, fill_db):
        # Setup
        item_id: int = (
            session.query(entities.TreatmentItem)
            .filter_by(title=test_data.ITEMS_DATA[0]['title'])
            .first()
            .id
        )
        patient_id: int = (
            session.query(entities.Patient)
            .filter_by(nickname=test_data.PATIENTS_DATA[0]['nickname'])
            .first()
            .id
        )
        limit = 0

        # Call
        result = repo.fetch_patient_reviews_by_item(patient_id=patient_id,
                                                    item_id=item_id,
                                                    order_field='item_rating',
                                                    order_direction='desc',
                                                    limit=limit,
                                                    offset=None)

        # Assert
        assert len(result) == limit

    def test__with_offset(self, repo, session, fill_db):
        # Setup
        offset = 1
        item_id: int = (
            session.query(entities.TreatmentItem)
            .filter_by(title=test_data.ITEMS_DATA[0]['title'])
            .first()
            .id
        )
        patient_id: int = (
            session.query(entities.Patient)
            .filter_by(nickname=test_data.PATIENTS_DATA[0]['nickname'])
            .first()
            .id
        )
        patient_reviews_count_by_item: int = session.execute(
            select(func.count(entities.ItemReview.id.distinct()))
            .join(entities.MedicalBook.item_reviews)
            .where(
                entities.MedicalBook.patient_id == patient_id,
                entities.ItemReview.item_id == item_id
            )
        ).scalar()

        # Call
        result = repo.fetch_patient_reviews_by_item(patient_id=patient_id,
                                                    item_id=item_id,
                                                    order_field='item_rating',
                                                    order_direction='desc',
                                                    limit=None,
                                                    offset=offset)

        # Assert
        assert len(result) == patient_reviews_count_by_item - offset


class TestFetchByRating:
    def test__fetch_by_rating(self, repo, session, fill_db):
        # Setup
        min_rating = 2.0
        max_rating = 10.0

        # Call
        result = repo.fetch_by_rating(min_rating=min_rating,
                                      max_rating=max_rating,
                                      order_field='item_rating',
                                      order_direction='desc',
                                      limit=None,
                                      offset=None)

        # Assert
        assert len(result) == len(test_data.REVIEWS_DATA)
        for review in result:
            assert isinstance(review, entities.ItemReview)
            assert review.item_rating >= min_rating
            assert review.item_rating <= max_rating

    def test__nulls_last(self, repo, session, fill_db):
        # Setup
        min_rating = 2.0
        max_rating = 10.0

        # Call
        result = repo.fetch_by_rating(min_rating=min_rating,
                                      max_rating=max_rating,
                                      order_field='usage_period',
                                      order_direction='desc',
                                      limit=None,
                                      offset=None)

        # Assert
        assert result[0].usage_period is not None
        assert result[-1].usage_period is None

    @pytest.mark.parametrize('order_field', [
        'id', 'item_id', 'is_helped', 'item_rating', 'item_count', 'usage_period',
    ])
    def test__order_is_asc(self, order_field, repo, session, fill_db):
        # Setup
        min_rating = 2.0
        max_rating = 10.0

        # Call
        result = repo.fetch_by_rating(min_rating=min_rating,
                                      max_rating=max_rating,
                                      order_field=order_field,
                                      order_direction='asc',
                                      limit=None,
                                      offset=None)

        # Assert
        assert result == sorted(
            result,
            key=lambda review: (
                float('inf') if getattr(review, order_field) is None
                else getattr(review, order_field)
            ),
            reverse=False
        )

    @pytest.mark.parametrize('order_field', [
        'id', 'item_id', 'is_helped', 'item_rating', 'item_count', 'usage_period',
    ])
    def test__order_is_desc(self, order_field, repo, session, fill_db):
        # Setup
        min_rating = 2.0
        max_rating = 10.0

        # Call
        result = repo.fetch_by_rating(min_rating=min_rating,
                                      max_rating=max_rating,
                                      order_field=order_field,
                                      order_direction='desc',
                                      limit=None,
                                      offset=None)

        # Assert
        assert result == sorted(
            result,
            key=lambda review: (
                float('-inf') if getattr(review, order_field) is None
                else getattr(review, order_field)
            ),
            reverse=True
        )

    def test__with_limit(self, repo, session, fill_db):
        # Setup
        min_rating = 2.0
        max_rating = 10.0
        limit = 1

        # Call
        result = repo.fetch_by_rating(min_rating=min_rating,
                                      max_rating=max_rating,
                                      order_field='item_rating',
                                      order_direction='desc',
                                      limit=limit,
                                      offset=None)

        # Assert
        assert len(result) == limit

    def test__with_offset(self, repo, session, fill_db):
        # Setup
        min_rating = 2.0
        max_rating = 10.0
        offset = 1

        # Call
        result = repo.fetch_by_rating(min_rating=min_rating,
                                      max_rating=max_rating,
                                      order_field='item_rating',
                                      order_direction='desc',
                                      limit=None,
                                      offset=offset)

        # Assert
        assert len(result) == len(test_data.REVIEWS_DATA) - offset


class TestFetchByHelpedStatus:
    def test__fetch_by_helped_status(self, repo, session, fill_db):
        # Setup
        helped_status = True
        review_count_by_helped_status: int = session.execute(
            select(func.count())
            .select_from(entities.ItemReview)
            .where(entities.ItemReview.is_helped == helped_status)
        ).scalar()

        # Call
        result = repo.fetch_by_helped_status(is_helped=helped_status,
                                             order_field='item_rating',
                                             order_direction='desc',
                                             limit=None,
                                             offset=None)

        # Assert
        assert len(result) == review_count_by_helped_status
        for review in result:
            assert isinstance(review, entities.ItemReview)
            assert review.is_helped == helped_status

    def test__nulls_last(self, repo, session, fill_db):
        # Setup
        helped_status = True

        # Call
        result = repo.fetch_by_helped_status(is_helped=helped_status,
                                             order_field='usage_period',
                                             order_direction='desc',
                                             limit=None,
                                             offset=None)

        # Assert
        assert result[0].usage_period is not None
        assert result[-1].usage_period is None

    @pytest.mark.parametrize('order_field', [
        'id', 'item_id', 'is_helped', 'item_rating', 'item_count', 'usage_period',
    ])
    def test__order_is_asc(self, order_field, repo, session, fill_db):
        # Setup
        helped_status = True

        # Call
        result = repo.fetch_by_helped_status(is_helped=helped_status,
                                             order_field=order_field,
                                             order_direction='asc',
                                             limit=None,
                                             offset=None)

        # Assert
        assert result == sorted(
            result,
            key=lambda review: (
                float('inf') if getattr(review, order_field) is None
                else getattr(review, order_field)
            ),
            reverse=False
        )

    @pytest.mark.parametrize('order_field', [
        'id', 'item_id', 'is_helped', 'item_rating', 'item_count', 'usage_period',
    ])
    def test__order_is_desc(self, order_field, repo, session, fill_db):
        # Setup
        helped_status = True

        # Call
        result = repo.fetch_by_helped_status(is_helped=helped_status,
                                             order_field=order_field,
                                             order_direction='desc',
                                             limit=None,
                                             offset=None)

        # Assert
        assert result == sorted(
            result,
            key=lambda review: (
                float('-inf') if getattr(review, order_field) is None
                else getattr(review, order_field)
            ),
            reverse=True
        )

    def test__with_limit(self, repo, session, fill_db):
        # Setup
        helped_status = True
        limit = 1

        # Call
        result = repo.fetch_by_helped_status(is_helped=helped_status,
                                             order_field='item_rating',
                                             order_direction='desc',
                                             limit=limit,
                                             offset=None)

        # Assert
        assert len(result) == limit

    def test__with_offset(self, repo, session, fill_db):
        # Setup
        helped_status = True
        offset = 1
        review_count_by_helped_status: int = session.execute(
            select(func.count())
            .select_from(entities.ItemReview)
            .where(entities.ItemReview.is_helped == helped_status)
        ).scalar()

        # Call
        result = repo.fetch_by_helped_status(is_helped=helped_status,
                                             order_field='item_rating',
                                             order_direction='desc',
                                             limit=None,
                                             offset=offset)

        # Assert
        assert len(result) == review_count_by_helped_status - offset


class TestAdd:
    def test__add(self, repo, session, fill_db):
        # Setup
        before_count = session.execute(
            select(func.count(entities.ItemReview.id.distinct()))
        ).scalar()

        # Call
        result = repo.add(entities.ItemReview(
            item_id=fill_db['item_ids'][0],
            is_helped=True,
            item_rating=7.5,
            item_count=1,
            usage_period=2592000
        ))
        after_count = session.execute(
            select(func.count(entities.ItemReview.id.distinct()))
        ).scalar()

        # Assert
        assert before_count + 1 == after_count
        assert isinstance(result, entities.ItemReview)

    def test__cascade_update_effect_for_item(self, repo, session, fill_db):
        # Setup
        review_id = fill_db['review_ids'][0]
        old_helped_status = True
        new_helped_status = False

        review_before_update: entities.ItemReview = session.execute(
            select(entities.ItemReview)
            .where(
                entities.ItemReview.id == review_id,
                entities.ItemReview.is_helped == old_helped_status
            )
        ).scalars().first()

        # Assert
        assert review_before_update.is_helped == old_helped_status

        # Call
        review_before_update.is_helped = new_helped_status

        # Setup
        item_after_update: entities.ItemReview = session.execute(
            select(entities.TreatmentItem)
            .where(entities.TreatmentItem.id == review_before_update.item_id)
        ).scalars().first()
        review_after_update: entities.ItemReview = next(
            (review for review in item_after_update.reviews if review.id == review_id),
            None
        )

        # Assert
        assert review_after_update.is_helped == new_helped_status

    def test__cascade_update_effect_for_med_book(self, repo, session, fill_db):
        # Setup
        review_id = fill_db['review_ids'][0]
        old_helped_status = True
        new_helped_status = False

        review_before_update: entities.ItemReview = session.execute(
            select(entities.ItemReview)
            .where(
                entities.ItemReview.id == review_id,
                entities.ItemReview.is_helped == old_helped_status
            )
        ).scalars().first()

        # Assert
        assert review_before_update.is_helped == old_helped_status

        # Call
        review_before_update.is_helped = new_helped_status

        # Setup
        med_book_after_update: entities.MedicalBook = session.execute(
            select(entities.MedicalBook)
            .join(entities.MedicalBook.item_reviews)
            .where(entities.MedicalBook.item_reviews.any(
                entities.ItemReview.id == review_id)
            )
        ).scalars().first()
        review_after_update: entities.ItemReview = next(
            (review for review in med_book_after_update.item_reviews
             if review.id == review_id),
            None
        )

        # Assert
        assert review_after_update.is_helped == new_helped_status


class TestRemove:
    def test__remove(self, repo, session, fill_db):
        # Setup
        before_count = session.execute(
            select(func.count(entities.ItemReview.id.distinct()))
        ).scalar()
        review_to_remove: entities.ItemReview = session.query(entities.ItemReview).first()

        # Call
        result = repo.remove(review_to_remove)

        # Setup
        after_count = session.execute(
            select(func.count(entities.ItemReview.id.distinct()))
        ).scalar()

        # Assert
        assert before_count - 1 == after_count
        assert isinstance(result, entities.ItemReview)

    def test__cascade_delete_item(self, repo, session, fill_db):
        # Setup
        review_to_remove: entities.ItemReview = session.query(entities.ItemReview).first()
        review_id_to_remove: int = review_to_remove.id
        item: entities.TreatmentItem = session.execute(
            select(entities.TreatmentItem)
            .distinct()
            .join(entities.TreatmentItem.reviews)
            .where(entities.TreatmentItem.reviews.any(
                entities.ItemReview.id == review_id_to_remove)
            )
        ).scalars().one_or_none()

        # Assert
        assert any(review_id_to_remove == review.id for review in item.reviews)

        # Call
        repo.remove(review_to_remove)

        # Setup
        session.refresh(item)

        # Assert
        assert all(review_id_to_remove != review.id for review in item.reviews)

    def test__cascade_delete_med_book(self, repo, session, fill_db):
        # Setup
        review_to_remove: entities.ItemReview = session.query(entities.ItemReview).first()
        med_books: list[entities.MedicalBook] = session.execute(
            select(entities.MedicalBook)
            .distinct()
            .where(entities.MedicalBook.item_reviews.any(
                entities.ItemReview.id == review_to_remove.id)
            )
            .options(joinedload(entities.MedicalBook.item_reviews))
        ).scalars().unique().all()

        # Assert
        assert any(review_to_remove in med_book.item_reviews for med_book in med_books)

        # Call
        repo.remove(review_to_remove)

        # Setup
        for med_book in med_books:
            session.refresh(med_book)

        # Assert
        assert len(med_books) > 0
        assert all(review_to_remove not in med_book.item_reviews for med_book in
                   med_books)
