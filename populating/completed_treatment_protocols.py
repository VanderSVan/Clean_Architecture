from random import randint
from datetime import timedelta

SQL_STR: str = (
    f"INSERT INTO completed_treatment_protocols ("
    f"treatment_period, patient_medical_history_id, treatment_item_id, result_id"
    f")\nVALUES\n\t"
)


def get_random_timedelta():
    random_days = randint(0, 500)
    random_hours = randint(0, 24)
    random_minutes = randint(0, 60)

    random_timedelta = timedelta(
        days=random_days,
        hours=random_hours,
        minutes=random_minutes
    )

    return random_timedelta


data_to_insert = {}
patient_medical_history_id = 1

while patient_medical_history_id <= 100:
    for _ in range(1, randint(3, 8)):

        treatment_item_id = randint(1, 100)
        result_id = randint(1, 5)

        if not data_to_insert.get((treatment_item_id, result_id)):
            data_to_insert[(treatment_item_id, result_id)] = (
                f"({get_random_timedelta().seconds}, "
                f"{patient_medical_history_id}, "
                f"{treatment_item_id}, "
                f"{result_id})"
            )

    patient_medical_history_id += 1


SQL_STR += ',\n\t'.join(data_to_insert.values())


if __name__ == '__main__':
    from pprint import pp

    print(SQL_STR)
    # pp(d)
    # print(len(d))
