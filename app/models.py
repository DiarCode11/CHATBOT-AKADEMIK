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

class FileType(enum.Enum):
    url = "url"
    pdf = "pdf"

class Action(enum.Enum):
    add = "add"
    delete = "delete"
    update = "update"   

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
    has_generated_to_vector = db.Column(db.Boolean, nullable=False, default=False)
    created_by_id = db.Column(db.String(100), db.ForeignKey('tbl_users.id'), nullable=False)
    created_by = db.relationship('Users', backref='pdf_datasets', lazy=True)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    deleted_at = db.Column(db.DateTime, nullable=True)

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
    has_generated_to_vector = db.Column(db.Boolean, nullable=False, default=False)
    extracted_text = db.Column(db.Text, nullable=False)
    created_by_id = db.Column(db.String(100), db.ForeignKey('tbl_users.id'), nullable=False)
    created_by = db.relationship('Users', backref='url_datasets', lazy=True)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    deleted_at = db.Column(db.DateTime, nullable=True)

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
    source = db.Column(db.String(100), nullable=False)
    year = db.Column(db.String(10), nullable=False)
    chunk = db.Column(db.Text, nullable=False)
    vector = db.Column(db.Text, nullable=False)
    created_by_id = db.Column(db.String(100), db.ForeignKey('tbl_users.id'), nullable=False)
    created_by = db.relationship('Users', backref='chunks', lazy=True)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.now())
    deleted_at = db.Column(db.DateTime, nullable=True, default=None)

    def __repr__(self):
        return f"Chunk('{self.chunk}', '{self.title}', '{self.content_type}')"
    
    def to_dict(self):
        return {
            'id': self.id,
            'title': self.title,
            'source': self.source,
            'chunk': self.chunk,
            'vector': self.vector,
            'created_by': self.created_by,
            'created_at': self.created_at,
            'updated_at': self.updated_at,
        }
    
class EmbedderSetting(db.Model):
    __tablename__ = 'cfg_embedder_setting'

    id = db.Column(db.String(100), primary_key=True, default=lambda: str(uuid.uuid4()))
    chunk_size = db.Column(db.Integer, nullable=False)
    chunk_overlap = db.Column(db.Integer, nullable=False)
    embedder = db.Column(db.String(50), nullable=False)
    vector_db_name = db.Column(db.String(50), nullable=False)
    created_user_id = db.Column(db.String(50), db.ForeignKey('tbl_users.id'), nullable=False)
    user = db.relationship('Users', backref='model_setting', lazy=True)
    created_at = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f"Model Setting {self.chunk_size} {self.chunk_overlap}"
    
    def to_dict(self):
        return {
            "id": self.id,
            "chunk_size": self.chunk_size,
            "chunk_overlap": self.chunk_overlap,
            "embedder": self.embedder,
            "vector_db_name": self.vector_db_name,
            "created_at": self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }
    
class LLMSetting(db.Model):
    __tablename__ = 'cfg_llm_setting'

    id = db.Column(db.String(100), primary_key=True, default=lambda: str(uuid.uuid4()))
    llm = db.Column(db.String(50), nullable=False)
    candidates_size = db.Column(db.Integer, nullable=False)
    created_user_id = db.Column(db.String(50), db.ForeignKey('tbl_users.id'), nullable=False)
    user = db.relationship('Users', backref='llm_setting', lazy=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())

    def __repr__(self):
        return f"Embedder Setting {self.embedder}"
    def to_dict(self):
        return {
            "id": self.id,
            "llm": self.llm,
            "candidate_size": self.candidates_size,
            "created_at": self.created_at
        }

class Conversation(db.Model):
    __tablename__ = 'log_conversation'

    id = db.Column(db.String(100), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(50), db.ForeignKey('tbl_users.id'), nullable=False)
    user = db.relationship('Users', backref='conversation', lazy=True)
    question = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    response_reaction = db.Column(db.Enum(Reaction), nullable=False, default=Reaction.null)





    

