import os
from typing import List

from abc import ABC, abstractmethod

class FUnit(ABC):
    def __init__(self, path: str):
        if not isinstance(path, str):
            raise ValueError("path must be a string")

        self.path = path
        self.name = os.path.basename(path)
        self.size = os.path.getsize(path)
        self.normalized_path = os.path.normpath(path)

    @staticmethod
    def from_path(self, path: str):
        if os.path.isfile(path):
            return FileUnit(path)
        elif os.path.isdir(path):
            return FolderUnit(path)
        else:
            raise ValueError("path must be a file or a directory")

    # @abstractmethod
    def get_path(self) -> str:
        return self.normalized_path

    # @abstractmethod
    def get_name(self) -> str:
        return self.name

    # @abstractmethod
    def get_size(self) -> int:
        return self.size

    @abstractmethod
    def __str__(self):
        pass

    @abstractmethod
    def __repr__(self):
        pass

    

class FileUnit(FUnit):
    def __init__(self, path: str):
        super().__init__(path)  
        self.type = self.get_type(path)
    
    @staticmethod
    def get_type(path: str) -> str:
        """파일의 확장자를 반환합니다.

        Returns:
            str: 파일의 확장자. 확장자가 없는 경우 빈 문자열 반환
        """
        _, ext = os.path.splitext(path)
        return ext[1:] if ext else ""

    
    def __str__(self):
        return f"{self.name}.({self.type})"
    
    def __repr__(self):
        return f"FileUnit({self.name})"


class FolderUnit(FUnit):
    def __init__(self, path: str):
        super().__init__(path)
        self.units: List[FUnit] = []
        for entry in os.scandir(path):
            if entry.is_file():
                self.units.append(FileUnit(entry.path))
            elif entry.is_dir():
                self.units.append(FolderUnit(entry.path))
        
    def __str__(self):
        return f"{self.name} dir"
    
    def __repr__(self):
        return f"FolderUnit({self.name})"


if __name__ == "__main__":
    import time

    start = time.time()
    folder_unit = FolderUnit(r"j:/dev")
    end = time.time()
    print(f"time: {end-start}")
    print(folder_unit.units)

