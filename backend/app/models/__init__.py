from datetime import datetime

from app.core.extensions import db


class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    full_name = db.Column(db.String(120), default='')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    analyses = db.relationship('Analysis', backref='user', lazy='dynamic', cascade='all, delete-orphan')

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'full_name': self.full_name,
            'created_at': self.created_at.isoformat(),
        }


class Analysis(db.Model):
    __tablename__ = 'analyses'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)
    filename = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(20), nullable=False)
    file_size = db.Column(db.Integer, default=0)
    word_count = db.Column(db.Integer, default=0)
    sentiment = db.Column(db.String(20), default='Neutral')
    document_type = db.Column(db.String(50), default='general')
    quality_grade = db.Column(db.String(2), default='N/A')
    quality_score = db.Column(db.Integer, default=0)
    entity_count = db.Column(db.Integer, default=0)
    topic_count = db.Column(db.Integer, default=0)
    result_data = db.Column(db.JSON, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'file_type': self.file_type,
            'file_size': self.file_size,
            'word_count': self.word_count,
            'sentiment': self.sentiment,
            'document_type': self.document_type,
            'quality_grade': self.quality_grade,
            'quality_score': self.quality_score,
            'entity_count': self.entity_count,
            'topic_count': self.topic_count,
            'created_at': self.created_at.isoformat(),
            'result_data': self.result_data,
        }

    def to_summary(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'file_type': self.file_type,
            'word_count': self.word_count,
            'sentiment': self.sentiment,
            'document_type': self.document_type,
            'quality_grade': self.quality_grade,
            'created_at': self.created_at.isoformat(),
        }
