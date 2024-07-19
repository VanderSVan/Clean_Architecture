from unittest.mock import call

from med_sharing_system.adapters.med_sharing_api import schemas as api_schemas
from med_sharing_system.application import dtos

# ---------------------------------------------------------------------------------------
# SETUP
# ---------------------------------------------------------------------------------------
MEDICAL_BOOK_1 = dict(
    id=1,
    title_history='История моей болезни 1',
    history='Анамнез болезни 1',
    patient_id=1,
    diagnosis_id=1,
    symptoms=[dict(id=1, name='Симптом 1'),
              dict(id=2, name='Симптом 2')],
    item_reviews=[
        dict(id=1,
             item_id=1,
             is_helped=True,
             item_rating=9.5,
             item_count=5,
             usage_period=7776000),
        dict(id=2,
             item_id=2,
             is_helped=False,
             item_rating=3.5,
             item_count=1,
             usage_period=5184000)
    ]
)
MEDICAL_BOOK_2 = dict(
    id=2,
    title_history='История моей болезни 2',
    history='Анамнез болезни 2',
    patient_id=2,
    diagnosis_id=2,
    symptoms=[dict(id=3, name='Симптом 3'),
              dict(id=4, name='Симптом 4')],
    item_reviews=[
        dict(id=3,
             item_id=3,
             is_helped=True,
             item_rating=7.5,
             item_count=3,
             usage_period=7776000),
    ]
)
MEDICAL_BOOK_LIST: list[dict] = [MEDICAL_BOOK_1, MEDICAL_BOOK_2]
DEFAULT_FILTER_PARAMS = api_schemas.SearchMedicalBooks(exclude_med_book_fields=None)
DEFAULT_FILTER_PARAMS_WITH_SYMPTOMS_EXCLUSION = (
    api_schemas.SearchMedicalBooksWithSymptoms(exclude_med_book_fields=None,
                                               exclude_symptom_fields=None)
)
DEFAULT_FILTER_PARAMS_WITH_REVIEWS_EXCLUSION = (
    api_schemas.SearchMedicalBooksWithItemReviews(exclude_med_book_fields=None,
                                                  exclude_item_review_fields=None)
)
DEFAULT_FILTER_PARAMS_WITH_SYMPTOMS_AND_REVIEWS_EXCLUSION = (
    api_schemas.SearchMedicalBooksWithSymptomsAndItemReviews(
        exclude_med_book_fields=None,
        exclude_symptom_fields=None,
        exclude_item_review_fields=None
    )
)

FILTER_PARAMS = api_schemas.SearchMedicalBooks(
    patient_id=1,
    item_ids=[1, 2],
    is_helped=True,
    diagnosis_id=1,
    symptom_ids=[1, 2],
    match_all_symptoms=True,
    exclude_med_book_fields=['id', 'history'],
    sort_field='diagnosis_id',
    sort_direction='desc',
    limit=10,
    offset=0
)
FILTER_PARAMS_WITH_SYMPTOMS_EXCLUSION = api_schemas.SearchMedicalBooksWithSymptoms(
    patient_id=1,
    item_ids=[1, 2],
    is_helped=True,
    diagnosis_id=1,
    symptom_ids=[1, 2],
    match_all_symptoms=True,
    exclude_med_book_fields=['history'],
    exclude_symptom_fields=['id'],
    sort_field='diagnosis_id',
    sort_direction='desc',
    limit=10,
    offset=0
)
FILTER_PARAMS_WITH_REVIEWS_EXCLUSION = api_schemas.SearchMedicalBooksWithItemReviews(
    patient_id=1,
    item_ids=[1, 2],
    is_helped=True,
    diagnosis_id=1,
    symptom_ids=[1, 2],
    match_all_symptoms=True,
    exclude_med_book_fields=['id', 'history'],
    exclude_item_review_fields=['id', 'usage_period'],
    sort_field='diagnosis_id',
    sort_direction='desc',
    limit=10,
    offset=0
)
FILTER_PARAMS_WITH_SYMPTOMS_AND_REVIEWS_EXCLUSION = (
    api_schemas.SearchMedicalBooksWithSymptomsAndItemReviews(
        patient_id=1,
        item_ids=[1, 2],
        is_helped=True,
        diagnosis_id=1,
        symptom_ids=[1, 2],
        match_all_symptoms=True,
        exclude_med_book_fields=['id', 'history'],
        exclude_symptom_fields=['id'],
        exclude_item_review_fields=['id', 'usage_period'],
        sort_field='diagnosis_id',
        sort_direction='desc',
        limit=10,
        offset=0
    )
)


def generate_url(filter_params, path) -> str:
    url = f'{path}?'
    for key, value in filter_params.dict().items():
        if isinstance(value, list):
            for v in value:
                url += f'{key}={v}&'
        else:
            url += f'{key}={value}&'
    return url[:-1]  # remove the last '&'


# ---------------------------------------------------------------------------------------
# TESTS
# ---------------------------------------------------------------------------------------
class TestOnGet:
    def test__on_get(self, medical_book_service, client):
        # Setup
        returned_med_books = [
            dtos.MedicalBook(**med_book) for med_book in MEDICAL_BOOK_LIST
        ]
        test_url: str = generate_url(FILTER_PARAMS, '{path}')

        # Тестовый вывод `find_med_books` может отличаться от реального вывода
        medical_book_service.find_med_books.return_value = returned_med_books

        # Call
        response = client.simulate_get(test_url.format(path='/medical_books'))

        # Assert
        assert response.status_code == 200
        assert len(response.json) == len(MEDICAL_BOOK_LIST)
        for med_book in response.json:
            for key in FILTER_PARAMS.exclude_med_book_fields:
                assert key not in med_book.keys()
        assert medical_book_service.method_calls == [call.find_med_books(FILTER_PARAMS)]

    def test__on_get_without_filters(self, medical_book_service, client):
        # Setup
        returned_med_books = [
            dtos.MedicalBook(**med_book) for med_book in MEDICAL_BOOK_LIST
        ]

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
        returned_med_books = [
            dtos.MedicalBookWithSymptoms(**med_book) for med_book in MEDICAL_BOOK_LIST
        ]
        test_url: str = generate_url(FILTER_PARAMS_WITH_SYMPTOMS_EXCLUSION,
                                     '/medical_books/symptoms')

        # Тестовый вывод `find_med_books` может отличаться от реального вывода
        medical_book_service.find_med_books_with_symptoms.return_value = (
            returned_med_books
        )

        # Call
        response = client.simulate_get(test_url)

        # Assert
        assert response.status_code == 200
        assert len(response.json) == len(MEDICAL_BOOK_LIST)
        for med_book in response.json:
            for key in FILTER_PARAMS_WITH_SYMPTOMS_EXCLUSION.exclude_med_book_fields:
                assert key not in med_book.keys()

            for key in FILTER_PARAMS_WITH_SYMPTOMS_EXCLUSION.exclude_symptom_fields:
                assert all(key not in symptom.keys()
                           for symptom in med_book['symptoms'])

        assert medical_book_service.method_calls == [
            call.find_med_books_with_symptoms(FILTER_PARAMS_WITH_SYMPTOMS_EXCLUSION)
        ]

    def test__on_get_with_symptoms_without_filters(self, medical_book_service, client):
        # Setup
        returned_med_books = [
            dtos.MedicalBookWithSymptoms(**med_book) for med_book in MEDICAL_BOOK_LIST
        ]

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
            call.find_med_books_with_symptoms(
                DEFAULT_FILTER_PARAMS_WITH_SYMPTOMS_EXCLUSION
            )
        ]


class TestOnGetWithReviews:
    def test__on_get_with_reviews(self, medical_book_service, client):
        # Setup
        returned_med_books = [
            dtos.MedicalBookWithItemReviews(**med_book) for med_book in MEDICAL_BOOK_LIST
        ]
        test_url: str = generate_url(FILTER_PARAMS_WITH_REVIEWS_EXCLUSION,
                                     '/medical_books/reviews')

        # Тестовый вывод может отличаться от реального вывода
        medical_book_service.find_med_books_with_reviews.return_value = returned_med_books

        # Call
        response = client.simulate_get(test_url)

        # Assert
        assert response.status_code == 200
        assert len(response.json) == len(MEDICAL_BOOK_LIST)
        for med_book in response.json:
            for key in FILTER_PARAMS_WITH_REVIEWS_EXCLUSION.exclude_med_book_fields:
                assert key not in med_book.keys()

            for key in FILTER_PARAMS_WITH_REVIEWS_EXCLUSION.exclude_item_review_fields:
                assert all(key not in review.keys()
                           for review in med_book['item_reviews'])

        assert medical_book_service.method_calls == [
            call.find_med_books_with_reviews(FILTER_PARAMS_WITH_REVIEWS_EXCLUSION)
        ]

    def test__on_get_with_reviews_without_filters(self, medical_book_service, client):
        # Setup
        returned_med_books = [
            dtos.MedicalBookWithItemReviews(**med_book) for med_book in MEDICAL_BOOK_LIST
        ]

        # Тестовый вывод `find_med_books` может отличаться от реального вывода
        medical_book_service.find_med_books_with_reviews.return_value = returned_med_books

        # Call
        response = client.simulate_get('/medical_books/reviews')

        # Assert
        assert response.status_code == 200
        assert response.json == [med_book.dict() for med_book in returned_med_books]
        assert medical_book_service.method_calls == [
            call.find_med_books_with_reviews(
                DEFAULT_FILTER_PARAMS_WITH_REVIEWS_EXCLUSION)
        ]


class TestOnGetWithSymptomsAndReviews:
    def test__on_get_with_symptoms_and_reviews(self, medical_book_service, client):
        # Setup
        returned_med_books = [
            dtos.MedicalBookWithSymptomsAndItemReviews(**med_book)
            for med_book in MEDICAL_BOOK_LIST
        ]
        test_url: str = generate_url(
            FILTER_PARAMS_WITH_SYMPTOMS_AND_REVIEWS_EXCLUSION,
            '/medical_books/symptoms/reviews'
        )
        # Тестовый вывод может отличаться от реального вывода
        medical_book_service.find_med_books_with_symptoms_and_reviews.return_value = (
            returned_med_books
        )

        # Call
        response = client.simulate_get(test_url)

        # Assert
        assert response.status_code == 200
        assert len(response.json) == len(MEDICAL_BOOK_LIST)
        for med_book in response.json:
            for key in (
                DEFAULT_FILTER_PARAMS_WITH_SYMPTOMS_AND_REVIEWS_EXCLUSION
                    .exclude_med_book_fields
            ):
                assert key not in med_book.keys()

            for key in (
                DEFAULT_FILTER_PARAMS_WITH_SYMPTOMS_AND_REVIEWS_EXCLUSION
                    .exclude_symptom_fields
            ):
                assert all(key not in symptom.keys()
                           for symptom in med_book['symptoms'])

            for key in (
                DEFAULT_FILTER_PARAMS_WITH_SYMPTOMS_AND_REVIEWS_EXCLUSION
                    .exclude_item_review_fields
            ):
                assert all(key not in review.keys()
                           for review in med_book['item_reviews'])

        assert medical_book_service.method_calls == [
            call.find_med_books_with_symptoms_and_reviews(
                FILTER_PARAMS_WITH_SYMPTOMS_AND_REVIEWS_EXCLUSION
            )
        ]

    def test__on_get_with_symptoms_and_reviews_without_filters(self, medical_book_service,
                                                               client):
        # Setup
        # Тестовый вывод может отличаться от реального вывода
        returned_med_books = [
            dtos.MedicalBookWithSymptomsAndItemReviews(**med_book)
            for med_book in MEDICAL_BOOK_LIST
        ]
        medical_book_service.find_med_books_with_symptoms_and_reviews.return_value = (
            returned_med_books
        )

        # Call
        response = client.simulate_get('/medical_books/symptoms/reviews')

        # Assert
        assert response.status_code == 200
        assert len(response.json) == len(MEDICAL_BOOK_LIST)
        assert response.json == [med_book for med_book in MEDICAL_BOOK_LIST]
        assert medical_book_service.method_calls == [
            call.find_med_books_with_symptoms_and_reviews(
                DEFAULT_FILTER_PARAMS_WITH_SYMPTOMS_AND_REVIEWS_EXCLUSION
            )
        ]

    def test__on_get_with_reviews_and_symptoms(self, medical_book_service, client):
        # Setup
        returned_med_books = [
            dtos.MedicalBookWithSymptomsAndItemReviews(**med_book)
            for med_book in MEDICAL_BOOK_LIST
        ]
        # Тестовый вывод может отличаться от реального вывода
        medical_book_service.find_med_books_with_symptoms_and_reviews.return_value = (
            returned_med_books
        )
        test_url: str = generate_url(
            FILTER_PARAMS_WITH_SYMPTOMS_AND_REVIEWS_EXCLUSION,
            '/medical_books/reviews/symptoms'
        )

        # Call
        response = client.simulate_get(test_url)

        # Assert
        assert response.status_code == 200
        assert len(response.json) == len(MEDICAL_BOOK_LIST)
        for med_book in response.json:
            for key in (
                DEFAULT_FILTER_PARAMS_WITH_SYMPTOMS_AND_REVIEWS_EXCLUSION
                    .exclude_med_book_fields
            ):
                assert key not in med_book.keys()

            for key in (
                DEFAULT_FILTER_PARAMS_WITH_SYMPTOMS_AND_REVIEWS_EXCLUSION
                    .exclude_symptom_fields
            ):
                assert all(key not in symptom.keys()
                           for symptom in med_book['symptoms'])

            for key in (
                DEFAULT_FILTER_PARAMS_WITH_SYMPTOMS_AND_REVIEWS_EXCLUSION
                    .exclude_item_review_fields
            ):
                assert all(key not in review.keys()
                           for review in med_book['item_reviews'])

        assert medical_book_service.method_calls == [
            call.find_med_books_with_symptoms_and_reviews(
                FILTER_PARAMS_WITH_SYMPTOMS_AND_REVIEWS_EXCLUSION
            )
        ]

    def test__on_get_with_reviews_and_symptoms_without_filters(self, medical_book_service,
                                                               client):
        # Setup
        returned_med_books = [
            dtos.MedicalBookWithSymptomsAndItemReviews(**med_book)
            for med_book in MEDICAL_BOOK_LIST
        ]
        # Тестовый вывод может отличаться от реального вывода
        medical_book_service.find_med_books_with_symptoms_and_reviews.return_value = (
            returned_med_books
        )

        # Call
        response = client.simulate_get('/medical_books/reviews/symptoms')

        # Assert
        assert response.status_code == 200
        assert response.json == [med_book for med_book in MEDICAL_BOOK_LIST]
        assert medical_book_service.method_calls == [
            call.find_med_books_with_symptoms_and_reviews(
                DEFAULT_FILTER_PARAMS_WITH_SYMPTOMS_AND_REVIEWS_EXCLUSION
            )
        ]


class TestOnGetById:
    def test__on_get_by_id(self, medical_book_service, client):
        # Setup
        returned_med_book = dtos.MedicalBook(**MEDICAL_BOOK_1)
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
        returned_med_book = dtos.MedicalBookWithSymptoms(**MEDICAL_BOOK_1)
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
        returned_med_book = dtos.MedicalBookWithItemReviews(**MEDICAL_BOOK_1)
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
        med_book_id = MEDICAL_BOOK_1['id']
        returned_med_book = dtos.MedicalBookWithSymptomsAndItemReviews(
            **MEDICAL_BOOK_1
        )
        # Тестовый вывод `get_med_book_with_symptoms_and_reviews` может отличаться от
        # реального вывода
        medical_book_service.get_med_book_with_symptoms_and_reviews.return_value = (
            returned_med_book
        )

        # Call
        response = client.simulate_get(f'/medical_books/{med_book_id}/symptoms/reviews')

        # Assert
        assert response.status_code == 200
        assert response.json == MEDICAL_BOOK_1
        assert medical_book_service.method_calls == [
            call.get_med_book_with_symptoms_and_reviews(str(med_book_id))
        ]

    def test__on_get_by_id_with_reviews_and_symptoms(self, medical_book_service, client):
        # Setup
        med_book_id = MEDICAL_BOOK_1['id']
        returned_med_book = dtos.MedicalBookWithSymptomsAndItemReviews(
            **MEDICAL_BOOK_1
        )
        # Тестовый вывод `get_med_book_with_symptoms_and_reviews` может отличаться от
        # реального вывода
        medical_book_service.get_med_book_with_symptoms_and_reviews.return_value = (
            returned_med_book
        )

        # Call
        response = client.simulate_get(f'/medical_books/{med_book_id}/reviews/symptoms')

        # Assert
        assert response.status_code == 200
        assert response.json == MEDICAL_BOOK_1
        assert medical_book_service.method_calls == [
            call.get_med_book_with_symptoms_and_reviews(str(med_book_id))
        ]


class TestOnPostNew:
    def test__on_post_new(self, medical_book_service, client):
        # Setup
        medical_book_service.add.return_value = (
            dtos.MedicalBookWithSymptomsAndItemReviews(**MEDICAL_BOOK_1)
        )
        data_to_post = dtos.NewMedicalBookInfo(**MEDICAL_BOOK_1)

        # Call
        response = client.simulate_post('/medical_books/new',
                                        json=data_to_post.dict())

        # Assert
        assert response.status_code == 201
        assert response.json == MEDICAL_BOOK_1
        assert medical_book_service.method_calls == [
            call.add(dtos.NewMedicalBookInfo(**data_to_post.dict()))
        ]


class TestOnPutById:
    def test__on_put_by_id(self, medical_book_service, client):
        # Setup
        medical_book_service.change.return_value = (
            dtos.MedicalBookWithSymptomsAndItemReviews(**MEDICAL_BOOK_1)
        )

        med_book_id = MEDICAL_BOOK_1['id']

        # Call
        response = client.simulate_put(f'/medical_books/{med_book_id}',
                                       json=MEDICAL_BOOK_1)

        # Assert
        assert response.status_code == 200
        assert response.json == MEDICAL_BOOK_1
        assert medical_book_service.method_calls == [
            call.change(dtos.UpdatedMedicalBookInfo(**MEDICAL_BOOK_1))
        ]


class TestOnPatchById:
    def test__on_patch_by_id(self, medical_book_service, client):
        # Setup
        medical_book_service.change.return_value = (
            dtos.MedicalBookWithSymptomsAndItemReviews(**MEDICAL_BOOK_1)
        )

        med_book_id = MEDICAL_BOOK_1['id']

        # Call
        response = client.simulate_patch(f'/medical_books/{med_book_id}',
                                         json=MEDICAL_BOOK_1)

        # Assert
        assert response.status_code == 200
        assert response.json == MEDICAL_BOOK_1
        assert medical_book_service.method_calls == [
            call.change(dtos.MedicalBookInfoToUpdate(**MEDICAL_BOOK_1))
        ]


class TestOnDeleteById:
    def test__on_delete_by_id(self, medical_book_service, client):
        # Setup
        medical_book_info: dict = MEDICAL_BOOK_1
        del medical_book_info["symptoms"]
        del medical_book_info["item_reviews"]
        medical_book_service.delete.return_value = dtos.MedicalBook(**medical_book_info)

        med_book_id = MEDICAL_BOOK_1['id']

        # Call
        response = client.simulate_delete(f'/medical_books/{med_book_id}')

        # Assert
        assert response.status_code == 200
        assert response.json == medical_book_info
        assert medical_book_service.method_calls == [call.delete(str(med_book_id))]
