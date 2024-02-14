from random import randint

sql_str: str = f"INSERT INTO symptom_combinations (symptom_id, patient_medical_history_id)\nVALUES\n\t"

d = {}
patient_medical_history_id = 1
while patient_medical_history_id <= 100:
    for k in range(1, randint(3, 8)):

        symptom_id = randint(1, 100)

        if not d.get((symptom_id, patient_medical_history_id)):
            d[(symptom_id, patient_medical_history_id)] = f"({symptom_id}, {patient_medical_history_id})"
    patient_medical_history_id += 1


sql_str += ',\n\t'.join(d.values())


if __name__ == '__main__':
    from pprint import pp

    print(sql_str)
    # pp(d)
    # print(len(d))