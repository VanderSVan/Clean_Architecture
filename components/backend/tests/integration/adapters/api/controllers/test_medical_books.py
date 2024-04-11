from dataclasses import asdict
from unittest.mock import call

from simple_medication_selection.application import entities, dtos, schemas

# ---------------------------------------------------------------------------------------
# SETUP
# ---------------------------------------------------------------------------------------
MEDICAL_BOOK_1 = entities.MedicalBook(
    id=1,
    title_history='История моей болезни 1',
    history='Анамнез болезни 1',
    patient_id=1,
    diagnosis_id=1,
    symptoms=[entities.Symptom(id=1, name='Симптом 1'),
              entities.Symptom(id=2, name='Симптом 2')],
    item_reviews=[
        entities.ItemReview(id=1,
                            item_id=1,
                            is_helped=True,
                            item_rating=9.5,
                            item_count=5,
                            usage_period=7776000),
        entities.ItemReview(id=2,
                            item_id=2,
                            is_helped=False,
                            item_rating=3.5,
                            item_count=1,
                            usage_period=5184000)
    ]
)
MEDICAL_BOOK_2 = entities.MedicalBook(
    id=2,
    title_history='История моей болезни 2',
    history='Анамнез болезни 2',
    patient_id=2,
    diagnosis_id=2,
    symptoms=[entities.Symptom(id=3, name='Симптом 3'),
              entities.Symptom(id=4, name='Симптом 4')],
    item_reviews=[
        entities.ItemReview(id=3,
                            item_id=3,
                            is_helped=True,
                            item_rating=7.5,
                            item_count=3,
                            usage_period=7776000),
    ]
)
MEDICAL_BOOK_LIST: list[entities.MedicalBook] = [MEDICAL_BOOK_1, MEDICAL_BOOK_2]
FILTER_PARAMS = schemas.FindMedicalBooks(
    patient_id=1,
    item_ids=[1, 2],
    is_helped=True,
    diagnosis_id=1,
    symptom_ids=[1, 2],
    match_all_symptoms=True,
    sort_field='diagnosis_id',
    sort_direction='desc',
    limit=10,
    offset=0
)
DEFAULT_FILTER_PARAMS = schemas.FindMedicalBooks()
TEST_URL = (
    '{path}?'
    f'patient_id={FILTER_PARAMS.patient_id}&'
    f'item_ids={FILTER_PARAMS.item_ids[0]}&'
    f'item_ids={FILTER_PARAMS.item_ids[1]}&'
    f'is_helped={FILTER_PARAMS.is_helped}&'
    f'diagnosis_id={FILTER_PARAMS.diagnosis_id}&'
    f'symptom_ids={FILTER_PARAMS.symptom_ids[0]}&'
    f'symptom_ids={FILTER_PARAMS.symptom_ids[1]}&'
    f'match_all_symptoms={FILTER_PARAMS.match_all_symptoms}&'
    f'sort_field={FILTER_PARAMS.sort_field}&'
    f'sort_direction={FILTER_PARAMS.sort_direction}&'
    f'limit={FILTER_PARAMS.limit}&'
    f'offset={FILTER_PARAMS.offset}'
)


# ---------------------------------------------------------------------------------------
# TESTS
# ---------------------------------------------------------------------------------------
class TestOnGet:
    def test__on_get(self, medical_book_service, client):
        # Setup
        returned_med_books = [dtos.MedicalBook(**med_book.__dict__)
                              for med_book in MEDICAL_BOOK_LIST]

        # Тестовый вывод `find_med_books` может отличаться от реального вывода
        medical_book_service.find_med_books.return_value = returned_med_books

        # Call
        response = client.simulate_get(TEST_URL.format(path='/medical_books'))

        # Assert
        assert response.status_code == 200
        assert response.json == [
            med_book.dict() for med_book in returned_med_books if med_book is not None
        ]
        assert medical_book_service.method_calls == [call.find_med_books(FILTER_PARAMS)]

    def test__on_get_without_filters(self, medical_book_service, client):
        # Setup
        returned_med_books = [dtos.MedicalBook(**med_book.__dict__)
                              for med_book in MEDICAL_BOOK_LIST]

        # Тестовый вывод `find_med_books` может отличаться от реального вывода
        medical_book_service.find_med_books.return_value = returned_med_books

        # Call
        response = client.simulate_get('/medical_books')

        # Assert
        assert response.status_code == 200
        assert response.json == [
            med_book.dict() for med_book in returned_med_books if med_book is not None
        ]
        assert medical_book_service.method_calls == [
            call.find_med_books(DEFAULT_FILTER_PARAMS)
        ]


class TestOnGetWithSymptoms:
    def test__on_get_with_symptoms(self, medical_book_service, client):
        # Setup
        returned_med_books = [dtos.MedicalBookWithSymptoms(**med_book.__dict__)
                              for med_book in MEDICAL_BOOK_LIST]

        # Тестовый вывод `find_med_books` может отличаться от реального вывода
        medical_book_service.find_med_books_with_symptoms.return_value = (
            returned_med_books
        )

        # Call
        response = client.simulate_get(TEST_URL.format(path='/medical_books/symptoms'))

        # Assert
        assert response.status_code == 200
        assert response.json == [med_book.dict() for med_book in returned_med_books]
        assert medical_book_service.method_calls == [
            call.find_med_books_with_symptoms(FILTER_PARAMS)
        ]

    def test__on_get_with_symptoms_without_filters(self, medical_book_service, client):
        # Setup
        returned_med_books = [dtos.MedicalBookWithSymptoms(**med_book.__dict__)
                              for med_book in MEDICAL_BOOK_LIST]

        # Тестовый вывод `find_med_books` может отличаться от реального вывода
        medical_book_service.find_med_books_with_symptoms.return_value = (
            returned_med_books
        )

        # Call
        response = client.simulate_get('/medical_books/symptoms')

        # Assert
        assert response.status_code == 200
        assert response.json == [med_book.dict() for med_book in returned_med_books]
        assert medical_book_service.method_calls == [
            call.find_med_books_with_symptoms(DEFAULT_FILTER_PARAMS)
        ]


class TestOnGetWithReviews:
    def test__on_get_with_reviews(self, medical_book_service, client):
        # Setup
        returned_med_books = [dtos.MedicalBookWithItemReviews(**med_book.__dict__)
                              for med_book in MEDICAL_BOOK_LIST]

        # Тестовый вывод `find_med_books` может отличаться от реального вывода
        medical_book_service.find_med_books_with_reviews.return_value = returned_med_books

        # Call
        response = client.simulate_get(TEST_URL.format(path='/medical_books/reviews'))

        # Assert
        assert response.status_code == 200
        assert response.json == [med_book.dict() for med_book in returned_med_books]
        assert medical_book_service.method_calls == [
            call.find_med_books_with_reviews(FILTER_PARAMS)
        ]

    def test__on_get_with_reviews_without_filters(self, medical_book_service, client):
        # Setup
        returned_med_books = [dtos.MedicalBookWithItemReviews(**med_book.__dict__)
                              for med_book in MEDICAL_BOOK_LIST]

        # Тестовый вывод `find_med_books` может отличаться от реального вывода
        medical_book_service.find_med_books_with_reviews.return_value = returned_med_books

        # Call
        response = client.simulate_get('/medical_books/reviews')

        # Assert
        assert response.status_code == 200
        assert response.json == [med_book.dict() for med_book in returned_med_books]
        assert medical_book_service.method_calls == [
            call.find_med_books_with_reviews(DEFAULT_FILTER_PARAMS)
        ]


class TestOnGetWithSymptomsAndReviews:
    def test__on_get_with_symptoms_and_reviews(self, medical_book_service, client):
        # Setup
        # Тестовый вывод `find_med_books_with_symptoms_and_reviews` может отличаться от реального вывода
        medical_book_service.find_med_books_with_symptoms_and_reviews.return_value = (
            MEDICAL_BOOK_LIST
        )

        # Call
        response = client.simulate_get(
            TEST_URL.format(path='/medical_books/symptoms/reviews')
        )

        # Assert
        assert response.status_code == 200
        assert response.json == [asdict(med_book) for med_book in MEDICAL_BOOK_LIST]
        assert medical_book_service.method_calls == [
            call.find_med_books_with_symptoms_and_reviews(FILTER_PARAMS)
        ]

    def test__on_get_with_symptoms_and_reviews_without_filters(self, medical_book_service,
                                                               client):
        # Setup
        # Тестовый вывод `find_med_books_with_symptoms_and_reviews` может отличаться от
        # реального вывода
        medical_book_service.find_med_books_with_symptoms_and_reviews.return_value = (
            MEDICAL_BOOK_LIST
        )

        # Call
        response = client.simulate_get('/medical_books/symptoms/reviews')

        # Assert
        assert response.status_code == 200
        assert response.json == [asdict(med_book) for med_book in MEDICAL_BOOK_LIST]
        assert medical_book_service.method_calls == [
            call.find_med_books_with_symptoms_and_reviews(DEFAULT_FILTER_PARAMS)
        ]

    def test__on_get_with_reviews_and_symptoms(self, medical_book_service, client):
        # Setup
        # Тестовый вывод `find_med_books_with_symptoms_and_reviews` может отличаться от
        # реального вывода
        medical_book_service.find_med_books_with_symptoms_and_reviews.return_value = (
            MEDICAL_BOOK_LIST
        )

        # Call
        response = client.simulate_get(
            TEST_URL.format(path='/medical_books/reviews/symptoms')
        )
        # Assert
        assert response.status_code == 200
        assert response.json == [asdict(med_book) for med_book in MEDICAL_BOOK_LIST]
        assert medical_book_service.method_calls == [
            call.find_med_books_with_symptoms_and_reviews(FILTER_PARAMS)
        ]

    def test__on_get_with_reviews_and_symptoms_without_filters(self, medical_book_service,
                                                               client):
        # Setup
        # Тестовый вывод `find_med_books_with_symptoms_and_reviews` может отличаться от
        # реального вывода
        medical_book_service.find_med_books_with_symptoms_and_reviews.return_value = (
            MEDICAL_BOOK_LIST
        )

        # Call
        response = client.simulate_get('/medical_books/reviews/symptoms')

        # Assert
        assert response.status_code == 200
        assert response.json == [asdict(med_book) for med_book in MEDICAL_BOOK_LIST]
        assert medical_book_service.method_calls == [
            call.find_med_books_with_symptoms_and_reviews(DEFAULT_FILTER_PARAMS)
        ]


class TestOnGetById:
    def test__on_get_by_id(self, medical_book_service, client):
        # Setup
        returned_med_book = dtos.MedicalBook(**MEDICAL_BOOK_1.__dict__)
        med_book_id = returned_med_book.id
        # Тестовый вывод `get_med_book` может отличаться от реального вывода
        medical_book_service.get_med_book.return_value = returned_med_book

        # Call
        response = client.simulate_get(f'/medical_books/{med_book_id}')

        # Assert
        assert response.status_code == 200
        assert response.json == returned_med_book.dict()
        assert medical_book_service.method_calls == [call.get_med_book(str(med_book_id))]


class TestOnGetByIdWithSymptoms:
    def test__on_get_by_id_with_symptoms(self, medical_book_service, client):
        # Setup
        returned_med_book = dtos.MedicalBookWithSymptoms(**MEDICAL_BOOK_1.__dict__)
        med_book_id = returned_med_book.id
        # Тестовый вывод `get_med_book_with_symptoms` может отличаться от реального вывода
        medical_book_service.get_med_book_with_symptoms.return_value = returned_med_book

        # Call
        response = client.simulate_get(f'/medical_books/{med_book_id}/symptoms')

        # Assert
        assert response.status_code == 200
        assert response.json == returned_med_book.dict()
        assert medical_book_service.method_calls == [
            call.get_med_book_with_symptoms(str(med_book_id))
        ]


class TestOnGetByIdWithReviews:
    def test__on_get_by_id_with_reviews(self, medical_book_service, client):
        # Setup
        returned_med_book = dtos.MedicalBookWithItemReviews(**MEDICAL_BOOK_1.__dict__)
        med_book_id = returned_med_book.id
        # Тестовый вывод `get_med_book_with_reviews` может отличаться от реального вывода
        medical_book_service.get_med_book_with_reviews.return_value = returned_med_book

        # Call
        response = client.simulate_get(f'/medical_books/{med_book_id}/reviews')

        # Assert
        assert response.status_code == 200
        assert response.json == returned_med_book.dict()
        assert medical_book_service.method_calls == [
            call.get_med_book_with_reviews(str(med_book_id))
        ]


class TestOnGetByIdWithSymptomsAndReviews:
    def test__on_get_by_id_with_symptoms_and_reviews(self, medical_book_service, client):
        # Setup
        med_book_id = MEDICAL_BOOK_1.id
        # Тестовый вывод `get_med_book_with_symptoms_and_reviews` может отличаться от
        # реального вывода
        medical_book_service.get_med_book_with_symptoms_and_reviews.return_value = (
            MEDICAL_BOOK_1
        )

        # Call
        response = client.simulate_get(f'/medical_books/{med_book_id}/symptoms/reviews')

        # Assert
        assert response.status_code == 200
        assert response.json == asdict(MEDICAL_BOOK_1)
        assert medical_book_service.method_calls == [
            call.get_med_book_with_symptoms_and_reviews(str(med_book_id))
        ]

    def test__on_get_by_id_with_reviews_and_symptoms(self, medical_book_service, client):
        # Setup
        med_book_id = MEDICAL_BOOK_1.id
        # Тестовый вывод `get_med_book_with_symptoms_and_reviews` может отличаться от
        # реального вывода
        medical_book_service.get_med_book_with_symptoms_and_reviews.return_value = (
            MEDICAL_BOOK_1
        )

        # Call
        response = client.simulate_get(f'/medical_books/{med_book_id}/reviews/symptoms')

        # Assert
        assert response.status_code == 200
        assert response.json == asdict(MEDICAL_BOOK_1)
        assert medical_book_service.method_calls == [
            call.get_med_book_with_symptoms_and_reviews(str(med_book_id))
        ]


class TestOnPostNew:
    def test__on_post_new(self, medical_book_service, client):
        # Setup
        medical_book_service.add.return_value = MEDICAL_BOOK_1

        # Call
        response = client.simulate_post('/medical_books/new', json=asdict(MEDICAL_BOOK_1))

        # Assert
        assert response.status_code == 201
        assert response.json == asdict(MEDICAL_BOOK_1)
        assert medical_book_service.method_calls == [
            call.add(dtos.NewMedicalBookInfo(**MEDICAL_BOOK_1.__dict__))
        ]


class TestOnPutById:
    def test__on_put_by_id(self, medical_book_service, client):
        # Setup
        medical_book_service.change.return_value = MEDICAL_BOOK_1
        med_book_id = MEDICAL_BOOK_1.id

        # Call
        response = client.simulate_put(f'/medical_books/{med_book_id}',
                                       json=asdict(MEDICAL_BOOK_1))

        # Assert
        assert response.status_code == 200
        assert response.json == asdict(MEDICAL_BOOK_1)
        assert medical_book_service.method_calls == [
            call.change(dtos.UpdatedMedicalBookInfo(**MEDICAL_BOOK_1.__dict__))
        ]


class TestOnDeleteById:
    def test__on_delete_by_id(self, medical_book_service, client):
        # Setup
        medical_book_service.delete.return_value = MEDICAL_BOOK_1
        med_book_id = MEDICAL_BOOK_1.id

        # Call
        response = client.simulate_delete(f'/medical_books/{med_book_id}')

        # Assert
        assert response.status_code == 200
        assert response.json == asdict(MEDICAL_BOOK_1)
        assert medical_book_service.method_calls == [call.delete(str(med_book_id))]

