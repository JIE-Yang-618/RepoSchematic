from .repository import UserRepository

class UserService:
    def __init__(self):
        self.repo = UserRepository()

    def run(self):
        return self.repo.list_users()
