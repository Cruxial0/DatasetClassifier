import json
from pathlib import Path
from sqlite3 import Connection, Cursor

from src.project import Project
from src.database.database import DB_VERSION, Database
from src.utils import get_image_files

def get_base_directory(data: list[tuple[int, str, str, str, list[str], str]]) -> str:
    return Path(data[0][1]).parent.absolute().as_posix()

def to_posix(path: str) -> str:
    return Path(path).absolute().as_posix()

def create_project(db: Database, project_name: str, directories: list[str]) -> int:
    """
    Creates a new project in the database

    Returns:
        int: The project ID
    """

    return db.insert_project(project_name, directories)

def get_remaining_files(directory_path, exclude_files):
    """
    Returns a list of image file paths in the given directory, excluding specified files.
    All paths are converted to POSIX format for consistent comparison.
    
    Args:
        directory_path (str): Path to the directory to scan
        exclude_files (list): List of full file paths to exclude
    
    Returns:
        list: List of image file paths in POSIX format, excluding the specified files
    """
    from pathlib import Path
    
    # Define common image file extensions
    IMAGE_EXTENSIONS = {
        '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'
    }
    
    # Convert directory path to Path object and then to POSIX format
    dir_path = Path(directory_path).resolve()
    
    # Convert exclude_files to set of resolved POSIX paths for consistent comparison
    exclude_set = {Path(f).resolve().as_posix() for f in exclude_files}
    
    # Get all files and filter for images, excluding the specified files
    filtered_files = [
        file_path.as_posix()
        for file_path in dir_path.glob('*')
        if (file_path.is_file() and 
            file_path.suffix.lower() in IMAGE_EXTENSIONS and 
            file_path.resolve().as_posix() not in exclude_set)
    ]
    
    return filtered_files

# Example usage:
# directory = "/path/to/directory"
# files_to_exclude = ["vacation.jpg", "profile.png"]
# result = get_filtered_image_files(directory, files_to_exclude)

def migrate(db: Database, project_name: str, data: list[tuple[int, str, str, str, list[str], str]]) -> Project:
    base_directory = get_base_directory(data)
    project_id = create_project(db, project_name, [base_directory])
    
    # Get the maximum existing image_id to use as offset
    cursor = db.connection.cursor()
    cursor.execute("SELECT COALESCE(MAX(image_id), -1) FROM images")
    max_id = cursor.fetchone()[0]
    id_offset = max_id + 1
    
    # Prepare data for batch insertion with offset ids
    images_data = [
        (d[0] + id_offset, to_posix(d[1]), d[5], project_id) 
        for d in data
    ]
    scores_data = [
        (d[0] + id_offset, project_id, d[3], json.dumps(d[4]), d[5]) 
        for d in data
    ]
    
    cursor.executemany(
        "INSERT INTO images (image_id, source_path, timestamp, project_id) VALUES (?, ?, ?, ?)", 
        images_data
    )
    cursor.executemany(
        "INSERT INTO scores (image_id, project_id, score, categories, timestamp) VALUES (?, ?, ?, ?, ?)", 
        scores_data
    )

    #Since the old database only tracks scored images, we need to find and add unscored images manually using I/O
    scored_paths = [d[1] for d in data]
    print(f"base directory: {base_directory}")
    print(f"scored paths: {len(scored_paths)}")
    print(f"expected count: {len(get_image_files(base_directory)) - len(scored_paths)}")
    remaining_images = get_remaining_files(base_directory, scored_paths)
    if remaining_images:
        print("actual count: ", len(remaining_images))
        cursor.executemany(
            "INSERT INTO images (source_path, project_id) VALUES (?, ?)", 
            [(image, project_id) for image in remaining_images]
            )
    
    db.connection.commit()
    return Project(project_id, project_name, [base_directory], db)