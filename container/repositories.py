# container/repositories.py
from repositories.user_repository import UserRepository

class RepositoryContainer:
    def __init__(self):
        self._repositories = {
            "user": UserRepository() 
        }

    def get(self, name: str):
        return self._repositories.get(name)