class BotClient:

    id: str
    task: str

    def __init__(self, id: str) -> None:
        self.id = id

    def set_task(self, task: str) -> None:
        self.task = task