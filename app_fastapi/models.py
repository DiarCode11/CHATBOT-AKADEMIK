from sqlalchemy import Column, Integer, String, Text, Enum, ForeignKey, DateTime
from sqlalchemy.orm import relationship, Session
from .database import Base
from datetime import datetime 
import uuid
import enum

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

class Users(Base):
    __tablename__ = 'tbl_users'

    id = Column(String(100), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(120), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    role = Column(Enum(UserRole), nullable=False, default=UserRole.user)
    password = Column(Text, nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now)

class PdfDatasets(Base):
    __tablename__ = 'tbl_pdf_dataset'

    id = Column(String(100), primary_key=True, default=lambda: str(uuid.uuid4()))
    filename = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    year = Column(String(100), nullable=False)
    created_by_id = Column(String(100), ForeignKey('tbl_users.id'), nullable=False)
    created_by = relationship('Users', backref='pdf_datasets', lazy='joined')
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False, default=datetime.now)
    deleted_at = Column(DateTime, nullable=True)

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

class UrlDatasets(Base):
    __tablename__ = 'tbl_url_dataset'

    id = Column(String(100), primary_key=True, default=lambda: str(uuid.uuid4()))
    url = Column(String(100), nullable=False)
    title = Column(String(100), nullable=False)
    year = Column(String(4), nullable=False)
    extracted_text = Column(Text, nullable=False)
    created_by_id = Column(String(100), ForeignKey('tbl_users.id'), nullable=False)
    created_by = relationship('Users', backref='url_datasets', lazy=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False, default=datetime.now)
    deleted_at = Column(DateTime, nullable=True)

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

class Chunks(Base):
    __tablename__ = "log_chunks"

    id = Column(String(100), primary_key=True, default=lambda: str(uuid.uuid4()))
    source = Column(String(100), nullable=False)
    year = Column(String(10), nullable=False)
    chunk = Column(Text, nullable=False)
    vector = Column(Text, nullable=False)
    created_by_id = Column(String(100), ForeignKey('tbl_users.id'), nullable=False)
    created_by = relationship('Users', backref='chunks', lazy=True)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False, default=datetime.now())
    deleted_at = Column(DateTime, nullable=True, default=None)

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
    
class EmbedderSetting(Base):
    __tablename__ = 'cfg_embedder_setting'

    id = Column(String(100), primary_key=True, default=lambda: str(uuid.uuid4()))
    chunk_size = Column(Integer, nullable=False)
    chunk_overlap = Column(Integer, nullable=False)
    embedder = Column(String(50), nullable=False)
    vector_db_name = Column(String(50), nullable=False)
    created_user_id = Column(String(50), ForeignKey('tbl_users.id'), nullable=False)
    user = relationship('Users', backref='model_setting', lazy=True)
    created_at = Column(DateTime, nullable=False)

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
    
class LLMSetting(Base):
    __tablename__ = 'cfg_llm_setting'

    id = Column(String(100), primary_key=True, default=lambda: str(uuid.uuid4()))
    llm = Column(String(50), nullable=False)
    candidates_size = Column(Integer, nullable=False)
    created_user_id = Column(String(50), ForeignKey('tbl_users.id'), nullable=False)
    user = relationship('Users', backref='llm_setting', lazy=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now())

    def __repr__(self):
        return f"Embedder Setting {self.embedder}"
    def to_dict(self):
        return {
            "id": self.id,
            "llm": self.llm,
            "candidate_size": self.candidates_size,
            "created_at": self.created_at
        }

class ChatProcess(Base):
    __tablename__ = 'log_chat_process'

    id = Column(String(100), primary_key=True, default=lambda: str(uuid.uuid4()))
    question = Column(Text(collation="utf8mb4_unicode_ci"), nullable=False)
    vector_from_query = Column(Text, nullable=False)
    expansion_result = Column(Text(collation="utf8mb4_unicode_ci"), nullable=False)
    retrieval_result = relationship('RetrievedChunks', backref='chat_process', lazy=True)
    corrective_prompt = Column(Text(collation="utf8mb4_unicode_ci"), nullable=False)
    corrective_result = Column(Text(collation="utf8mb4_unicode_ci"), nullable=False)
    generator_prompt = Column(Text(collation="utf8mb4_unicode_ci"), nullable=False)
    final_result = Column(Text(collation="utf8mb4_unicode_ci"), nullable=False)
    created_at = Column(DateTime, nullable=False, default=datetime.now())

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

class RetrievedChunks(Base):
    __tablename__ = 'log_retrieved_chunks'

    id = Column(String(100), primary_key=True, default=lambda: str(uuid.uuid4()))
    chat_process_id = Column(String(100), ForeignKey('log_chat_process.id'), nullable=False)
    chunk = Column(Text(collation="utf8mb4_unicode_ci"), nullable=False)
    vector = Column(Text, nullable=False)
    similiarity_score = Column(String(100), nullable=False)

    def to_dict(self):
        return {
            "chunk": self.chunk,
            "similiarity_score": self.similiarity_score,
            "vector": self.vector
        }


class ModifiedDataset(Base):
    __tablename__ = 'log_modified_dataset'

    id = Column(String(100), primary_key=True, default=lambda: str(uuid.uuid4()))
    file_id = Column(Text, nullable=False)
    file_type = Column(Enum(FileType), nullable=False)
    action = Column(Enum(Action), nullable=True)
    modified_by_id = Column(String(100), ForeignKey('tbl_users.id'), nullable=False)
    created_by = relationship('Users', backref='modified_datasets', lazy=True)
    created_at = Column(DateTime, nullable=False, default=datetime.now())

    def get_filename(self, db: Session):
        if self.file_type == FileType.url:
            url = db.get(UrlDatasets, self.file_id)
            return url.title if url else None
        elif self.file_type == FileType.pdf:
            pdf = db.get(PdfDatasets, self.file_id)
            return pdf.filename if pdf else None
        return None
    
    def to_dict(self):
        return {
            "id": self.file_id,
            "title": self.get_filename(),
            "action": self.action.name,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S")  
        }


