from random import randint

sql_str: str = f"INSERT INTO patient_medical_histories (history, patient_id, diagnosis_id)\nVALUES\n\t"

d = {}
patient_id = 1
history_id = len(d)
while len(d) < 100:
    for k in range(1, randint(2, 4)):

        diagnosis_id = randint(1, 100)

        if not d.get((patient_id, diagnosis_id)):
            history_id += 1
            d[(patient_id, diagnosis_id)] = f"('history_{history_id}', {patient_id}, {diagnosis_id})"
    patient_id += 1


sql_str += ',\n\t'.join(d.values())


if __name__ == '__main__':
    from pprint import pp

    print(sql_str)
    # pp(d)