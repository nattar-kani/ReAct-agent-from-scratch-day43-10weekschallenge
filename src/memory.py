class AgentMemory:
    def __init__(self,task:str):
        self.task = task
        self.history = []

    def add_event(self,event_type:str,content):
        self.history.append({
            "type":event_type,
            "content": content
        })

    def get_history(self)->list:
        return self.history.copy()

    def clear(self):
        self.history.clear()