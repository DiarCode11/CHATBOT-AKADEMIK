from datetime import datetime
import uuid
import enum
from . import db

class UserRole(enum.Enum):
    admin = "admin"
    user = "user"

class Reaction(enum.Enum):
    null = "null"
    like = "like"
    dislike = "dislike"


class Users(db.Model):
    __tablename__ = 'tbl_users'

    id = db.Column(db.String(100), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.user)
    password = db.Column(db.Text, nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

class PdfDatasets(db.Model):
    __tablename__ = 'tbl_pdf_dataset'

    id = db.Column(db.String(100), primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = db.Column(db.Text, nullable=False)
    description = db.Column(db.Text, nullable=False)
    year = db.Column(db.String(100), nullable=False)
    created_by_id = db.Column(db.String(100), db.ForeignKey('tbl_users.id'), nullable=False)
    created_by = db.relationship('Users', backref='pdf_datasets', lazy=True)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now())

    def __repr__(self):
        return f"PdfDataset('{self.filename}', '{self.year}')"
    
    def to_dict(self):
        return {
            'id': self.id,
            'filename': self.filename,
            'description': self.description,
            'year': self.year,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }

class UrlDatasets(db.Model):
    __tablename__ = 'tbl_url_dataset'

    id = db.Column(db.String(100), primary_key=True, default=lambda: str(uuid.uuid4()))
    url = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    year = db.Column(db.String(4), nullable=False)
    extracted_text = db.Column(db.Text, nullable=False)
    created_by_id = db.Column(db.String(100), db.ForeignKey('tbl_users.id'), nullable=False)
    created_by = db.relationship('Users', backref='url_datasets', lazy=True)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now())

    def __repr__(self):
        return f"UrlDataset('{self.title}', '{self.url}')"
    
    def to_dict(self):
        return {
            'id': self.id,
            'url': self.url,
            'title': self.title,
            'year': self.year,
            'extracted_text': self.extracted_text,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S')
        }

class Chunks(db.Model):
    __tablename__ = "log_chunks"

    id = db.Column(db.String(100), primary_key=True, default=lambda: str(uuid.uuid4()))
    chunk = db.Column(db.String(100), nullable=False)
    title = db.Column(db.String(100), nullable=False)
    vector = db.Column(db.Text, nullable=False)
    content_type = db.Column(db.String(50), nullable=False)  # 'pdf' or 'url'
    content_id = db.Column(db.String(100), nullable=False)  # ID of related PdfDataset or UrlDataset
    created_by_id = db.Column(db.String(100), db.ForeignKey('tbl_users.id'), nullable=False)
    created_by = db.relationship('Users', backref='chunks', lazy=True)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now())

    @property
    def related_content(self):
        if self.content_type == 'pdf':
            return PdfDatasets.query.get(self.content_id)
        elif self.content_type == 'url':
            return UrlDatasets.query.get(self.content_id)
        return None

    def __repr__(self):
        return f"Chunk('{self.chunk}', '{self.title}', '{self.content_type}')"

class ModelSetting(db.Model):
    __tablename__ = 'cfg_model_setting'

    id = db.Column(db.String(100), primary_key=True, default=lambda: str(uuid.uuid4()))
    chunk_size = db.Column(db.Integer, nullable=False)
    chunk_overlap = db.Column(db.Integer, nullable=False)
    embedder = db.Column(db.String(50), nullable=False)
    llm_model = db.Column(db.String(50), nullable=False)
    user_id = db.Column(db.String(50), db.ForeignKey('tbl_users.id'), nullable=False)
    user = db.relationship('Users', backref='model_setting', lazy=True)

    def __repr__(self):
        return f"Model Setting {self.chunk_size} {self.chunk_overlap}"

class Conversation(db.Model):
    __tablename__ = 'log_conversation'

    id = db.Column(db.String(100), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(50), db.ForeignKey('tbl_users.id'), nullable=False)
    user = db.relationship('Users', backref='conversation', lazy=True)
    question = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    response_reaction = db.Column(db.Enum(Reaction), nullable=False, default=Reaction.null)


    

