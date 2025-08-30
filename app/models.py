import mongoengine as me
from datetime import datetime

# MongoEngine Document to store session data along with image details and AI response
class SessionData(me.Document):
    text_prompt = me.StringField(required=False)
    image_data = me.BinaryField(required=False)  # Store image data as binary
    image_name = me.StringField(required=False)  # Store original image name
    session_date = me.DateTimeField(default=datetime.utcnow)
    session_duration = me.FloatField(required=False)  # In seconds
    ai_response = me.StringField(required=False)  # Store AI model response

    def __str__(self):
        return f"Session on {self.session_date}, Duration: {self.session_duration} seconds"
