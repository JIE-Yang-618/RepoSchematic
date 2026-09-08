from .service import UserService

def main():
    service = UserService()
    return service.run()
