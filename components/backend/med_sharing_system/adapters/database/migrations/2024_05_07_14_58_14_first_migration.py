"""first_migration

Revision ID: f98f4162ed6d
Revises: 
Create Date: 2024-05-07 14:58:14.150784+00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f98f4162ed6d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('diagnoses',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_diagnoses')),
    sa.UniqueConstraint('name', name=op.f('uq_diagnoses_name'))
    )
    op.create_table('item_categories',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_item_categories')),
    sa.UniqueConstraint('name', name=op.f('uq_item_categories_name'))
    )
    op.create_table('item_types',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_item_types')),
    sa.UniqueConstraint('name', name=op.f('uq_item_types_name'))
    )
    op.create_table('patients',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('nickname', sa.String(), nullable=False),
    sa.Column('gender', sa.String(), nullable=False),
    sa.Column('age', sa.Integer(), nullable=False),
    sa.Column('skin_type', sa.String(), nullable=False),
    sa.Column('about', sa.Text(), nullable=True),
    sa.Column('phone', sa.String(length=15), nullable=True),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_patients')),
    sa.UniqueConstraint('nickname', name=op.f('uq_patients_nickname'))
    )
    op.create_table('symptoms',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_symptoms')),
    sa.UniqueConstraint('name', name=op.f('uq_symptoms_name'))
    )
    op.create_table('medical_books',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('title_history', sa.String(length=255), nullable=False),
    sa.Column('history', sa.Text(), nullable=True),
    sa.Column('patient_id', sa.Integer(), nullable=True),
    sa.Column('diagnosis_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['diagnosis_id'], ['diagnoses.id'], name=op.f('fk_medical_books_diagnosis_id_diagnoses'), onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['patient_id'], ['patients.id'], name=op.f('fk_medical_books_patient_id_patients'), onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_medical_books'))
    )
    op.create_table('treatment_items',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('title', sa.String(), nullable=False),
    sa.Column('price', sa.DECIMAL(precision=12, scale=2), nullable=True),
    sa.Column('description', sa.String(), nullable=True),
    sa.Column('type_id', sa.Integer(), nullable=False),
    sa.Column('category_id', sa.Integer(), nullable=False),
    sa.Column('avg_rating', sa.Float(), nullable=True),
    sa.ForeignKeyConstraint(['category_id'], ['item_categories.id'], name=op.f('fk_treatment_items_category_id_item_categories'), onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['type_id'], ['item_types.id'], name=op.f('fk_treatment_items_type_id_item_types'), onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_treatment_items'))
    )
    op.create_table('item_reviews',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('item_id', sa.Integer(), nullable=False),
    sa.Column('is_helped', sa.Boolean(), nullable=False),
    sa.Column('item_rating', sa.Float(), nullable=False),
    sa.Column('item_count', sa.Integer(), nullable=False),
    sa.Column('usage_period', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['item_id'], ['treatment_items.id'], name=op.f('fk_item_reviews_item_id_treatment_items'), onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_item_reviews'))
    )
    op.create_table('medical_books_symptoms',
    sa.Column('med_book_id', sa.Integer(), nullable=False),
    sa.Column('symptom_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['med_book_id'], ['medical_books.id'], name=op.f('fk_medical_books_symptoms_med_book_id_medical_books'), onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['symptom_id'], ['symptoms.id'], name=op.f('fk_medical_books_symptoms_symptom_id_symptoms'), onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('med_book_id', 'symptom_id', name=op.f('pk_medical_books_symptoms'))
    )
    op.create_table('medical_books_item_reviews',
    sa.Column('med_book_id', sa.Integer(), nullable=False),
    sa.Column('item_review_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['item_review_id'], ['item_reviews.id'], name=op.f('fk_medical_books_item_reviews_item_review_id_item_reviews'), onupdate='CASCADE', ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['med_book_id'], ['medical_books.id'], name=op.f('fk_medical_books_item_reviews_med_book_id_medical_books'), onupdate='CASCADE', ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('med_book_id', 'item_review_id', name=op.f('pk_medical_books_item_reviews'))
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('medical_books_item_reviews')
    op.drop_table('medical_books_symptoms')
    op.drop_table('item_reviews')
    op.drop_table('treatment_items')
    op.drop_table('medical_books')
    op.drop_table('symptoms')
    op.drop_table('patients')
    op.drop_table('item_types')
    op.drop_table('item_categories')
    op.drop_table('diagnoses')
    # ### end Alembic commands ###
