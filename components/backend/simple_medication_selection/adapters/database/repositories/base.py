from sqlalchemy.orm import Session

from simple_medication_selection.adapters.database.transactions import TransactionContext


# yapf: disable
class BaseRepository:
    """
    Base class for Repositories, using SQLAlchemy
    """
    def __init__(self, context: TransactionContext):
        self.context = context

    @property
    def session(self) -> Session:
        return self.context.current_session

# yapf: enable
