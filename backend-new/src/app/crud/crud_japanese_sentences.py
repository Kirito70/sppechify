from fastcrud import FastCRUD

from ..models.japanese_sentence import JapaneseSentence
from ..schemas.japanese_sentence import (
    JapaneseSentenceCreateInternal,
    JapaneseSentenceUpdate,
    JapaneseSentenceUpdateInternal,
    JapaneseSentenceDelete,
    JapaneseSentenceRead
)

CRUDJapaneseSentence = FastCRUD[
    JapaneseSentence, 
    JapaneseSentenceCreateInternal, 
    JapaneseSentenceUpdate, 
    JapaneseSentenceUpdateInternal, 
    JapaneseSentenceDelete,
    JapaneseSentenceRead
]
crud_japanese_sentences = CRUDJapaneseSentence(JapaneseSentence)