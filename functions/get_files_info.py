import os

from google.genai import types


def get_files_info(working_directory, directory="."):

    try:
        # Ensure the target directory is within the working directory
        abs_working_dir = os.path.abspath(working_directory)
        target_dir = os.path.normpath(os.path.join(abs_working_dir, directory))

        # Check if the target directory is a subdirectory of the working directory
        valid_target_dir = os.path.commonpath([abs_working_dir, target_dir]) == abs_working_dir

        # Validate the target directory
        if not valid_target_dir:
            return f'Error: Cannot list "{directory}" as it is outside the permitted working directory'

        # Check if the target directory exists and is a directory
        if not os.path.isdir(target_dir):
            return f'Error: "{directory}" is not a directory'
        
        files_info = []
        
        # List all entries in the target directory and gather their information
        for entry in os.listdir(target_dir):
            entry_path = os.path.join(target_dir, entry)
            file_info = {
                "name": entry,
                "size": os.path.getsize(entry_path),
                "is_dir": os.path.isdir(entry_path)
            }
            files_info.append(file_info)

        return_string = ""

        # Format the file information into a readable string
        for file_info in files_info:
            return_string += f"- {file_info['name']}: file_size={file_info['size']} bytes, is_dir={file_info['is_dir']}\n"

        return return_string
    
    # Handle any exceptions that may occur and return an error message
    except Exception as e:
        return f'Error: {str(e)}'


# Define the function schema for get_files_info to be used with the Gemini API
schema_get_files_info = types.FunctionDeclaration(
    name="get_files_info",
    description="Lists files in a specified directory relative to the working directory, providing file size and directory status",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "directory": types.Schema(
                type=types.Type.STRING,
                description="Directory path to list files from, relative to the working directory (default is the working directory itself)",
            ),
        },
    ),
)