from google.genai import types

from config import WORKING_DIR
from functions.get_files_info import get_files_info, schema_get_files_info
from functions.get_file_content import get_file_content, schema_get_file_content
from functions.run_python_file import run_python_file, schema_run_python_file
from functions.write_file import write_file, schema_write_file


# Define the available functions as a Tool for the Gemini API
available_functions = types.Tool(
    function_declarations=[
        schema_get_files_info,
        schema_get_file_content,
        schema_run_python_file,
        schema_write_file,
    ]
)

# Map the function name to the actual function implementation
function_map = {
        "get_files_info": get_files_info,
        "get_file_content": get_file_content,
        "run_python_file": run_python_file,
        "write_file": write_file,
}


# This function will be called by the Gemini API when the model decides to call a function
def call_function(function_call, verbose=False):
    # Print the function call details if verbose mode is enabled
    if verbose:
        print(f"Calling function: {function_call.name}({function_call.args})")
    else:
        print(f" - Calling function: {function_call.name}")

    # Extract the function name from the function call, defaulting to an empty string if not provided
    function_name = function_call.name or ""

    # Check if the function name is in the function map, and if not, return an error response
    if function_name not in function_map:
        return types.Content(
            role="tool",
            parts=[
                types.Part.from_function_response(
                    name=function_name,
                    response={"error": f"Unkown function: {function_name}"},
                )
            ],
        )
    
    # Extract the arguments for the function call, defaulting to an empty dictionary if no arguments are provided
    args = dict(function_call.args) if function_call.args else {}

    # For this example, we assume all functions operate within a specific working directory. We add this to the arguments before calling the function.
    args["working_directory"] = WORKING_DIR

    # Call the function with the provided arguments and store the result
    function_result = function_map[function_name](**args)

    # Return the function result in a format that the Gemini API expects, using the function name and the result of the function call
    return types.Content(
        role="tool",
        parts=[
            types.Part.from_function_response(
                name=function_name,
                response={"result": function_result},
            )
        ],
    )