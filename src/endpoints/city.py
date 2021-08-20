from fastapi import (Request, Depends, status, Response, Form)
from typing import Optional, List
from src.models.managers.city import CityManager
from src.endpoints.setup import app, fastapi_users
from src.models.user import User
from src.models.city import City, CityCreate, CityDB, CityUpdate, CreateCitySerializer, UpdateCitySerializer
from src.endpoints.setup import ENDPOINT


@app.get(f'{ENDPOINT}/cities', status_code=status.HTTP_200_OK)
async def get_cities(
    response: Response,
    user: User = Depends(fastapi_users.current_user()), 
    city_manager: CityManager = Depends(CityManager)
):
    return  await  city_manager.get_cities()


@app.get(ENDPOINT+'/city/{city_id}', status_code=status.HTTP_200_OK)
async def get_city(
    response: Response,
    city_id:str,
    user: User = Depends(fastapi_users.current_user()), 
    city_manager: CityManager = Depends(CityManager)
):
    city = await  city_manager.get_city(city_id)
    if not city:
        #city not found case
        response.status_code = status.HTTP_404_NOT_FOUND
        return {
            'status':status.HTTP_404_NOT_FOUND,
            'code':'city/not-found',
            'message': 'city not found'
        }
    return city

@app.post(f'{ENDPOINT}/city/create')
async def insert_city(
    response: Response,
    create_city_serializer:CreateCitySerializer ,
    user: User = Depends(fastapi_users.current_user()), 
    city_manager: CityManager = Depends(CityManager)
):
    if(not user.is_superuser):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {
            'status':status.HTTP_401_UNAUTHORIZED,
            'code':'city/insert-unauthorized',
            'message': 'Unauthorized to insert city'
        }
    cities:List[City] = await  city_manager.get_cities()
    for city in cities:
        if city.name == create_city_serializer.name:
            response.status_code = status.HTTP_400_BAD_REQUEST
            return {
                'status':status.HTTP_400_BAD_REQUEST,
                'code':'city/already-exists',
                'message': 'city already exists'
            }
    city_create:CityCreate = CityCreate(name=create_city_serializer.name, country=create_city_serializer.country)
    return await city_manager.insert_city(city_create=city_create)


@app.put(ENDPOINT+'/city/{city_id}/update', status_code=status.HTTP_200_OK)
async def update_city(
    response: Response,
    city_id:str,
    update_city_serializer:UpdateCitySerializer,
    user: User = Depends(fastapi_users.current_user()), 
    city_manager: CityManager = Depends(CityManager)
):
    if(not user.is_superuser):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {
            'status':status.HTTP_401_UNAUTHORIZED,
            'code':'city/update-unauthorized',
            'message': 'Unauthorized to update city'
        }
    city:City = await  city_manager.get_city(city_id=city_id)
    if not city:
        #city not found case
        response.status_code = status.HTTP_404_NOT_FOUND
        return {
            'status':status.HTTP_404_NOT_FOUND,
            'code':'city/not-found',
            'message': 'city not found'
        }
    
    return await city_manager.update_city(
        city_id=city_id, 
        city_update=CityUpdate(
            name=update_city_serializer.name,
            country=update_city_serializer.country))

@app.delete(ENDPOINT+'/city/{city_id}/delete', status_code=status.HTTP_200_OK)
async def delete_city(
    response: Response,
    city_id:str,
    user: User = Depends(fastapi_users.current_user()), 
    city_manager: CityManager = Depends(CityManager)
):
    if(not user.is_superuser):
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {
            'status':status.HTTP_401_UNAUTHORIZED,
            'code':'city/update-unauthorized',
            'message': 'Unauthorized to update city'
        }
    city:City = await city_manager.get_city(city_id=city_id)
    if not city:
        #city not found case
        response.status_code = status.HTTP_404_NOT_FOUND
        return {
            'status':status.HTTP_404_NOT_FOUND,
            'code':'city/not-found',
            'message': 'city not found'
        }
    return await city_manager.delete_city(city_id=city_id)
