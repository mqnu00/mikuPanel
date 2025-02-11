
class UserInfo:

    def __init__(self,
                 username=None,
                 password=None):

        self.username = username
        self.password = password

    def to_dict(self):

        return {
            "username": self.username,
            "password": self.password
        }


class User(object):

    def __init__(self, username, password):
        self.userinfo = UserInfo(username, password)

    def register(self):
        pass

    def login(self):
        pass

    def logout(self):
        pass


if __name__ == '__main__':
    # print(UserInfo.select_by_username('mqnu00'))
    userinfo = UserInfo()
