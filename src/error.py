
class UserNotBindError(Exception):
    
    def __str__(self) -> str:
        return '该账号尚未绑定，请输入 !bind 用户名 绑定账号'

class UserNotFoundError(Exception):

    def __str__(self) -> str:
        return '未查询到该玩家'

class UserEnterError(Exception):

    def __str__(self) -> str:
        return '请输入正确参数'

class DrawImageError(Exception):

    def __init__(self, value: str) -> None:
        self.value = value

class ModsError(Exception):

    def __init__(self, value: str) -> None:
        self.value = value

class TokenError(Exception):

    def __init__(self, value: str) -> None:
        self.value = value