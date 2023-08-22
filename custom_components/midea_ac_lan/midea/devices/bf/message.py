from ...core.message import (
    MessageType,
    MessageRequest,
    MessageResponse,
    MessageBody
)


class MessageBFBase(MessageRequest):
    def __init__(self, device_protocol_version, message_type, body_type):
        super().__init__(
            device_protocol_version=device_protocol_version,
            device_type=0xBF,
            message_type=message_type,
            body_type=body_type
        )

    @property
    def _body(self):
        raise NotImplementedError


class MessageQuery(MessageBFBase):
    def __init__(self, device_protocol_version):
        super().__init__(
            device_protocol_version=device_protocol_version,
            message_type=MessageType.query)

    @property
    def _body(self):
        return bytearray([0x01])


class MessageBFBody(MessageBody):
    def __init__(self, body):
        super().__init__(body)
        self.time_remaining = (0 if body[22] == 0xFF else body[22]) * 3600 + \
                              (0 if body[23] == 0xFF else body[23]) * 60 + \
                              (0 if body[24] == 0xFF else body[24])
        cur_temperature = body[25] * 256 + body[26]
        if cur_temperature == 0:
            cur_temperature = body[27] * 256 + body[28]
        self.current_temperature = cur_temperature
        self.door = (body[32] & 0x02) > 0
        self.tank_ejected = (body[32] & 0x04) > 0
        self.water_state = (body[32] & 0x08) > 0
        self.water_change_reminder = (body[32] & 0x10) > 0


class MessageBFResponse(MessageResponse):
    def __init__(self, message):
        super().__init__(message)
        body = message[self.HEADER_LENGTH: -1]
        if self._message_type in [MessageType.set, MessageType.notify1, MessageType.query] and self._body_type == 0x01:
            self._body = MessageBFBody(body)
        self.set_attr()

