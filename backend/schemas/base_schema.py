from pydantic import BaseModel

class MessageResponse(BaseModel):    #TODO add to user router
    message: str