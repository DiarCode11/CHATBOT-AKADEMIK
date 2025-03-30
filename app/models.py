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
    email = db.Column(db.String(120), nullable=False)
    role = db.Column(db.Enum(UserRole), nullable=False, default=UserRole.user)
    password = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False)
    updated_at = db.Column(db.DateTime, nullable=False)
    deleted_at = db.Column(db.DateTime, nullable=True, default=None)

    def to_dict(self):
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role.value,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None,
            'deleted_at': self.deleted_at.strftime('%Y-%m-%d %H:%M:%S') if self.deleted_at else None
        }


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

class ChatProcess(db.Model):
    __tablename__ = 'log_chat_process'

    id = db.Column(db.String(100), primary_key=True, default=lambda: str(uuid.uuid4()))
    question = db.Column(db.Text(collation="utf8mb4_unicode_ci"), nullable=False)
    vector_from_query = db.Column(db.Text, nullable=False)
    expansion_result = db.Column(db.Text(collation="utf8mb4_unicode_ci"), nullable=True, default=None)
    retrieval_result = db.relationship('RetrievedChunks', backref='chat_process', lazy=True)
    corrective_prompt = db.Column(db.Text(collation="utf8mb4_unicode_ci"), nullable=True, default=None)
    corrective_result = db.Column(db.Text(collation="utf8mb4_unicode_ci"), nullable=True, default=None)
    generator_prompt = db.Column(db.Text(collation="utf8mb4_unicode_ci"), nullable=False)
    final_result = db.Column(db.Text(collation="utf8mb4_unicode_ci"), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())

    def get_retrieval_result(self):
        sorted_chunks = sorted(
            self.retrieval_result, 
            key=lambda x: float(x.similiarity_score) if x.similiarity_score.replace('.', '', 1).isdigit() else float('inf')
        )
        return [result.to_dict() for result in sorted_chunks]
    
    def to_dict(self):
        return {
            "id": self.id,
            "question": self.question,
            "vector_from_query": self.vector_from_query,
            "expansion_result": self.expansion_result,
            "retrieval_result": self.get_retrieval_result(),
            "corrective_prompt": self.corrective_prompt,
            "corrective_result": self.corrective_result,
            "generator_prompt": self.generator_prompt,
            "final_result": self.final_result,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }

class RetrievedChunks(db.Model):
    __tablename__ = 'log_retrieved_chunks'

    id = db.Column(db.String(100), primary_key=True, default=lambda: str(uuid.uuid4()))
    chat_process_id = db.Column(db.String(100), db.ForeignKey('log_chat_process.id'), nullable=False)
    chunk = db.Column(db.Text(collation="utf8mb4_unicode_ci"), nullable=False)
    vector = db.Column(db.Text, nullable=False)
    similiarity_score = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return {
            "chunk": self.chunk,
            "similiarity_score": self.similiarity_score,
            "vector": self.vector
        }


class ModifiedDataset(db.Model):
    __tablename__ = 'log_modified_dataset'

    id = db.Column(db.String(100), primary_key=True, default=lambda: str(uuid.uuid4()))
    file_id = db.Column(db.Text, nullable=False)
    file_type = db.Column(db.Enum(FileType), nullable=False)
    action = db.Column(db.Enum(Action), nullable=True)
    modified_by_id = db.Column(db.String(100), db.ForeignKey('tbl_users.id'), nullable=False)
    created_by = db.relationship('Users', backref='modified_datasets', lazy=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now())

    def get_filename(self):
        if self.file_type == FileType.url:
            url = db.session.get(UrlDatasets, self.file_id)
            return url.title if url else None
        elif self.file_type == FileType.pdf:
            pdf = db.session.get(PdfDatasets, self.file_id)
            return pdf.filename if pdf else None
        return None
    
    def to_dict(self):
        return {
            "id": self.file_id,
            "title": self.get_filename(),
            "action": self.action.name,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S")  
        }



    

