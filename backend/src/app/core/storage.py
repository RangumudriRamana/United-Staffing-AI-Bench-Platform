import os
import shutil
from abc import ABC, abstractmethod
from pathlib import Path

class StorageProvider(ABC):
    """Abstract baseline contract dictating standard file operations across any storage engine."""
    
    @abstractmethod
    async def upload(self, storage_key: str, content: bytes) -> str:
        """Persists raw binary arrays directly to the target environment storage location."""
        pass

    @abstractmethod
    async def delete(self, storage_key: str) -> None:
        """Removes the matching file target block from the environment storage location."""
        pass


class LocalStorageProvider(StorageProvider):
    """File backend manager targeting the local machine filesystem during development testing."""
    
    def __init__(self, base_directory: str = "storage_bucket"):
        self.base_dir = Path(base_directory)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    async def upload(self, storage_key: str, content: bytes) -> str:
        destination = self.base_dir / storage_key
        destination.parent.mkdir(parents=True, exist_ok=True)
        
        # Write binary file chunks cleanly to disk execution spots
        with open(destination, "wb") as file_buffer:
            file_buffer.write(content)
            
        return str(destination.resolve())

    async def delete(self, storage_key: str) -> None:
        target_path = self.base_dir / storage_key
        if target_path.exists():
            os.remove(target_path)