from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "Passport Photo Generator API"
    API_V1_STR: str = "/api/v1"
    PORT: int = 10000
    
    # Layout Config
    A4_WIDTH_PX: int = 2480  # 300 DPI
    A4_HEIGHT_PX: int = 3508 # 300 DPI
    LETTER_WIDTH_PX: int = 2550
    LETTER_HEIGHT_PX: int = 3300
    PHOTO_4X6_WIDTH_PX: int = 1200
    PHOTO_4X6_HEIGHT_PX: int = 1800
    PHOTO_5X7_WIDTH_PX: int = 1500
    PHOTO_5X7_HEIGHT_PX: int = 2100
    PASSPORT_WIDTH_MM: int = 35
    PASSPORT_HEIGHT_MM: int = 45
    DPI: int = 300
    
    # Pre-calculated pixels
    # 35mm = 35 / 25.4 * 300 = 413.38 ~ 413
    # 45mm = 45 / 25.4 * 300 = 531.49 ~ 531
    PHOTO_WIDTH_PX: int = int((PASSPORT_WIDTH_MM / 25.4) * DPI)
    PHOTO_HEIGHT_PX: int = int((PASSPORT_HEIGHT_MM / 25.4) * DPI)
    
    class Config:
        case_sensitive = True

settings = Settings()
