from fastapi import FastAPI
from fastapi.responses import JSONResponse, HTMLResponse
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime

app = FastAPI()

engine = create_engine('postgresql://postgres:root@localhost:900/postgres')

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()

Base = declarative_base()

class Category(Base):
    __tablename__ = 'category'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))

class Author(Base):
    __tablename__ = 'author'
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    age = Column(Integer, nullable=True)  # Para filtro por idade

class Post(Base):
    __tablename__ = 'post'
    id = Column(Integer, primary_key=True)
    title = Column(String(255))
    subtitle = Column(String(255), nullable=True)
    created = Column(DateTime)
    authorid = Column(Integer, ForeignKey('author.id', ondelete='CASCADE'))
    category_id = Column(Integer, ForeignKey('category.id', ondelete='SET NULL'), nullable=True)
    author = relationship('Author')
    category = relationship('Category')

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

# CRUD Author
@app.post("/authors", tags=["Autores"])
def create_author(name: str, age: int = None):
    if not name:
        return JSONResponse(content={'error': 'Name is required'}, status_code=400)
    try:
        author = Author(name=name, age=age)
        session.add(author)
        session.commit()
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)
    return JSONResponse(content={'id': author.id, 'name': author.name, 'age': author.age}, status_code=201)

@app.put("/authors", tags=["Autores"])
def put_author(id: int, name: str, age: int = None):
    if not id:
        return JSONResponse(content={'error': 'ID is required'}, status_code=400)
    if not name:
        return JSONResponse(content={'error': 'Name is required'}, status_code=400)
    try:
        author = session.query(Author).filter_by(id=id).first()
        if not author:
            return JSONResponse(content={'error': 'Author not found'}, status_code=404)
        author.name = name
        if age is not None:
            author.age = age
        session.commit()
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)
    return JSONResponse(content={'id': author.id, 'name': author.name, 'age': author.age}, status_code=200)

@app.delete("/authors", tags=["Autores"])
def delete_author(id: int):
    if not id:
        return JSONResponse(content={'error': 'ID is required'}, status_code=400)
    try:
        author = session.query(Author).filter_by(id=id).first()
        if not author:
            return JSONResponse(content={'error': 'Author not found'}, status_code=404)
        session.delete(author)
        session.commit()
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)
    return JSONResponse(content={'message': 'Author deleted successfully'}, status_code=200)

@app.get('/authors/all', tags=["Autores"])
def get_all_authors():
    try:
        author_list = session.query(Author).all()
        if not author_list:
            return JSONResponse(content={'error': 'No authors found'}, status_code=404)
        authors = []
        for author in author_list:
            authors.append({'id': author.id, 'name': author.name, 'age': author.age})
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)
    return JSONResponse(content=authors, status_code=200)

@app.get('/authors/{author_id}/', tags=["Autores"])
def get_author(author_id: int):
    if not author_id:
        return JSONResponse(content={'error': 'ID is required'}, status_code=400)
    try:
        author = session.query(Author).filter_by(id=author_id).first()
        if not author:
            return JSONResponse(content={'error': 'Author not found'}, status_code=404)
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)
    return JSONResponse(content={'id': author.id, 'name': author.name, 'age': author.age}, status_code=200)

# CRUD Category
@app.post("/categories", tags=["Categorias"])
def create_category(name: str):
    if not name:
        return JSONResponse(content={'error': 'Name is required'}, status_code=400)
    try:
        category = Category(name=name)
        session.add(category)
        session.commit()
        return JSONResponse(content={'id': category.id, 'name': category.name}, status_code=201)
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)

@app.put("/categories", tags=["Categorias"])
def update_category(id: int, name: str):
    if not id or not name:
        return JSONResponse(content={'error': 'ID and Name are required'}, status_code=400)
    try:
        category = session.query(Category).filter_by(id=id).first()
        if not category:
            return JSONResponse(content={'error': 'Category not found'}, status_code=404)
        category.name = name
        session.commit()
        return JSONResponse(content={'id': category.id, 'name': category.name}, status_code=200)
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)

@app.get("/categories", tags=["Categorias"])
def list_categories():
    try:
        categories = session.query(Category).all()
        return JSONResponse(content=[{'id': c.id, 'name': c.name} for c in categories], status_code=200)
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)

@app.delete("/categories", tags=["Categorias"])
def delete_category(id: int):
    if not id:
        return JSONResponse(content={'error': 'ID is required'}, status_code=400)
    try:
        category = session.query(Category).filter_by(id=id).first()
        if not category:
            return JSONResponse(content={'error': 'Category not found'}, status_code=404)
        session.delete(category)
        session.commit()
        return JSONResponse(content={'message': 'Category deleted successfully'}, status_code=200)
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)

# CRUD Post
@app.post("/posts", tags=["Posts"])
def create_post(title: str, authorid: int, category_id: int = None, subtitle: str = None):
    if not title:
        return JSONResponse(content={'error': 'Title is required'}, status_code=400)
    if not authorid:
        return JSONResponse(content={'error': 'Author ID is required'}, status_code=400)
    try:
        author = session.query(Author).filter_by(id=authorid).first()
        if not author:
            return JSONResponse(content={'error': 'Author not found'}, status_code=404)
        if category_id:
            category = session.query(Category).filter_by(id=category_id).first()
            if not category:
                return JSONResponse(content={'error': 'Category not found'}, status_code=404)
        post = Post(title=title, subtitle=subtitle, created=datetime.now(), authorid=authorid, category_id=category_id)
        session.add(post)
        session.commit()
        return JSONResponse(content={
            'id': post.id, 'title': post.title, 'subtitle': post.subtitle, 'created': str(post.created),
            'authorid': post.authorid, 'category_id': post.category_id
        }, status_code=201)
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)

@app.put("/posts", tags=["Posts"])
def put_post(id: int, title: str, authorid: int, category_id: int = None, subtitle: str = None):
    try:
        if not id:
            return JSONResponse(content={'error': 'ID is required'}, status_code=400)
        if not title:
            return JSONResponse(content={'error': 'Title is required'}, status_code=400)
        if not authorid:
            return JSONResponse(content={'error': 'Author ID is required'}, status_code=400)
        post = session.query(Post).filter_by(id=id).first()
        if not post:
            return JSONResponse(content={'error': 'Post not found'}, status_code=404)
        author = session.query(Author).filter_by(id=authorid).first()
        if not author:
            return JSONResponse(content={'error': 'Author not found'}, status_code=404)
        if category_id:
            category = session.query(Category).filter_by(id=category_id).first()
            if not category:
                return JSONResponse(content={'error': 'Category not found'}, status_code=404)
            post.category_id = category_id
        post.title = title
        post.subtitle = subtitle
        post.authorid = authorid
        session.commit()
        return JSONResponse(content={
            'id': post.id, 'title': post.title, 'subtitle': post.subtitle, 'created': str(post.created),
            'authorid': post.authorid, 'category_id': post.category_id
        }, status_code=200)
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)

@app.delete("/posts", tags=["Posts"])
def delete_post(id: int):
    try:
        if not id:
            return JSONResponse(content={'error': 'ID is required'}, status_code=400)
        post = session.query(Post).filter_by(id=id).first()
        if not post:
            return JSONResponse(content={'error': 'Post not found'}, status_code=404)
        session.delete(post)
        session.commit()
        return JSONResponse(content={'message': 'Post deleted successfully'}, status_code=200)
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)

@app.get("/posts", tags=["Posts"])
def get_posts():
    try:
        posts = session.query(Post).all()
        post_list = []
        for post in posts:
            author = session.query(Author).filter_by(id=post.authorid).first()
            category = session.query(Category).filter_by(id=post.category_id).first() if post.category_id else None
            post_list.append({
                'id': post.id,
                'title': post.title,
                'subtitle': post.subtitle,
                'created': str(post.created),
                'authorid': author.id if author else None,
                'author_name': author.name if author else None,
                'author_age': author.age if author else None,
                'category_id': category.id if category else None,
                'category_name': category.name if category else None
            })
        return JSONResponse(content=post_list, status_code=200)
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)

@app.get("/posts/filter", tags=["Posts"])
def filter_posts(category_id: int = None, min_age: int = None, search: str = None):
    try:
        query = session.query(Post).join(Author)
        if category_id:
            query = query.filter(Post.category_id == category_id)
        if min_age:
            query = query.filter(Author.age >= min_age)
        if search:
            query = query.filter(
                (Post.title.ilike(f"%{search}%")) |
                (Post.subtitle.ilike(f"%{search}%"))
            )
        posts = query.all()
        result = []
        for post in posts:
            author = post.author
            category = post.category
            result.append({
                'id': post.id,
                'title': post.title,
                'subtitle': post.subtitle,
                'created': str(post.created),
                'authorid': author.id if author else None,
                'author_name': author.name if author else None,
                'author_age': author.age if author else None,
                'category_id': category.id if category else None,
                'category_name': category.name if category else None
            })
        return JSONResponse(content=result, status_code=200)
    except Exception as e:
        session.rollback()
        return JSONResponse(content={'error': str(e)}, status_code=500)

# Endpoint HTML com títulos de seção (não sobrescreve a documentação Swagger)
@app.get("/home", response_class=HTMLResponse, tags=["Visualização"])
def home():
    autores = session.query(Author).all()
    categorias = session.query(Category).all()
    posts = session.query(Post).all()

    html = """
    <html>
    <head>
        <title>Blog FastAPI</title>
        <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            h1 { color: #2c3e50; }
            ul { margin-bottom: 30px; }
        </style>
    </head>
    <body>
        <h1>Autores</h1>
        <ul>
    """
    for autor in autores:
        html += f"<li>{autor.name} (idade: {autor.age if autor.age is not None else 'N/A'})</li>"
    html += """
        </ul>
        <h1>Categorias</h1>
        <ul>
    """
    for categoria in categorias:
        html += f"<li>{categoria.name}</li>"
    html += """
        </ul>
        <h1>Posts</h1>
        <ul>
    """
    for post in posts:
        html += f"<li>{post.title} - {post.subtitle or ''}</li>"
    html += """
        </ul>
    </body>
    </html>
    """
    return HTMLResponse(content=html)