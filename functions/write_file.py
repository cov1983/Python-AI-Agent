import os

from google.genai import types

def write_file(working_directory, file_path, content):
    
    try:
        # Ensure the target file path is within the working directory
        abs_working_dir = os.path.abspath(working_directory)
        target_file_path = os.path.normpath(os.path.join(abs_working_dir, file_path))

        # Check if the target file path is a subpath of the working directory
        valid_target_file_path = os.path.commonpath([abs_working_dir, target_file_path]) == abs_working_dir

        # Validate the target file path
        if not valid_target_file_path:
            return f'Error: Cannot write to "{file_path}" as it is outside the permitted working directory'
        
        # Check if the target file path exists and is a directory
        if os.path.isdir(target_file_path):
            return f'Error: Cannot write to "{file_path}" as it is a directory'

        # Create any necessary directories for the target file path
        os.makedirs(os.path.dirname(target_file_path), exist_ok=True)

        # Write the content to the target file
        with open(target_file_path, 'w') as file:
            file.write(content)

        return f'Successfully wrote to "{file_path}" ({len(content)} characters written)'
    
    except Exception as e:
        return f'Error: {str(e)}'
    

# Define the function schema for write_file to be used with the Gemini API
schema_write_file = types.FunctionDeclaration(
    name="write_file",
    description="Writes text content to a specified file within the working directory (overwriting if the file exists)",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="File path to write content to, relative to the working directory",
            ),
            "content": types.Schema(
                type=types.Type.STRING,
                description="Content to write to the file",
            ),
        },
        required=["file_path", "content"],
    ),
)   