from src.models.managers.category import CategoryManager
from src.models.managers.user import UserManager

category_manager = CategoryManager()


async def get_category_manager() -> CategoryManager:
    return category_manager
