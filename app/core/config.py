from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "scubaaaa-api"

    APP_PORT: int = 8000

    # Camera stream server (mjpg-streamer MJPEG)
    CAMERA_HOST: str = "192.168.2.1"
    CAMERA_STREAM_PORT: int = 8888

    # Arduino serial
    SERIAL_DEVICE: str = "/dev/ttyUSB0"
    SERIAL_BAUD: int = 9600

    @property
    def camera_stream_url(self) -> str:
        """MJPEG stream URL for the camera."""
        return f"http://{self.CAMERA_HOST}:{self.CAMERA_STREAM_PORT}/?action=stream"

    class Config:
        env_file = ".env"


settings = Settings()
