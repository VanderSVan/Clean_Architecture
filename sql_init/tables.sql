CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    role VARCHAR(50) NOT NULL,
    email VARCHAR(50) UNIQUE NOT NULL,
    password VARCHAR(50) NOT NULL,
    nickname VARCHAR(50) NOT NULL
);

CREATE TABLE patients (
    id SERIAL PRIMARY KEY,
    age INT NOT NULL,
    skin_type VARCHAR(50),
    about TEXT,
    phone INT,
    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE symptoms (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);

CREATE TABLE diagnoses (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);

CREATE TABLE treatment_items (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    category VARCHAR(50) NOT NULL,
    type VARCHAR(50) NOT NULL,
    price NUMERIC(10, 2) NOT NULL
);

CREATE TABLE triggers (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);

CREATE TABLE result_types (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL
);

CREATE TABLE patient_medical_histories (
    id SERIAL PRIMARY KEY,
    history TEXT NOT NULL,
    diagnosis_id INTEGER REFERENCES diagnoses(id) ON DELETE SET NULL,
    patient_id INTEGER REFERENCES patients(id) ON DELETE CASCADE,
    CONSTRAINT ck_patient_medical_histories_unique UNIQUE (patient_id, diagnosis_id)
);

CREATE TABLE symptom_combinations (
    id SERIAL PRIMARY KEY,
    symptom_id INTEGER REFERENCES symptoms(id) ON DELETE CASCADE,
    patient_medical_history_id INTEGER REFERENCES patient_medical_histories(id) ON DELETE CASCADE,
    CONSTRAINT ck_symptom_combinations_unique UNIQUE (symptom_id, patient_medical_history_id)
);

CREATE TABLE trigger_combinations (
    id SERIAL PRIMARY KEY,
    trigger_id INTEGER REFERENCES triggers(id) ON DELETE CASCADE,
    patient_medical_history_id INTEGER REFERENCES patient_medical_histories(id) ON DELETE CASCADE,
    CONSTRAINT ck_trigger_combinations_unique UNIQUE (trigger_id, patient_medical_history_id)
);

CREATE TABLE completed_treatment_protocols (
    id SERIAL PRIMARY KEY,
    treatment_start TIMESTAMP,
    treatment_end TIMESTAMP,
    treatment_period INTEGER NOT NULL,
    patient_medical_history_id INTEGER REFERENCES patient_medical_histories(id) ON DELETE CASCADE,
    treatment_item_id INTEGER REFERENCES treatment_items(id) ON DELETE CASCADE,
    result_id INTEGER REFERENCES result_types(id) ON DELETE CASCADE,
    CONSTRAINT ck_completed_treatment_protocols_unique UNIQUE (treatment_item_id, result_id)
);
