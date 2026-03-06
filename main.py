"""
A simple command-line interface to interact with the Gemini API and execute functions based on model responses.
This is my original implementation of the code before refactoring. 
It contains a single main function that handles all aspects of the interaction with the Gemini API, including generating content, handling function calls, and managing the conversation loop.
While this implementation works, it can be difficult to read and maintain due to the large size of the main function.
"""

import os
import argparse

from dotenv import load_dotenv
from google import genai
from google.genai import types

from prompts import system_prompt

from config import GEMINI_MODEL, MAX_ITERATIONS

from call_function import available_functions, call_function


def main():
    # Load the API key from the .env file
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")

    # Ensure the API key is set
    if not api_key:
        raise RuntimeError("GEMINI_API_KEY is not set in the environment variables")

    # Initialize the Gemini API client
    client = genai.Client(api_key=api_key)

    # Set up argument parsing for the user prompt and verbose flag
    parser = argparse.ArgumentParser(description="A simple command-line interface to interact with the Gemini API and execute functions based on model responses.")
    parser.add_argument("user_prompt", type=str, help="The prompt to send to the Gemini API")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose output")
    args = parser.parse_args()

    # Create the message content for the Gemini API request
    messages = [types.Content(role="user", parts=[types.Part(text=args.user_prompt)])]

    # Agent loop to continuously generate content based on the user prompt and handle function calls made by the model. 
    # In a real application, you would likely want to add some exit condition to this loop.
    for _ in range(MAX_ITERATIONS):  
        response, function_results = generate_content(client, GEMINI_MODEL, args, messages)

        # Check if the response contains any candidates (generated content) and add them to the messages for the next iteration. 
        # If there are no candidates, we assume the conversation has ended and break the loop.
        if response.candidates:
            for candidate in response.candidates:
                messages.append(candidate.content)
        else:
            print("No candidates in response, ending loop.")
            break

        # If there are function results from the previous iteration, add them to the messages for the next iteration. 
        # This allows the model to see the results of its function calls and potentially make further decisions based on those results.
        if function_results:
            messages.extend(function_results)

        # Check if the model made any function calls in its response. 
        # If not, we assume there are no further actions for the model to take and break the loop.
        if not response.function_calls:
            print("No more function calls, ending loop.")
            break

        # If maximum number of iterations is reached and the model still has not ended the conversation, print a message and exit the program with a non-zero status code.
        if _ == MAX_ITERATIONS - 1:
            print("Maximum iterations reached, ending loop.")
            exit(1)

    


def generate_content(client, model, args, messages):

     # Generate content using the Gemini API
    response = client.models.generate_content(
        model=model,
        contents=messages,
        config=types.GenerateContentConfig(
            # Enable function calling to allow the model to call defined functions
            tools=[available_functions],
            # Use the system prompt defined in prompts.py to instruct the model
            system_instruction=system_prompt,
            # Set temperature to 0 for deterministic output
            temperature=0,
            
            ),
    )

    # Validate the response and print the results
    if not response.usage_metadata:
        raise RuntimeError("Gemini API response appears to be malformed: missing usage_metadata")
    

    # Check if the model made any function calls in its response. If not, print the response text and return.
    if not response.function_calls:
        print("No more function calls, final response:")
        print(response.text)
        return response, []

    # If the model did make function calls, we need to handle those calls and execute the corresponding functions. 
    # We will iterate through each function call in the response, execute it using the call_function helper, and store the results.
    function_results = []

    for function_call in response.function_calls:
        function_call_response = call_function(function_call, verbose=args.verbose)
        if not function_call_response.parts:
            raise RuntimeError("Function call response appears to be malformed: missing parts")
        if function_call_response.parts[0].function_response is None:
            raise RuntimeError("Function call response appears to be malformed: missing function_response")
        if function_call_response.parts[0].function_response.response is None:
            raise RuntimeError("Function call response appears to be malformed: missing function_response.response")
        function_results.append(function_call_response)

    # If verbose mode is enabled, print detailed information about the request and response
    if args.verbose:
        print(f"User prompt: {args.user_prompt}")
        print(f"Prompt tokens: {response.usage_metadata.prompt_token_count}")
        print(f"Response tokens: {response.usage_metadata.candidates_token_count}")
        print(f"Response: \n{function_results}")
    

    return response, function_results
        

if __name__ == "__main__":
    main()
