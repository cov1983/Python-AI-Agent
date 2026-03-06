import os
import subprocess

from google.genai import types

def run_python_file(working_directory, file_path, args=None):

    try:
        # Ensure the target file path is within the working directory
        abs_working_dir = os.path.abspath(working_directory)
        target_file_path = os.path.normpath(os.path.join(abs_working_dir, file_path))

        # Check if the target file path is a subpath of the working directory
        valid_target_file_path = os.path.commonpath([abs_working_dir, target_file_path]) == abs_working_dir

        # Validate the target file path
        if not valid_target_file_path:
            return f'Error: Cannot execute "{file_path}" as it is outside the permitted working directory'
        
        # Check if the target file path exists and is a file
        if not os.path.isfile(target_file_path):
            return f'Error: "{file_path}" does not exist or is not a regular file'
        
        # Check if the target file path is a Python file
        if not target_file_path.endswith('.py'):
            return f'Error: "{file_path}" is not a Python file'

        # Construct the command to run the Python file with optional arguments
        command = ["python", target_file_path]
        if args:
            command.extend(args)

        # Run the command and capture the output
        result = subprocess.run(
            command,
            capture_output=True,
            text=True,
            cwd=abs_working_dir,
            timeout=30,
        )
        
        output = []
        
        # Check the return code and output to determine the result of the execution
        if result.returncode != 0:
            output.append(f"Process exited with code {result.returncode}")
        if not result.stdout and not result.stderr:
            output.append("No output produced")
        if result.stdout:
            output.append(f"STDOUT:\n{result.stdout}")
        if result.stderr:
            output.append(f"STDERR:\n{result.stderr}")
        return "\n".join(output)

    except subprocess.TimeoutExpired:
        return f'Error: "{file_path}" execution timed out after 30 seconds'
    
    except Exception as e:
        return f'Error: {str(e)}'


# Define the function schema for run_python_file to be used with the Gemini API
schema_run_python_file = types.FunctionDeclaration(
    name="run_python_file",
    description="Executes a specified Python file within the working directory and returns its output",
    parameters=types.Schema(
        type=types.Type.OBJECT,
        properties={
            "file_path": types.Schema(
                type=types.Type.STRING,
                description="The path to the Python file to execute, relative to the working directory",
            ),
            "args": types.Schema(
                type=types.Type.ARRAY,
                items=types.Schema(type=types.Type.STRING),
                description="Optional arguments to pass to the Python file",
            ),
        },
        required=["file_path"],
    ),
)