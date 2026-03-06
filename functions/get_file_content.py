import os

from google.genai import types

from config import MAX_CHARS

def get_file_content(working_directory, file_path):
    try:
        # Ensure the target file is within the working directory
        abs_working_dir = os.path.abspath(working_directory)
        target_file = os.path.normpath(os.path.join(abs_working_dir, file_path))

        # Check if the target file is a subpath of the working directory
        valid_target_file = os.path.commonpath([abs_working_dir, target_file]) == abs_working_dir

        # Validate the target file
        if not valid_target_file:
            return f'Error: Cannot access "{file_path}" as it is outside the permitted working directory'

        # Check if the target file exists and is a file
        if not os.path.isfile(target_file):
            return f'Error: File not found or is not a regular file: "{file_path}"'
        
        # Read the content of the file, limiting to MAX_CHARS characters
        with open(target_file, 'r') as f:
            content = f.read(MAX_CHARS)

            # After reading the first MAX_CHARS...
            if f.read(1):
                content += f'[...File "{file_path}" truncated at {MAX_CHARS} characters]'
        
        return content
    
    # Handle any exceptions that may occur and return an error message
    except Exception as e:
        return f'Error: {str(e)}'
    

# Define the function schema for get_file_content to be used with the Gemini API
schema_get_file_content = types.FunctionDeclaration(
    name="get_file_content",
    description=f"Reads the content of a specified file relative to the working directory, with a maximum character limit of {MAX_CHARS} characters to prevent excessive output",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="File path to read content from, relative to the working directory",
            ),
        },
        required=["file_path"],
    ),
)   