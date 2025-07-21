from datetime import datetime
from app import db

class Message(db.Model):
    __tablename__ = 'messages'
    
    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    recipient_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    property_id = db.Column(db.Integer, db.ForeignKey('properties.id'))
    message_text = db.Column(db.Text, nullable=False)
    attachment_url = db.Column(db.String(500))
    is_read = db.Column(db.Boolean, default=False)
    sent_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def mark_as_read(self):
        self.is_read = True
        db.session.commit()
    
    def __repr__(self):
        return f'<Message from {self.sender.username} to {self.recipient.username}>'