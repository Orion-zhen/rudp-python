from copy import deepcopy


STATE2CODE = {"NOT_SENT": 0, "SENT_NOT_ACKED": 1, "ACKED": 2}
CODE2STATE = {0: "NOT_SENT", 1: "SENT_NOT_ACKED", 2: "ACKED"}


class Data(object):
    """描述发送的数据的类"""

    def __init__(self, message: str, seq: int, state="NOT_SENT") -> None:
        """描述发送的数据类型的对象

        Args:
            message (str): 需要发送的消息
            seq (int): 序列号
            state (str, optional): 该消息的状态. Defaults to "NOT_SENT".
        """
        # 为了避免奇怪的GC bug
        self.__message = deepcopy(message)
        self.__seq = seq
        self.__state = STATE2CODE[state]

    @property
    def message(self):
        return deepcopy(self.__message)

    @property
    def seq(self):
        return self.__seq

    @property
    def state(self):
        return CODE2STATE[self.__state]

    def __check_state(self, state_code: int) -> bool:
        """检查状态变更是否合法

        Args:
            state (int): 目标状态码

        Returns:
            bool: 是否合法的判断
        """
        if self.__state == 2 and state_code == 1:
            # 不能把已确认的变为为确认
            return False
        if self.__state == 0 and state_code == 2:
            # 不能把未发送的变为已确认的
            return False
        return True

    def switch(self, state: str) -> None:
        """修改数据包的状态

        Args:
            state (str): 目标状态名
        """
        state_code = STATE2CODE[state]
        if self.__check_state(state_code):
            self.__state = state_code
        else:
            raise Exception("Illegal state switch!")
