from fastapi import (Request, Depends, status, Response, Form)
from typing import Optional
from src.models.managers.category import CategoryManager
from src.endpoints.setup import app, fastapi_users
from src.models.user import User
from src.models.category import Category, CategoryDB
from src.endpoints.setup import ENDPOINT


@app.get(f'{ENDPOINT}/categories', status_code=status.HTTP_200_OK)
async def get_categories(
    response: Response,
    user: User = Depends(fastapi_users.current_user()), 
    category_manager: CategoryManager = Depends(CategoryManager)
):
    categories = await  category_manager.get_categories()
    return categories


@app.get(ENDPOINT+'/category/{category_id}', status_code=status.HTTP_200_OK)
async def get_category(
    response: Response,
    category_id:str,
    user: User = Depends(fastapi_users.current_user()), 
    category_manager: CategoryManager = Depends(CategoryManager)
):
    category = await  category_manager.get_category(category_id)
    if not category:
        #category not found case
        response.status_code = status.HTTP_404_NOT_FOUND
        return {
            'status':status.HTTP_404_NOT_FOUND,
            'code':'category/not-found',
            'message': 'category not found'
        }
    return category

@app.post(f'{ENDPOINT}/category/create')
async def insert_category(
    response: Response,
    category_db:CategoryDB ,
    user: User = Depends(fastapi_users.current_user()), 
    category_manager: CategoryManager = Depends(CategoryManager)
):
    if(not user.is_superuser):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {
            'status':status.HTTP_401_UNAUTHORIZED,
            'code':'category/insert-unauthorized',
            'message': 'Unauthorized to insert category'
        }
    categories = await  category_manager.get_categories()
    for _category in categories:
        if _category.name == category_db.name:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {
                'status':status.HTTP_400_BAD_REQUEST,
                'code':'category/already-exists',
                'message': 'Category already exists'
            }
    category = Category(name=category_db.name, description=category_db.description)
    created_category = await category_manager.insert_category(category)
    return created_category


@app.put(ENDPOINT+'/category/{category_id}/update', status_code=status.HTTP_200_OK)
async def update_category(
    response: Response,
    category_id:str,
    category_db:CategoryDB,
    user: User = Depends(fastapi_users.current_user()), 
    category_manager: CategoryManager = Depends(CategoryManager)
):
    if(not user.is_superuser):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {
            'status':status.HTTP_401_UNAUTHORIZED,
            'code':'category/update-unauthorized',
            'message': 'Unauthorized to update category'
        }
    category = await  category_manager.get_category(category_id)
    if not category:
        #category not found case
        response.status_code = status.HTTP_404_NOT_FOUND
        return {
            'status':status.HTTP_404_NOT_FOUND,
            'code':'category/not-found',
            'message': 'category not found'
        }
    updated_category:Category = await category_manager.update_category(
        category_id=category_id,
        category_db=category_db
    )
    return updated_category

@app.delete(ENDPOINT+'/category/{category_id}/delete', status_code=status.HTTP_200_OK)
async def delete_category(
    response: Response,
    category_id:str,
    user: User = Depends(fastapi_users.current_user()), 
    category_manager: CategoryManager = Depends(CategoryManager),
):
    if(not user.is_superuser):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {
            'status':status.HTTP_401_UNAUTHORIZED,
            'code':'category/update-unauthorized',
            'message': 'Unauthorized to update category'
        }
    category:Category = await category_manager.get_category(category_id)
    if not category:
        #category not found case
        response.status_code = status.HTTP_404_NOT_FOUND
        return {
            'status':status.HTTP_404_NOT_FOUND,
            'code':'category/not-found',
            'message': 'category not found'
        }
    if await category_manager.delete_category(category_id):
        response.status_code = status.HTTP_200_OK
        return 
